from django.http import HttpRequest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail

from django.test.utils import override_settings
from lfs.addresses.models import Address
from lfs.addresses.utils import AddressManagement
from lfs.core.models import Country
from lfs.core.models import Shop
from lfs.customer.models import CreditCard
from lfs.customer.models import Customer
from lfs.customer.utils import create_unique_username, create_customer
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax
from lfs.payment.models import PaymentMethod
from django.contrib.sessions.middleware import SessionMiddleware


class CreditCardTestCase(TestCase):
    def setUp(self):
        self.cc = CreditCard(
            type="mastercard",
            owner="John Doe",
            number="4711",
            expiration_date_month=8,
            expiration_date_year=2012
        )

    def test_unicode(self):
        self.assertEquals(self.cc.__unicode__(), "%s / %s" % (self.cc.type, self.cc.owner))


class CustomerTestCase(TestCase):

    fixtures = ['lfs_shop.xml']

    def setUp(self):
        self.username = 'joe'
        self.password = 'bloggs'

        self.user = User(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        ie = Country.objects.get(code="ie")
        gb = Country.objects.get(code="gb")
        de = Country.objects.get(code="de")
        us = Country.objects.get(code="us")
        fr = Country.objects.get(code="fr")

        shop, created = Shop.objects.get_or_create(name="lfs test", shop_owner="John Doe", default_country=de)
        shop.save()
        shop.invoice_countries.add(ie)
        shop.invoice_countries.add(gb)
        shop.invoice_countries.add(de)
        shop.invoice_countries.add(us)
        shop.invoice_countries.add(fr)
        shop.shipping_countries.add(ie)
        shop.shipping_countries.add(gb)
        shop.shipping_countries.add(de)
        shop.shipping_countries.add(us)
        shop.shipping_countries.add(fr)
        shop.save()

        tax = Tax.objects.create(rate=19)

        ShippingMethod.objects.create(
            name="Standard",
            active=True,
            price=1.0,
            tax=tax
        )

        PaymentMethod.objects.create(
            name="Direct Debit",
            active=True,
            tax=tax,
        )

    def test_create_customer(self):
        request = HttpRequest()
        request.user = self.user
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        self.assertEquals(Address.objects.count(), 0)
        create_customer(request)
        self.assertEquals(Address.objects.count(), 4)


class AddressTestCase(TestCase):

    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        ie = Country.objects.get(code="ie")
        gb = Country.objects.get(code="gb")
        de = Country.objects.get(code="de")
        us = Country.objects.get(code="us")
        fr = Country.objects.get(code="fr")

        shop, created = Shop.objects.get_or_create(name="lfs test", shop_owner="John Doe", default_country=de)
        shop.save()
        shop.invoice_countries.add(ie)
        shop.invoice_countries.add(gb)
        shop.invoice_countries.add(de)
        shop.invoice_countries.add(us)
        shop.invoice_countries.add(fr)
        shop.shipping_countries.add(ie)
        shop.shipping_countries.add(gb)
        shop.shipping_countries.add(de)
        shop.shipping_countries.add(us)
        shop.shipping_countries.add(fr)
        shop.save()

        tax = Tax.objects.create(rate=19)

        shipping_method = ShippingMethod.objects.create(
            name="Standard",
            active=True,
            price=1.0,
            tax=tax
        )

        payment_method = PaymentMethod.objects.create(
            name="Direct Debit",
            active=True,
            tax=tax,
        )

        self.address1 = Address.objects.create(
            firstname="John",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 42",
            city="Gotham City",
            zip_code="23422",
            country=de,
            phone="555-111111",
            email="john@doe.com",
        )

        self.address2 = Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 43",
            city="Smallville",
            zip_code="24432",
            country=de,
            phone="666-111111",
            email="jane@doe.com",
        )

        self.address3 = Address.objects.create(
            firstname="John",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 42",
            city="Gotham City",
            zip_code="23422",
            country=de,
            phone="555-111111",
            email="john@doe.com",
        )

        self.address4 = Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 43",
            city="Smallville",
            zip_code="24432",
            country=de,
            phone="666-111111",
            email="jane@doe.com",
        )

        self.username = 'joe'
        self.password = 'bloggs'

        new_user = User(username=self.username)
        new_user.set_password(self.password)
        new_user.save()

        self.customer = Customer.objects.create(
            user=new_user,
            selected_shipping_method=shipping_method,
            selected_payment_method=payment_method,
            selected_shipping_address=self.address1,
            selected_invoice_address=self.address2,
            default_shipping_address=self.address3,
            default_invoice_address=self.address4,
        )

    def test_address_page(self):
        """
        Tests that we can see a shipping and an invoice address
        """
        # login as our customer
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        address_response = self.client.get(reverse('lfs_my_addresses'))
        # self.dump_response(address_response)
        self.assertContains(address_response, 'Smallville', status_code=200)
        self.assertContains(address_response, 'Gotham City', status_code=200)

    def test_register_then_view_address(self):
        """Check we have a customer in database after registration"""
        # we should have one customer starting
        self.assertEqual(len(Customer.objects.all()), 1)

        registration_response = self.client.post(reverse('lfs_login'), {'action': 'register', 'email': 'test@test.com', 'password_1': 'password', 'password_2': 'password'})
        self.assertEquals(registration_response.status_code, 302)
        self.assertEquals(registration_response._headers['location'], ('Location', '/'))

        # Test that one message has been sent.
        self.assertEquals(len(mail.outbox), 1)

        # see if we can view the address page
        address_response = self.client.get(reverse('lfs_my_addresses'))
        self.assertContains(address_response, 'City', status_code=200)

        # we should now have 2 customers
        self.assertEqual(len(Customer.objects.all()), 2)

    def dump_response(self, http_response):
        fo = open('tests_customers.html', 'w')
        fo.write(str(http_response))
        fo.close()

    def test_create_new_address(self):
        # test that we have only 4 addresses registered (from setUp)
        self.assertEquals(Address.objects.count(), 4)

        # register a new user
        registration_response = self.client.post(reverse('lfs_login'), {'action': 'register', 'email': 'test@test.com', 'password_1': 'password', 'password_2': 'password'})
        self.assertEquals(registration_response.status_code, 302)
        self.assertEquals(registration_response._headers['location'], ('Location', '/'))

        self.assertEquals(Address.objects.count(), 8)

        # Test that one message has been sent.
        self.assertEquals(len(mail.outbox), 1)

        our_user = User.objects.get(email='test@test.com')
        our_customer = Customer.objects.get(user=our_user)
        self.assertNotEquals(our_customer.selected_invoice_address, None)
        self.assertNotEquals(our_customer.selected_shipping_address, None)

        # see if we can view the addresss page
        address_data = {
            'invoice-firstname': 'Joe', 'invoice-lastname': 'Bloggs',
            'invoice-line1': 'de company name', 'invoice-line2': 'de street',
            'invoice-city': 'Dallas', 'invoice-state': 'TX',
            'invoice-code': '84003', 'invoice-country': 'US',
            'invoice-phone': '+49 4711 4711', 'invoice-email': 'joe.bloggs@acme.com',
            'shipping-firstname': 'Joe', 'shipping-lastname': 'Bloggs',
            'shipping-line1': 'de company name', 'shipping-line2': 'de street',
            'shipping-city': 'Dallas', 'shipping-state': 'TX',
            'shipping-code': '84003', 'shipping-country': 'US',
            'shipping-phone': '+49 4712 4712', 'invoice-email': 'joe.bloggs@acme.com',
        }

        self.client.post(reverse('lfs_my_addresses'), address_data)

        self.assertEquals(Address.objects.count(), 8)

        # refetch our user from the database
        our_customer = Customer.objects.get(user=our_user)
        self.assertNotEquals(our_customer.selected_invoice_address, None)
        self.assertNotEquals(our_customer.selected_shipping_address, None)
        self.assertEquals(our_customer.selected_invoice_address.firstname, 'Joe')
        self.assertEquals(our_customer.selected_invoice_address.lastname, 'Bloggs')

    def test_change_address_page(self):
        """
        Tests that we can see a shipping and an invoice address
        """
        # login as our customer
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        iam = AddressManagement(self.customer, self.address2, "invoice")
        sam = AddressManagement(self.customer, self.address1, "shipping")

        iam_data = iam.get_address_as_dict()
        sam_data = sam.get_address_as_dict()
        data = {"invoice-firstname": "newname",
                "invoice-lastname": self.address2.lastname,
                "invoice-phone": self.address2.phone,
                "invoice-email": self.address2.email,

                "shipping-firstname": self.address1.firstname,
                "shipping-lastname": self.address1.lastname,
                "shipping-phone": self.address1.phone,
                "shipping-email": self.address1.email,
                }
        for key, value in iam_data.items():
            data['invoice-%s' % key] = value

        for key, value in sam_data.items():
            data['shipping-%s' % key] = value

        data['invoice-country'] = 'AT'

        response = self.client.post(reverse('lfs_my_addresses'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        iam2 = Address.objects.get(pk=self.address2.pk)
        self.assertEqual(iam2.firstname, "newname")
        self.assertEqual(iam2.country.code.upper(), "AT")


class NoAutoUpdateAddressTestCase(TestCase):

    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        ie = Country.objects.get(code="ie")
        gb = Country.objects.get(code="gb")
        de = Country.objects.get(code="de")
        us = Country.objects.get(code="us")
        fr = Country.objects.get(code="fr")

        shop, created = Shop.objects.get_or_create(name="lfs test", shop_owner="John Doe", default_country=de)
        shop.save()
        shop.invoice_countries.add(ie)
        shop.invoice_countries.add(gb)
        shop.invoice_countries.add(de)
        shop.invoice_countries.add(us)
        shop.invoice_countries.add(fr)
        shop.shipping_countries.add(ie)
        shop.shipping_countries.add(gb)
        shop.shipping_countries.add(de)
        shop.shipping_countries.add(us)
        shop.shipping_countries.add(fr)
        shop.save()

        tax = Tax.objects.create(rate=19)

        shipping_method = ShippingMethod.objects.create(
            name="Standard",
            active=True,
            price=1.0,
            tax=tax
        )

        payment_method = PaymentMethod.objects.create(
            name="Direct Debit",
            active=True,
            tax=tax,
        )

        self.address1 = Address.objects.create(
            firstname="John",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 42",
            city="Gotham City",
            zip_code="23422",
            country=de,
            phone="555-111111",
            email="john@doe.com",
        )

        self.address2 = Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 43",
            city="Smallville",
            zip_code="24432",
            country=de,
            phone="666-111111",
            email="jane@doe.com",
        )

        self.address3 = Address.objects.create(
            firstname="John",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 42",
            city="Gotham City",
            zip_code="23422",
            country=de,
            phone="555-111111",
            email="john@doe.com",
        )

        self.address4 = Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 43",
            city="Smallville",
            zip_code="24432",
            country=de,
            phone="666-111111",
            email="jane@doe.com",
        )

        self.username = 'joe'
        self.password = 'bloggs'

        new_user = User(username=self.username)
        new_user.set_password(self.password)
        new_user.save()

        self.customer = Customer.objects.create(
            user=new_user,
            selected_shipping_method=shipping_method,
            selected_payment_method=payment_method,
            selected_shipping_address=self.address1,
            selected_invoice_address=self.address2,
            default_shipping_address=self.address3,
            default_invoice_address=self.address4,
        )

    @override_settings(LFS_AUTO_UPDATE_DEFAULT_ADDRESSES=False)
    def test_address_page(self):
        """
        Tests that we can see a shipping and an invoice address
        """
        # login as our customer
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        address_response = self.client.get(reverse('lfs_my_addresses'))
        # self.dump_response(address_response)
        self.assertContains(address_response, 'Smallville', status_code=200)
        self.assertContains(address_response, 'Gotham City', status_code=200)

    @override_settings(LFS_AUTO_UPDATE_DEFAULT_ADDRESSES=False)
    def test_register_then_view_address(self):
        """Check we have a customer in database after registration"""
        # we should have one customer starting
        self.assertEqual(len(Customer.objects.all()), 1)

        registration_response = self.client.post(reverse('lfs_login'), {'action': 'register', 'email': 'test@test.com', 'password_1': 'password', 'password_2': 'password'})
        self.assertEquals(registration_response.status_code, 302)
        self.assertEquals(registration_response._headers['location'], ('Location', '/'))

        # Test that one message has been sent.
        self.assertEquals(len(mail.outbox), 1)

        # see if we can view the address page
        address_response = self.client.get(reverse('lfs_my_addresses'))
        self.assertContains(address_response, 'City', status_code=200)

        # we should now have 2 customers
        self.assertEqual(len(Customer.objects.all()), 2)

    def dump_response(self, http_response):
        fo = open('tests_customers.html', 'w')
        fo.write(str(http_response))
        fo.close()

    @override_settings(LFS_AUTO_UPDATE_DEFAULT_ADDRESSES=False)
    def test_create_new_address(self):
        # test that we have only 4 addresses registered (from setUp)
        self.assertEquals(Address.objects.count(), 4)

        # register a new user
        registration_response = self.client.post(reverse('lfs_login'), {'action': 'register', 'email': 'test@test.com', 'password_1': 'password', 'password_2': 'password'})
        self.assertEquals(registration_response.status_code, 302)
        self.assertEquals(registration_response._headers['location'], ('Location', '/'))

        self.assertEquals(Address.objects.count(), 8)

        # Test that one message has been sent.
        self.assertEquals(len(mail.outbox), 1)

        our_user = User.objects.get(email='test@test.com')
        our_customer = Customer.objects.get(user=our_user)
        self.assertNotEquals(our_customer.selected_invoice_address, None)
        self.assertNotEquals(our_customer.selected_shipping_address, None)

        # see if we can view the addresss page
        address_data = {
            'invoice-firstname': 'Joe', 'invoice-lastname': 'Bloggs',
            'invoice-line1': 'de company name', 'invoice-line2': 'de street',
            'invoice-city': 'Dallas', 'invoice-state': 'TX',
            'invoice-code': '84003', 'invoice-country': 'US',
            'invoice-phone': '+49 4711 4711', 'invoice-email': 'joe.bloggs@acme.com',
            'shipping-firstname': 'Joe', 'shipping-lastname': 'Bloggs',
            'shipping-line1': 'de company name', 'shipping-line2': 'de street',
            'shipping-city': 'Dallas', 'shipping-state': 'TX',
            'shipping-code': '84003', 'shipping-country': 'US',
            'shipping-phone': '+49 4712 4712', 'invoice-email': 'joe.bloggs@acme.com',
        }

        self.client.post(reverse('lfs_my_addresses'), address_data)

        self.assertEquals(Address.objects.count(), 8)

        # refetch our user from the database
        our_customer = Customer.objects.get(user=our_user)
        self.assertNotEquals(our_customer.selected_invoice_address, None)
        self.assertNotEquals(our_customer.selected_shipping_address, None)
        self.assertEquals(our_customer.selected_invoice_address.firstname, 'Joe')
        self.assertEquals(our_customer.selected_invoice_address.lastname, 'Bloggs')

    @override_settings(LFS_AUTO_UPDATE_DEFAULT_ADDRESSES=False)
    def test_change_address_page(self):
        """
        Tests that we can see a shipping and an invoice address
        """
        # login as our customer
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        iam = AddressManagement(self.customer, self.address2, "invoice")
        sam = AddressManagement(self.customer, self.address1, "shipping")

        iam_data = iam.get_address_as_dict()
        sam_data = sam.get_address_as_dict()
        data = {"invoice-firstname": "newname",
                "invoice-lastname": self.address2.lastname,
                "invoice-phone": self.address2.phone,
                "invoice-email": self.address2.email,

                "shipping-firstname": self.address1.firstname,
                "shipping-lastname": self.address1.lastname,
                "shipping-phone": self.address1.phone,
                "shipping-email": self.address1.email,
                }
        for key, value in iam_data.items():
            data['invoice-%s' % key] = value

        for key, value in sam_data.items():
            data['shipping-%s' % key] = value

        data['invoice-country'] = 'AT'

        response = self.client.post(reverse('lfs_my_addresses'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        iam2 = Address.objects.get(pk=self.address2.pk)
        self.assertEqual(iam2.firstname, "newname")
        self.assertEqual(iam2.country.code.upper(), "AT")


class LoginTestCase(TestCase):

    fixtures = ['lfs_shop.xml']

    def test_register_customer(self):
        client = Client()
        response = client.get(reverse('lfs_login'))
        self.assertEqual(response.status_code, 200)

        self.assertFalse(User.objects.filter(username='test@example.com').exists())
        response = client.post(reverse('lfs_login'), {'email': 'test@example.com',
                                                      'password_1': 'test',
                                                      'password_2': 'test',
                                                      'action': 'register',
                                                      'next': '/'})
        self.assertTrue(User.objects.filter(username='test@example.com').exists())

        response = client.post(reverse('lfs_login'), {'email': 'testverylongemailaddressthatislongerthanusername@example.com',
                                                      'password_1': 'test',
                                                      'password_2': 'test',
                                                      'action': 'register',
                                                      'next': '/'})
        self.assertTrue(User.objects.filter(email='testverylongemailaddressthatislongerthanusername@example.com').exists())
        u = User.objects.get(email='testverylongemailaddressthatislongerthanusername@example.com')
        self.assertEqual(u.username, u.email[:30])

        new_username = create_unique_username('testverylongemailaddressthatislongerthanusername2@example.com')
        response = client.post(reverse('lfs_login'), {'email': 'testverylongemailaddressthatislongerthanusername2@example.com',
                                                      'password_1': 'test',
                                                      'password_2': 'test',
                                                      'action': 'register',
                                                      'next': '/'})
        self.assertTrue(User.objects.filter(email='testverylongemailaddressthatislongerthanusername2@example.com').exists())
        u = User.objects.get(email='testverylongemailaddressthatislongerthanusername2@example.com')
        self.assertEqual(u.username, new_username)

    def test_change_email(self):
        u = User.objects.create(username="test@example.com", email="test@example.com", is_active=True)
        u.set_password('test')
        u.save()
        client = Client()
        client.login(username='test@example.com', password='test')
        response = client.post(reverse('lfs_my_email'),
                               {'email': 'testverylongemailaddressthatislongerthanusername@example.com',
                                'action': 'email'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='testverylongemailaddressthatislongerthanusername@example.com').exists())
