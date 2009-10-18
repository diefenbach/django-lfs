# django imports
from django.contrib.auth.models import User
from django.contrib.sessions.backends.file import SessionStore
from django.test import TestCase

# lfs imports
from lfs.cart.models import Cart
from lfs.cart.models import CartItem
from lfs.catalog.models import Product
from lfs.tests.utils import RequestFactory
from lfs.tax.models import Tax
from lfs.voucher.models import Voucher
from lfs.voucher.models import VoucherGroup
from lfs.voucher.settings import ABSOLUTE
from lfs.voucher.settings import PERCENTAGE

class CartModelsTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        self.tax = Tax.objects.create(rate=19.0)
        
        self.p1 = Product.objects.create(name="Product 1", slug="product-1", price=10.0, tax=self.tax)
        self.p2 = Product.objects.create(name="Product 2", slug="product-2", price=100.0, tax=self.tax)
        

        self.cart = Cart.objects.create()
        CartItem.objects.create(cart=self.cart, product=self.p1, amount=1)
        CartItem.objects.create(cart=self.cart, product=self.p2, amount=1)

    def test_get_price(self):
        """
        """
        price_net = self.cart.get_price_net()
        self.assertEqual("%.2f" % price_net, "%.2f" % 92.44)

    def test_get_gross(self):
        """
        """
        price_gross = self.cart.get_price_gross()
        self.assertEqual(price_gross, 110.0)
        
    def test_tax(self):
        """
        """
        tax = self.cart.get_tax()
        self.assertEqual("%.2f" % tax, "%.2f" % 17.56)
        
    def test_get_amount_of_items(self):
        """
        """
        amount = self.cart.amount_of_items
        self.assertEqual(2, 2)
        
    def test_get_items(self):
        """
        """
        items = self.cart.items()
        self.assertEqual(len(items), 2)