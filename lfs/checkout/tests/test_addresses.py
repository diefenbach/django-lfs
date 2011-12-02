# django imports
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.file import SessionStore
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings

# test imports
from lfs.catalog.models import Product
from lfs.cart.models import Cart
from lfs.cart.models import CartItem
from lfs.cart.views import add_to_cart
from lfs.cart import utils as cart_utils
from lfs.core.models import Shop, Country
from lfs.core.utils import get_default_shop
from lfs.customer.models import Customer, Address
from lfs.order.utils import add_order
from lfs.order.settings import SUBMITTED
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import BY_INVOICE, DIRECT_DEBIT
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax


class CheckoutAddressesTestCase(TestCase):
    """Test localization of addresses on OnePageCheckoutForm.
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        ie = Country.objects.get(code="ie")
        gb = Country.objects.get(code="gb")
        de = Country.objects.get(code="de")
        us = Country.objects.get(code="us")

        shop = get_default_shop()
        for ic in Country.objects.all():
            shop.invoice_countries.add(ic)
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
            city="Gotham City",
            zip_code="2342",
            country=ie,
        )

        address2 = Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            company_name="Doe Ltd.",
            street="Street 43",
            city="Smallville",
            zip_code="2443",
            country=us,
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
        )

        p2 = Product.objects.create(
            name="Product 2",
            slug="product-2",
            sku="sku-2",
            price=2.2,
            tax=tax,
        )

        cart = Cart.objects.create(
            user=new_user
        )

        item = CartItem.objects.create(
            cart=cart,
            product=p1,
            amount=2,
        )

        item = CartItem.objects.create(
            cart=cart,
            product=p2,
            amount=3,
        )

        self.c = Client()

    def dump_response(self, http_response):
        fo = open('tests_checkout_addresses.html', 'w')
        fo.write(str(http_response))
        fo.close()

    def test_checkout_page_ie(self):
        """Tests that checkout page gets populated with correct details
        """
        # login as our customer
        logged_in = self.c.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        cart_response = self.c.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)

        checkout_response = self.c.get(reverse('lfs_checkout'))

        # we expect a list of irish counties in the response as we have an Irish shipping address
        self.assertContains(checkout_response, 'Offaly', status_code=200)

        # we expect a list of american states in the response as we have an Irish shipping address
        self.assertContains(checkout_response, 'Washington', status_code=200)

    def test_address_changed_on_checkout(self):
        # login as our customer
        logged_in = self.c.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        self.assertEquals(Address.objects.count(), 2)
        cart_response = self.c.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)

        checkout_response = self.c.get(reverse('lfs_checkout'))
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
                         'shipping_email': 'b@b.com',
                         'shipping_phone': '7654321',
                         'payment_method': self.by_invoice.id,
                         }

        checkout_post_response = self.c.post(reverse('lfs_checkout'), checkout_data)
        #self.dump_response(checkout_post_response)
        self.assertRedirects(checkout_post_response, reverse('lfs_thank_you'), status_code=302, target_status_code=200,)

        # test we have same amount of address objects at end of checkout
        self.assertEquals(Address.objects.count(), 2)

    def test_ajax_saves_address(self):
        self.assertEquals(Address.objects.count(), 2)

        # register a new user
        registration_response = self.c.post(reverse('lfs_login'), {'action': 'register', 'email': 'test@test.com', 'password_1': 'password', 'password_2': 'password'})
        self.assertEquals(registration_response.status_code, 302)
        self.assertEquals(registration_response._headers['location'], ('Location', 'http://testserver/'))

        # get our new customer
        our_customer = Customer.objects.get(user__email="test@test.com")
        self.assertNotEqual(our_customer, None)
        self.assertNotEqual(our_customer.selected_invoice_address, None)
        self.assertNotEqual(our_customer.selected_shipping_address, None)

        # test that an ajax request creates a new customer address
        form_data = {'invoice-country': 'ie'}
        ajax_respons = self.c.post(reverse('lfs_changed_invoice_country'), form_data)
        self.assertEquals(Address.objects.count(), 4)

        # refetch our customer
        our_customer = Customer.objects.get(user__email="test@test.com")
        self.assertNotEqual(our_customer.selected_invoice_address, None)
        self.assertNotEqual(our_customer.selected_shipping_address, None)

        # test that we still have the same number of Addresses after another invoice post
        form_data = {'invoice-line1': 'my house',
                     'invoice-line2': 'a street',
                     'invoice-city': 'a city',
                     'invoice-code': 'a code',
                     'invoice-state': 'a state',
                     }
        ajax_respons = self.c.post(reverse('lfs_changed_invoice_country'), form_data)
        self.assertEquals(Address.objects.count(), 4)

        # post some shipping address info
        form_data = {'shipping-line1': 'de missusesss house'}
        ajax_respons = self.c.post(reverse('lfs_changed_shipping_country'), form_data)
        self.assertEquals(Address.objects.count(), 4)

        # refetch our customer
        our_customer = Customer.objects.get(user__email="test@test.com")
        self.assertNotEqual(our_customer.selected_invoice_address, None)
        self.assertNotEqual(our_customer.selected_shipping_address, None)

        # test that adding more info to shipping address doesn't create a brand new one
        form_data = {'shipping-firstname': 'charlize',
                     'shipping-line2': 'a street',
                     'shipping-city': 'a city',
                     'shipping-code': 'a code',
                     'shipping-state': 'a state', }
        ajax_respons = self.c.post(reverse('lfs_changed_shipping_country'), form_data)
        self.assertEquals(Address.objects.count(), 4)
