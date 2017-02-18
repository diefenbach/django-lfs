from django.contrib.auth.models import User
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from lfs.catalog.models import Product
from lfs.cart.models import Cart
from lfs.cart.models import CartItem
from lfs.core.models import Country
from lfs.core.utils import get_default_shop
from lfs.customer.models import Customer
from lfs.addresses.models import Address
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import BY_INVOICE
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
            line1="Street 42",
            city="Gotham City",
            zip_code="2342",
            country=ie,
        )

        address2 = Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 43",
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
            default_shipping_address=address1,
            default_invoice_address=address2
        )

        self.PRODUCT1_NAME = "Surfboard"
        p1 = Product.objects.create(
            name=self.PRODUCT1_NAME,
            slug="product-1",
            sku="sku-1",
            price=1.1,
            tax=tax,
            active=True,
        )

        p2 = Product.objects.create(
            name="Product 2",
            slug="product-2",
            sku="sku-2",
            price=2.2,
            tax=tax,
            active=True,
        )

        cart = Cart.objects.create(
            user=new_user
        )

        CartItem.objects.create(
            cart=cart,
            product=p1,
            amount=2,
        )

        CartItem.objects.create(
            cart=cart,
            product=p2,
            amount=3,
        )

    def dump_response(self, http_response):
        fo = open('tests_checkout_addresses.html', 'w')
        fo.write(str(http_response))
        fo.close()

    def test_checkout_page_ie(self):
        """Tests that checkout page gets populated with correct details
        """
        # login as our customer
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        cart_response = self.client.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)

        checkout_response = self.client.get(reverse('lfs_checkout'))

        # we expect a list of irish counties in the response as we have an Irish shipping address
        self.assertContains(checkout_response, 'Offaly', status_code=200)

        # we expect a list of american states in the response as we have an Irish shipping address
        self.assertContains(checkout_response, 'Washington', status_code=200)

    def test_address_changed_on_checkout(self):
        # login as our customer
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        self.assertEquals(Address.objects.count(), 2)
        cart_response = self.client.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)

        self.client.get(reverse('lfs_checkout'))
        checkout_data = {'invoice-firstname': 'bob',
                         'invoice-lastname': 'builder',
                         'invoice-line1': 'de company',
                         'invoice-line2': 'de street',
                         'invoice-city': 'de area',
                         'invoice-state': 'de town',
                         'invoice-code': '12345',
                         'invoice-country': "DE",
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
        # self.dump_response(checkout_post_response)
        self.assertRedirects(checkout_post_response, reverse('lfs_thank_you'), status_code=302, target_status_code=200,)

        # test we have same amount of address objects at end of checkout
        self.assertEquals(Address.objects.count(), 4)

    def test_ajax_saves_address(self):
        self.assertEquals(Address.objects.count(), 2)

        # register a new user
        registration_response = self.client.post(reverse('lfs_login'), {'action': 'register', 'email': 'test@test.com', 'password_1': 'password', 'password_2': 'password'})
        self.assertEquals(registration_response.status_code, 302)
        self.assertEquals(registration_response._headers['location'], ('Location', '/'))

        # get our new customer
        our_customer = Customer.objects.get(user__email="test@test.com")
        self.assertNotEqual(our_customer, None)
        # four new addresses should be created for our_customer
        self.assertNotEqual(our_customer.selected_invoice_address, None)
        self.assertNotEqual(our_customer.selected_shipping_address, None)
        self.assertNotEqual(our_customer.default_invoice_address, None)
        self.assertNotEqual(our_customer.default_shipping_address, None)

        self.assertEquals(Address.objects.count(), 6)

        # test that an ajax request creates a new customer address
        form_data = {'invoice-country': 'ie'}
        self.client.post(reverse('lfs_changed_invoice_country'), form_data)
        self.assertEquals(Address.objects.count(), 6)

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
                     'invoice-country': 'ie',
                     }
        self.client.post(reverse('lfs_changed_invoice_country'), form_data)
        self.assertEquals(Address.objects.count(), 6)

        # post some shipping address info
        form_data = {
            'shipping-line1': 'de missusesss house',
            'shipping-country': 'ie',
        }
        self.client.post(reverse('lfs_changed_shipping_country'), form_data)
        self.assertEquals(Address.objects.count(), 6)

        # refetch our customer
        our_customer = Customer.objects.get(user__email="test@test.com")
        self.assertNotEqual(our_customer.selected_invoice_address, None)
        self.assertNotEqual(our_customer.selected_shipping_address, None)

        # test that adding more info to shipping address doesn't create a brand new one
        form_data = {
            'shipping-firstname': 'charlize',
            'shipping-line2': 'a street',
            'shipping-city': 'a city',
            'shipping-code': 'a code',
            'shipping-state': 'a state',
            'shipping-country': 'ie',
        }
        self.client.post(reverse('lfs_changed_shipping_country'), form_data)
        self.assertEquals(Address.objects.count(), 6)


