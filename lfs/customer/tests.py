# django imports
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import mail

# lfs imports
from lfs.core.models import Shop
from lfs.customer.models import Customer
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax
from lfs.payment.models import PaymentMethod

# other imports
from countries.models import Country
from postal.models import PostalAddress

class AddressTestCase(TestCase):
    
    def setUp(self):
        """
        """
        ie = Country.objects.get(iso="IE")
        gb = Country.objects.get(iso="GB")
        de = Country.objects.get(iso="DE")
        us = Country.objects.get(iso="US")
        fr = Country.objects.get(iso="FR")

        shop, created = Shop.objects.get_or_create(name="lfs test", shop_owner="John Doe",
                                          default_country=de)
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
         
        tax = Tax.objects.create(rate = 19)
        
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
        
        country = Country.objects.get(iso="DE")
        
        address1 = PostalAddress.objects.create(
            line1 = "Doe Ltd.",
            line2 = "Street 42",
            line3 = "2342",
            line5 = "Gotham City",
            country = country,
        )

        address2 = PostalAddress.objects.create(
            line1 = "Doe Ltd.",
            line2 = "Street 43",
            line3 = "2443",
            line5 = "Smallville",
            country = country,
        )
        
        self.username = 'joe'
        self.password = 'bloggs'
    
        new_user = User(username=self.username)
        new_user.set_password(self.password)
        new_user.save()
        
        self.customer = Customer.objects.create(
            user = new_user,
            selected_shipping_method = shipping_method,
            selected_payment_method = payment_method,
            selected_shipping_firstname = "John",
            selected_shipping_lastname = "Doe",
            selected_shipping_address = address1,
            selected_invoice_firstname = "Jane",
            selected_invoice_lastname = "Doe",
            selected_invoice_address = address2,            
        )
        self.c = Client()
    
    def test_address_page(self):
        """
        Tests that we can see a shipping and an invoice address
        """
         # login as our customer
        logged_in = self.c.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)

        address_response = self.c.get(reverse('lfs_my_addresses'))
        self.dump_response(address_response)
        self.assertContains(address_response, 'Smallville', status_code=200)
        self.assertContains(address_response, 'Gotham City', status_code=200)
        
        
    def test_register_then_view_address(self):
        """Check we have a customer in database after registration"""
        # we should have one customer starting
        self.assertEqual(len(Customer.objects.all()), 1)

        registration_response = self.c.post(reverse('lfs_login'), {'action': 'register', 'email': 'test@test.com', 'password_1': 'password', 'password_2': 'password'})
        self.assertEquals(registration_response.status_code, 302)
        self.assertEquals(registration_response._headers['location'], ('Location', 'http://testserver/'))
        
        # Test that one message has been sent.
        self.assertEquals(len(mail.outbox), 1)
        
        # see if we can view the addresss page
        address_response = self.c.get(reverse('lfs_my_addresses'))
        self.assertContains(address_response, 'City', status_code=200)
        
        # we should now have 2 customers
        self.assertEqual(len(Customer.objects.all()), 2)

    def dump_response(self, http_response):
        fo = open('tests_customers.html', 'w')
        fo.write(str(http_response))
        fo.close()

    def test_create_new_address(self):
        # test that we have only 2 addresses registered (from setUp)
        self.assertEquals(PostalAddress.objects.count(), 2)

        # register a new user
        registration_response = self.c.post(reverse('lfs_login'), {'action': 'register', 'email': 'test@test.com', 'password_1': 'password', 'password_2': 'password'})
        self.assertEquals(registration_response.status_code, 302)
        self.assertEquals(registration_response._headers['location'], ('Location', 'http://testserver/'))

        # Test that one message has been sent.
        self.assertEquals(len(mail.outbox), 1)

        our_user = User.objects.get(email='test@test.com')
        our_customer = Customer.objects.get(user=our_user)
        self.assertEquals(our_customer.selected_invoice_address, None)

        # see if we can view the addresss page
        address_data = {'invoice_firstname': 'Joe', 'invoice_lastname': 'Bloggs',
                        'invoice-line1': 'de company name', 'invoice-line2': 'de street',
                        'invoice-line3': 'Dallas', 'invoice-line4': 'TX',
                        'invoice-line5': '84003', 'invoice-country': 'US',
                        'shipping-country': 'IE'}
        address_response = self.c.post(reverse('lfs_my_addresses'), address_data)
        
        # We get 2 new postal addresses one shipping and one postal
        self.assertEquals(PostalAddress.objects.count(), 4)
        self.assertRedirects(address_response, reverse('lfs_my_addresses'), status_code=302, target_status_code=200,)

        # refetch our user from the database
        our_customer = Customer.objects.get(user=our_user)
        self.assertNotEquals(our_customer.selected_invoice_address, None)
