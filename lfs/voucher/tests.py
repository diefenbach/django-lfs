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

class VoucherUtilsTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        pass

    def test_create_vouchers(self):
        """
        """
        pass

class VoucherTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        self.request = RequestFactory().get("/")
        self.request.session = SessionStore()
        self.request.user = User(id=1)

        self.vg = VoucherGroup.objects.create(
            name="xmas",
            creator = self.request.user,
        )

        self.v1 = Voucher.objects.create(
            number = "AAAA",
            group = self.vg,
            creator = self.request.user,
            expiration_date = "2009-12-31",
            kind_of = ABSOLUTE,
            value = 10.0,
        )

        self.p1 = Product.objects.create(name="Product 1", slug="product-1", price=10.0)
        self.p2 = Product.objects.create(name="Product 2", slug="product-2", price=100.0)

        self.cart = Cart.objects.create()
        CartItem.objects.create(cart=self.cart, product=self.p1, amount=1)
        CartItem.objects.create(cart=self.cart, product=self.p2, amount=1)

    def test_defaults(self):
        """
        """
        self.assertEqual(self.v1.number, "AAAA")
        self.assertEqual(self.v1.group, self.vg)
        self.assertEqual(self.v1.creator, self.request.user)
        self.assertEqual(self.v1.expiration_date, "2009-12-31")
        self.assertEqual(self.v1.kind_of, ABSOLUTE)
        self.assertEqual(self.v1.active, True)
        self.assertEqual(self.v1.used, False)
        self.assertEqual(self.v1.used_date, None)
        self.assertEqual(self.v1.value, 10.0)
        self.assertEqual(self.v1.tax, None)

    def test_prices_absolute(self):
        """
        """
        # No tax
        price_net = self.v1.get_price_net()
        self.assertEqual(price_net, 10)

        price_gross = self.v1.get_price_gross()
        self.assertEqual(price_gross, 10)

        tax = self.v1.get_tax()
        self.assertEqual(tax, 0.0)

        # With tax
        self.v1.tax = Tax.objects.create(rate=19.0)
        self.v1.save()

        price_net = self.v1.get_price_net()
        self.assertEqual("%.2f" % price_net, "%.2f" % 8.4)

        price_gross = self.v1.get_price_gross()
        self.assertEqual(price_gross, 10)

        tax = self.v1.get_tax()
        self.assertEqual("%.2f" % tax, "%.2f" % 1.6)

    def test_prices_percentage(self):
        """
        """
        # 10% discount
        self.v1.kind_of = PERCENTAGE
        self.v1.value = 10.0
        self.v1.save()

        # No tax
        price_gross = self.v1.get_price_gross(self.cart)
        self.assertEqual(price_gross, 11.0)

        price_net = self.v1.get_price_net(self.cart)
        self.assertEqual(price_net, 11.0)

        tax = self.v1.get_tax(self.cart)
        self.assertEqual(tax, 0.0)

        # With tax
        # Note: If the voucher is pecentage the tax is taken from the several 
        # products not from the voucher itself.
        tax = Tax.objects.create(rate=19.0)
        self.p1.tax = tax
        self.p1.save()
        self.p2.tax = tax
        self.p2.save()

        price_gross = self.v1.get_price_gross(self.cart)
        self.assertEqual(price_gross, 11.0)

        price_net = self.v1.get_price_net(self.cart)
        self.assertEqual("%.2f" % price_net, "%.2f" % 9.24)

        tax = self.v1.get_tax(self.cart)
        self.assertEqual("%.2f" % tax, "%.2f" % 1.76)

    def test_kind_of(self):
        """
        """
        self.assertEqual(self.v1.kind_of, ABSOLUTE)
        self.assertEqual(self.v1.is_absolute(), True)
        self.assertEqual(self.v1.is_percentage(), False)

        self.v1.kind_of = PERCENTAGE
        self.v1.save()

        self.assertEqual(self.v1.kind_of, PERCENTAGE)
        self.assertEqual(self.v1.is_absolute(), False)
        self.assertEqual(self.v1.is_percentage(), True)

    def test_mark_as_used(self):
        """
        """
        self.assertEqual(self.v1.used, False)
        self.assertEqual(self.v1.used_date, None)

        self.v1.mark_as_used()

        self.assertEqual(self.v1.used, True)
        self.failIf(self.v1.used_date is None)
