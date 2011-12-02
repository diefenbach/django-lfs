# django imports
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.file import SessionStore
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core import mail

# test imports
from lfs.catalog.models import Product
from lfs.cart.models import Cart
from lfs.cart.models import CartItem
from lfs.cart.views import add_to_cart
from lfs.cart import utils as cart_utils
from lfs.core.models import Shop, Country
from lfs.core.utils import get_default_shop
from lfs.customer.models import Customer, Address
from lfs.order.models import Order
from lfs.order.settings import SUBMITTED
from lfs.order.utils import add_order
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import BY_INVOICE
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax

# 3rd party imports
from postal.library import form_factory


class CheckoutTestCase(TestCase):
    """
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        ie = Country.objects.get(code="ie")
        gb = Country.objects.get(code="gb")
        de = Country.objects.get(code="de")
        us = Country.objects.get(code="us")
        fr = Country.objects.get(code="fr")
        nl = Country.objects.get(code="nl")

        shop = get_default_shop()

        for ic in Country.objects.all():
            shop.invoice_countries.add(ic)

        shop.shipping_countries.add(nl)
        shop.save()

        tax = Tax.objects.create(rate=19)

        shipping_method = ShippingMethod.objects.create(
            name="Standard",
            active=True,
            price=1.0,
            tax=tax
        )

        self.by_invoice = PaymentMethod.objects.get(pk=BY_INVOICE)

        address1 = Address.objects.create(
            firstname="John",
            lastname="Doe",
            company_name="Doe Ltd.",
            street="Street 42",
            city="2342",
            state="Gotham City",
            country=gb,
        )

        address2 = Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            company_name="Doe Ltd.",
            street="Street 43",
            city="2443",
            state="Smallville",
            country=fr,
        )

        self.username = 'joe'
        self.password = 'bloggs'

        new_user = User(username=self.username)
        new_user.set_password(self.password)
        new_user.save()

        self.customer = Customer.objects.create(
            user=new_user,
            selected_shipping_method=shipping_method,
            selected_payment_method=self.by_invoice,
            selected_shipping_address=address1,
            selected_invoice_address=address2,
        )

        self.PRODUCT1_NAME = "Surfboard"
        p1 = Product.objects.create(
            name=self.PRODUCT1_NAME,
            slug="product-1",
            sku="sku-1",
            price=1.1,
            tax=tax,
            stock_amount=100,
        )

        p2 = Product.objects.create(
            name="Product 2",
            slug="product-2",
            sku="sku-2",
            price=2.2,
            tax=tax,
            stock_amount=50,
        )

        cart = Cart.objects.create(
            user=new_user
        )

        self.item1 = CartItem.objects.create(
            cart=cart,
            product=p1,
            amount=2,
        )

        self.item2 = CartItem.objects.create(
            cart=cart,
            product=p2,
            amount=3,
        )

        self.c = Client()

    def dump_response(self, http_response):
        fo = open('tests_checkout.html', 'w')
        fo.write(str(http_response))
        fo.close()

    def test_checkout_page(self):
        """Tests that checkout page gets populated with correct details
        """
        # login as our customer
        logged_in = self.c.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        cart_response = self.c.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)

        checkout_response = self.c.get(reverse('lfs_checkout'))
        self.assertContains(checkout_response, 'Smallville', status_code=200)

    def test_checkout_country_after_cart_country_change(self):
        """Tests that checkout page gets populated with correct details
        """
        # login as our customer
        logged_in = self.c.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        cart_response = self.c.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)
        user = User.objects.get(username=self.username)
        customer = Customer.objects.get(user=user)
        fr = Country.objects.get(code="fr")
        self.assertEquals(customer.selected_invoice_address.country.code, "fr")

        # change the country in the cart
        de = Country.objects.get(code="de")
        cart_response = self.c.post('/refresh-cart', {'country': de.code.lower(), "amount-cart-item_%s" % self.item1.id: 1, "amount-cart-item_%s" % self.item2.id: 1})

        customer = Customer.objects.get(user=user)
        self.assertEquals(customer.selected_shipping_address.country.code.lower(), "de")
        self.assertEquals(customer.selected_invoice_address.country.code.lower(), "de")

        cart_response = self.c.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)

        checkout_response = self.c.get(reverse('lfs_checkout'))
        self.assertContains(checkout_response, '<option value="DE" selected="selected">Deutschland</option>', status_code=200)

    def test_order_phone_email_set_after_checkout(self):
        # login as our customer
        logged_in = self.c.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        # check initial database quantities
        self.assertEquals(Address.objects.count(), 2)
        self.assertEquals(Customer.objects.count(), 1)
        self.assertEquals(Order.objects.count(), 0)

        # check we have no invoice or shipping phone or email prior to checkout
        our_customer = Customer.objects.all()[0]
        self.assertEqual(our_customer.selected_invoice_address.phone, '')
        self.assertEqual(our_customer.selected_invoice_address.email, None)
        self.assertEqual(our_customer.selected_shipping_address.phone, '')
        self.assertEqual(our_customer.selected_shipping_address.email, None)

        checkout_data = {'invoice_firstname': 'bob',
                         'invoice_lastname': 'builder',
                         'invoice-line1': 'de company',
                         'invoice-line2': 'de street',
                         'invoice-city': 'de area',
                         'invoice-state': 'de town',
                         'invoice-code': 'cork',
                         'invoice-country': "IE",
                         'invoice_email': 'a@a.com',
                         'invoice_phone': '1234567',
                         'shipping_firstname': 'hans',
                         'shipping_lastname': 'schmidt',
                         'shipping-line1': 'orianenberger strasse',
                         'shipping-line2': 'de town',
                         'shipping-city': 'stuff',
                         'shipping-state': 'BE',
                         'shipping-code': '12345',
                         'shipping-country': "DE",
                         'payment_method': self.by_invoice.id,
                         'shipping_email': 'b@b.com',
                         'shipping_phone': '7654321',
                         }

        checkout_post_response = self.c.post(reverse('lfs_checkout'), checkout_data)
        self.assertRedirects(checkout_post_response, reverse('lfs_thank_you'), status_code=302, target_status_code=200,)

        # check that an order email got sent
        self.assertEqual(getattr(settings, 'LFS_SEND_ORDER_MAIL_ON_CHECKOUT', True), True)
        self.assertEqual(getattr(settings, 'LFS_SEND_ORDER_MAIL_ON_PAYMENT', False), False)
        self.assertEqual(len(mail.outbox), 1)

        # check database quantities post-checkout
        self.assertEquals(Address.objects.count(), 2)
        self.assertEquals(Customer.objects.count(), 1)
        self.assertEquals(Order.objects.count(), 1)

        # check our customer details post checkout
        our_customer = Customer.objects.all()[0]
        self.assertEqual(our_customer.selected_invoice_address.phone, "1234567")
        self.assertEqual(our_customer.selected_invoice_address.email, "a@a.com")
        self.assertEqual(our_customer.selected_shipping_address.phone, '7654321')
        self.assertEqual(our_customer.selected_shipping_address.email, "b@b.com")

    def test_checkout_with_4_line_shipping_address(self):
        # login as our customer
        logged_in = self.c.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        # test that our Netherlands form has only 4 address line fields
        nl_form_class = form_factory("NL")
        nl_form = nl_form_class()
        self.assertEqual('state' in nl_form.fields, False)
        self.assertEqual('code' in nl_form.fields, True)

        # check initial database quantities
        self.assertEquals(Address.objects.count(), 2)
        self.assertEquals(Customer.objects.count(), 1)
        self.assertEquals(Order.objects.count(), 0)

        # check we have no invoice or shipping phone or email prior to checkout
        our_customer = Customer.objects.all()[0]
        self.assertEqual(our_customer.selected_invoice_address.phone, '')
        self.assertEqual(our_customer.selected_invoice_address.email, None)
        self.assertEqual(our_customer.selected_shipping_address.phone, '')
        self.assertEqual(our_customer.selected_shipping_address.email, None)

        checkout_data = {'invoice_firstname': 'bob',
                         'invoice_lastname': 'builder',
                         'invoice-line1': 'de company',
                         'invoice-line2': 'de street',
                         'invoice-city': 'de area',
                         'invoice-state': 'de town',
                         'invoice-code': '1234AB',
                         'invoice-country': "NL",
                         'invoice_email': 'a@a.com',
                         'invoice_phone': '1234567',
                         'shipping_firstname': 'hans',
                         'shipping_lastname': 'schmidt',
                         'shipping-line1': 'orianenberger strasse',
                         'shipping-line2': 'de town',
                         'shipping-city': 'stuff',
                         'shipping-state': 'BE',
                         'shipping-code': '1234AB',
                         'shipping-country': "NL",
                         'payment_method': self.by_invoice.id,
                         'shipping_email': 'b@b.com',
                         'shipping_phone': '7654321',
                         }

        checkout_post_response = self.c.post(reverse('lfs_checkout'), checkout_data)
        self.assertRedirects(checkout_post_response, reverse('lfs_thank_you'), status_code=302, target_status_code=200,)

        # check database quantities post-checkout
        self.assertEquals(Address.objects.count(), 2)
        self.assertEquals(Customer.objects.count(), 1)
        self.assertEquals(Order.objects.count(), 1)

        # check our customer details post checkout
        our_customer = Customer.objects.all()[0]
        self.assertEqual(our_customer.selected_invoice_address.phone, "1234567")
        self.assertEqual(our_customer.selected_invoice_address.email, "a@a.com")
        self.assertEqual(our_customer.selected_shipping_address.phone, '7654321')
        self.assertEqual(our_customer.selected_shipping_address.email, "b@b.com")