class CheckoutAddressesNoAutoUpdateTestCase(TestCase):
    """Test localization of addresses on OnePageCheckoutForm while
    autoupdate of default addresses is disabled.
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        ie = Country.objects.get(code="ie")
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
            line1="Street 42",
            city="Gotham City",
            zip_code="2342",
            country=ie,
        )

        address2 = Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 43",
            city="Smallville",
            zip_code="2443",
            country=us,
        )

        address3 = Address.objects.create(
            firstname="John",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 42",
            city="Gotham City",
            zip_code="2342",
            country=ie,
        )

        address4 = Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 43",
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
            default_shipping_address=address3,
            default_invoice_address=address4
        )

        self.PRODUCT1_NAME = "Surfboard"
        p1 = Product.objects.create(
            name=self.PRODUCT1_NAME,
            slug="product-1",
            sku="sku-1",
            price=1.1,
            tax=tax,
            active=True,
        )

        p2 = Product.objects.create(
            name="Product 2",
            slug="product-2",
            sku="sku-2",
            price=2.2,
            tax=tax,
            active=True,
        )

        cart = Cart.objects.create(
            user=new_user
        )

        CartItem.objects.create(
            cart=cart,
            product=p1,
            amount=2,
        )

        CartItem.objects.create(
            cart=cart,
            product=p2,
            amount=3,
        )

    def dump_response(self, http_response):
        fo = open('tests_checkout_addresses.html', 'w')
        fo.write(str(http_response))
        fo.close()

    @override_settings(LFS_AUTO_UPDATE_DEFAULT_ADDRESSES=False)
    def test_checkout_page_ie(self):
        """Tests that checkout page gets populated with correct details
        """
        # login as our customer
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        cart_response = self.client.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)

        checkout_response = self.client.get(reverse('lfs_checkout'))

        # we expect a list of irish counties in the response as we have an Irish shipping address
        self.assertContains(checkout_response, 'Offaly', status_code=200)

        # we expect a list of american states in the response as we have an Irish shipping address
        self.assertContains(checkout_response, 'Washington', status_code=200)

    @override_settings(LFS_AUTO_UPDATE_DEFAULT_ADDRESSES=False)
    def test_address_changed_on_checkout(self):
        # login as our customer
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        self.assertEquals(Address.objects.count(), 4)
        cart_response = self.client.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)

        self.client.get(reverse('lfs_checkout'))
        checkout_data = {'invoice-firstname': 'bob',
                         'invoice-lastname': 'builder',
                         'invoice-line1': 'de company',
                         'invoice-line2': 'de street',
                         'invoice-city': 'de area',
                         'invoice-state': 'de town',
                         'invoice-code': '12345',
                         'invoice-country': "DE",
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
        # self.dump_response(checkout_post_response)
        self.assertRedirects(checkout_post_response, reverse('lfs_thank_you'), status_code=302, target_status_code=200,)

        # test we have same amount of address objects at end of checkout
        self.assertEquals(Address.objects.count(), 6)

    @override_settings(LFS_AUTO_UPDATE_DEFAULT_ADDRESSES=False)
    def test_ajax_saves_address(self):
        self.assertEquals(Address.objects.count(), 4)

        # register a new user
        registration_response = self.client.post(reverse('lfs_login'), {'action': 'register', 'email': 'test@test.com', 'password_1': 'password', 'password_2': 'password'})
        self.assertEquals(registration_response.status_code, 302)
        self.assertEquals(registration_response._headers['location'], ('Location', '/'))

        # get our new customer
        our_customer = Customer.objects.get(user__email="test@test.com")
        self.assertNotEqual(our_customer, None)
        # four new addresses should be created for our_customer
        self.assertNotEqual(our_customer.selected_invoice_address, None)
        self.assertNotEqual(our_customer.selected_shipping_address, None)
        self.assertNotEqual(our_customer.default_invoice_address, None)
        self.assertNotEqual(our_customer.default_shipping_address, None)

        self.assertEquals(Address.objects.count(), 8)

        # test that an ajax request creates a new customer address
        form_data = {'invoice-country': 'ie'}
        self.client.post(reverse('lfs_changed_invoice_country'), form_data)
        self.assertEquals(Address.objects.count(), 8)

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
                     'invoice-country': 'ie',
                     }
        self.client.post(reverse('lfs_changed_invoice_country'), form_data)
        self.assertEquals(Address.objects.count(), 8)

        # post some shipping address info
        form_data = {
            'shipping-line1': 'de missusesss house',
            'shipping-country': 'ie',
        }
        self.client.post(reverse('lfs_changed_shipping_country'), form_data)
        self.assertEquals(Address.objects.count(), 8)

        # refetch our customer
        our_customer = Customer.objects.get(user__email="test@test.com")
        self.assertNotEqual(our_customer.selected_invoice_address, None)
        self.assertNotEqual(our_customer.selected_shipping_address, None)

        # test that adding more info to shipping address doesn't create a brand new one
        form_data = {
            'shipping-firstname': 'charlize',
            'shipping-line2': 'a street',
            'shipping-city': 'a city',
            'shipping-code': 'a code',
            'shipping-state': 'a state',
            'shipping-country': 'ie',
        }
        self.client.post(reverse('lfs_changed_shipping_country'), form_data)
        self.assertEquals(Address.objects.count(), 8)
