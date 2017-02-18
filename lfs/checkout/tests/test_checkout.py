from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core import mail
from django.test import TestCase

from lfs.catalog.models import Product
from lfs.cart.models import Cart
from lfs.cart.models import CartItem
from lfs.core.models import Country
from lfs.core.utils import get_default_shop
from lfs.customer.models import Customer
from lfs.addresses.models import Address
from lfs.order.models import Order
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import BY_INVOICE
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax

from postal.library import form_factory


class CheckoutTestCase(TestCase):
    """
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        gb = Country.objects.get(code="gb")
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
            line1="Street 42",
            city="2342",
            state="Gotham City",
            country=gb,
        )

        address2 = Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 43",
            city="2443",
            state="Smallville",
            country=fr,
        )

        self.username = 'joe'
        self.password = 'bloggs'

        new_user = User(username=self.username)
        new_user.set_password(self.password)
        new_user.save()
        self.user = new_user

        self.customer = Customer.objects.create(
            user=new_user,
            selected_shipping_method=shipping_method,
            selected_payment_method=self.by_invoice,
            selected_shipping_address=address1,
            selected_invoice_address=address2,
            default_shipping_address=address1,
            default_invoice_address=address2,
        )

        self.PRODUCT1_NAME = "Surfboard"
        p1 = Product.objects.create(
            name=self.PRODUCT1_NAME,
            slug="product-1",
            sku="sku-1",
            price=1.1,
            tax=tax,
            stock_amount=100,
            active=True,
        )

        p2 = Product.objects.create(
            name="Product 2",
            slug="product-2",
            sku="sku-2",
            price=2.2,
            tax=tax,
            stock_amount=50,
            active=True,
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

    def test_login(self):
        """Tests the login view.
        """
        from lfs.checkout.views import login
        from lfs.checkout.settings import CHECKOUT_TYPE_ANON

        from lfs.tests.utils import create_request
        request = create_request()

        # Anonymous
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()

        result = login(request)
        self.assertEqual(result.status_code, 200)

        # Set checkout_type
        shop = get_default_shop()
        shop.checkout_type = CHECKOUT_TYPE_ANON
        shop.save()

        # Fake a new reuqest
        request.shop = shop

        result = login(request)
        self.assertEqual(result.status_code, 302)

        # Authenticated
        request.user = self.user
        result = login(request)

        self.assertEqual(result.status_code, 302)

    def test_register(self):
        """Tests the login view.
        """
        email = 'testverylongemailaddressthatislongerthanusername1@example.com'
        self.client.post(reverse('lfs_checkout_login'), {'email': email,
                                                         'action': 'register',
                                                         'password_1': 'test',
                                                         'password_2': 'test'})
        self.assertEqual(User.objects.filter(email=email).count(), 1)
        self.client.logout()

        email2 = 'testverylongemailaddressthatislongerthanusername2@example.com'
        self.client.post(reverse('lfs_checkout_login'), {'email': email2,
                                                         'action': 'register',
                                                         'password_1': 'test',
                                                         'password_2': 'test'})
        self.assertEqual(User.objects.filter(email=email2).count(), 1)

    def dump_response(self, http_response):
        fo = open('tests_checkout.html', 'w')
        fo.write(str(http_response))
        fo.close()

    def test_checkout_page(self):
        """Tests that checkout page gets populated with correct details
        """
        # login as our customer
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        cart_response = self.client.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)

        checkout_response = self.client.get(reverse('lfs_checkout'))
        self.assertContains(checkout_response, 'Smallville', status_code=200)

    def test_checkout_country_after_cart_country_change(self):
        """Tests that checkout page gets populated with correct details
        """
        # login as our customer
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        cart_response = self.client.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)
        user = User.objects.get(username=self.username)
        customer = Customer.objects.get(user=user)
        Country.objects.get(code="fr")
        self.assertEquals(customer.selected_invoice_address.country.code, "fr")

        # change the country in the cart
        de = Country.objects.get(code="de")
        cart_response = self.client.post(reverse('lfs_refresh_cart'), {'country': de.code.lower(), "amount-cart-item_%s" % self.item1.id: 1, "amount-cart-item_%s" % self.item2.id: 1})

        customer = Customer.objects.get(user=user)
        self.assertEquals(customer.selected_shipping_address.country.code.lower(), "de")
        self.assertEquals(customer.selected_invoice_address.country.code.lower(), "de")

        cart_response = self.client.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)

        checkout_response = self.client.get(reverse('lfs_checkout'))
        self.assertContains(checkout_response, '<option value="DE" selected="selected">Deutschland</option>', status_code=200)

    def test_order_phone_email_set_after_checkout(self):
        # login as our customer
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        # check initial database quantities
        self.assertEquals(Address.objects.count(), 2)
        self.assertEquals(Customer.objects.count(), 1)
        self.assertEquals(Order.objects.count(), 0)

        # check we have no invoice or shipping phone or email prior to checkout
        our_customer = Customer.objects.all()[0]
        self.assertEqual(our_customer.selected_invoice_address.phone, None)
        self.assertEqual(our_customer.selected_invoice_address.email, None)
        self.assertEqual(our_customer.selected_shipping_address.phone, None)
        self.assertEqual(our_customer.selected_shipping_address.email, None)

        checkout_data = {'invoice-firstname': 'bob',
                         'invoice-lastname': 'builder',
                         'invoice-line1': 'de company',
                         'invoice-line2': 'de street',
                         'invoice-city': 'de area',
                         'invoice-state': 'de town',
                         'invoice-code': 'cork',
                         'invoice-country': "IE",
                         'invoice-email': 'a@a.com',
                         'invoice-phone': '1234567',
                         'shipping-firstname': 'hans',
                         'shipping-lastname': 'schmidt',
                         'shipping-line1': 'orianenberger strasse',
                         'shipping-line2': 'de town',
                         'shipping-city': 'stuff',
                         'shipping-state': 'BE',
                         'shipping-code': '12345',
                         'shipping-country': "DE",
                         'shipping-email': 'b@b.com',
                         'shipping-phone': '7654321',
                         'payment_method': self.by_invoice.id,
                         }

        checkout_post_response = self.client.post(reverse('lfs_checkout'), checkout_data)
        self.assertRedirects(checkout_post_response, reverse('lfs_thank_you'), status_code=302, target_status_code=200,)

        # check that an order email got sent
        self.assertEqual(getattr(settings, 'LFS_SEND_ORDER_MAIL_ON_CHECKOUT', True), True)
        self.assertEqual(getattr(settings, 'LFS_SEND_ORDER_MAIL_ON_PAYMENT', False), False)
        self.assertEqual(len(mail.outbox), 1)

        # check database quantities post-checkout
        self.assertEquals(Address.objects.count(), 4)
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
        logged_in = self.client.login(username=self.username, password=self.password)
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
        self.assertEqual(our_customer.selected_invoice_address.phone, None)
        self.assertEqual(our_customer.selected_invoice_address.email, None)
        self.assertEqual(our_customer.selected_shipping_address.phone, None)
        self.assertEqual(our_customer.selected_shipping_address.email, None)

        checkout_data = {'invoice-firstname': 'bob',
                         'invoice-lastname': 'builder',
                         'invoice-line1': 'de company',
                         'invoice-line2': 'de street',
                         'invoice-city': 'de area',
                         'invoice-state': 'de town',
                         'invoice-code': '1234AB',
                         'invoice-country': "NL",
                         'invoice-email': 'a@a.com',
                         'invoice-phone': '1234567',
                         'shipping-firstname': 'hans',
                         'shipping-lastname': 'schmidt',
                         'shipping-line1': 'orianenberger strasse',
                         'shipping-line2': 'de town',
                         'shipping-city': 'stuff',
                         'shipping-state': 'BE',
                         'shipping-code': '1234AB',
                         'shipping-country': "NL",
                         'shipping-email': 'b@b.com',
                         'shipping-phone': '7654321',
                         'payment_method': self.by_invoice.id,
                         }

        checkout_post_response = self.client.post(reverse('lfs_checkout'), checkout_data)
        self.assertRedirects(checkout_post_response, reverse('lfs_thank_you'), status_code=302, target_status_code=200,)

        # check database quantities post-checkout
        self.assertEquals(Address.objects.count(), 4)
        self.assertEquals(Customer.objects.count(), 1)
        self.assertEquals(Order.objects.count(), 1)

        # check our customer details post checkout
        our_customer = Customer.objects.all()[0]
        self.assertEqual(our_customer.selected_invoice_address.phone, "1234567")
        self.assertEqual(our_customer.selected_invoice_address.email, "a@a.com")
        self.assertEqual(our_customer.selected_shipping_address.phone, '7654321')
        self.assertEqual(our_customer.selected_shipping_address.email, "b@b.com")
