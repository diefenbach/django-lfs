# django imports
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import mail

# lfs imports
from lfs.customer.models import Customer
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax
from lfs.payment.models import PaymentMethod

# other imports
from countries.models import Country
from postal.models import PostalAddress

class AddressTestCase(TestCase):
    
    fixtures = ['lfs_shop.xml']
    
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
        
        country = Country.objects.get(iso="IE")
        
        address1 = PostalAddress.objects.create(
            firstname = "John",
            lastname = "Doe",
            line1 = "Doe Ltd.",
            line2 = "Street 42",
            line3 = "2342",
            line4 = "Gotham City",
            country = country,
        )

        address2 = PostalAddress.objects.create(
            firstname = "Jane",
            lastname = "Doe",
            line1 = "Doe Ltd.",
            line2 = "Street 43",
            line3 = "2443",
            line4 = "Smallville",
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
