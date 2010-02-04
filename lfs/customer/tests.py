# django imports
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import mail


# lfs imports
from lfs.core.models import Country
from lfs.customer.models import Address
from lfs.customer.models import Customer
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax
from lfs.payment.models import PaymentMethod


class AddressTestCase(TestCase):
    
    fixtures = ['lfs_shop.xml', 'lfs_all_countries.xml']
    
    def setUp(self):
        """
        """         
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
        
        country = Country.objects.get(code="ie")
        
        address1 = Address.objects.create(
            firstname = "John",
            lastname = "Doe",
            company_name = "Doe Ltd.",
            street = "Street 42",
            zip_code = "2342",
            city = "Gotham City",
            country = country,
            phone = "555-111111",
            email = "john@doe.com",
        )

        address2 = Address.objects.create(
            firstname = "Jane",
            lastname = "Doe",
            company_name = "Doe Ltd.",
            street = "Street 43",
            zip_code = "2443",
            city = "Smallville",
            country = country,
            phone = "666-111111",
            email = "jane@doe.com",
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
            selected_shipping_address = address1,
            selected_invoice_address = address2,            
        )
        self.c = Client()
        
        # login as our customer
        logged_in = self.c.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)
    
    def test_address_page(self):
        """
        Tests that we can see a shipping and an invoice address
        """
        address_response = self.c.get(reverse('lfs_my_addresses'))
        self.assertContains(address_response, 'Smallville', status_code=200)
        self.assertContains(address_response, 'Gotham City', status_code=200)
        
        
    def test_register_then_view_address(self):
        """Check we have a customer in database after registration"""
        # we should have one customer starting
        self.assertEqual(len(Customer.objects.all()), 1)
        
        # logout joe
        self.c.logout()        
        
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
