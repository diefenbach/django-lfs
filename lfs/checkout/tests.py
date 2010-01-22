# django imports
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.file import SessionStore
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

# test imports
from lfs.catalog.models import Product
from lfs.cart.models import Cart
from lfs.cart.models import CartItem
from lfs.cart.views import add_to_cart
from lfs.cart import utils as cart_utils
from lfs.core.models import Country
from lfs.customer.models import Address
from lfs.customer.models import Customer
from lfs.order.utils import add_order
from lfs.order.settings import SUBMITTED
from lfs.payment.models import PaymentMethod
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax

class CheckoutTestCase(TestCase):
    """
    """
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
        
        country = Country.objects.create(name="Middle-earth")
        
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
        
        self.PRODUCT1_NAME="Surfboard"
        p1 = Product.objects.create(
            name=self.PRODUCT1_NAME,
            slug="product-1",
            sku="sku-1",
            price=1.1,
            tax = tax,
        )
            
        p2 = Product.objects.create(
            name="Product 2",
            slug="product-2",
            sku="sku-2",
            price=2.2,
            tax = tax,
        )
        
        cart = Cart.objects.create(
            user=new_user
        )
        
        item = CartItem.objects.create(
            cart = cart,
            product = p1,
            amount = 2,
        )

        item = CartItem.objects.create(
            cart = cart,
            product = p2,
            amount = 3,
        )
        
        self.c = Client()
        
        # login as our customer
        logged_in = self.c.login(username=self.username, password=self.password)
        self.assertEqual(logged_in, True)
        
    def test_checkout_page(self):
        """Tests that checkout page gets populated with correct details
        """
        cart_response = self.c.get(reverse('lfs_cart'))
        self.assertContains(cart_response, self.PRODUCT1_NAME, status_code=200)        
        
        checkout_response = self.c.get(reverse('lfs_checkout'))
        self.assertContains(checkout_response, 'Smallville', status_code=200)
    
