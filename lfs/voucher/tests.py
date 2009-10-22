# django imports
from django.contrib.auth.models import User
from django.contrib.sessions.backends.file import SessionStore
from django.test import TestCase

# lfs imports
import lfs.voucher.utils
from lfs.cart.models import Cart
from lfs.cart.models import CartItem
from lfs.catalog.models import Product
from lfs.tests.utils import RequestFactory
from lfs.tax.models import Tax
from lfs.voucher.models import Voucher
from lfs.voucher.models import VoucherGroup
from lfs.voucher.models import VoucherOptions
from lfs.voucher.settings import ABSOLUTE
from lfs.voucher.settings import PERCENTAGE

class VoucherUtilsTestCase(TestCase):
    """
    """
    def test_create_vouchers_1(self):
        """Tests the default voucher options
        """
        number = lfs.voucher.utils.create_voucher_number()
        self.failUnless(len(number) == 5)

        letters = "ABCDEFGHIJKLMNOPQRSTUVXYZ"

        for letter in number:
            self.failIf(letter not in letters)

    def test_create_vouchers_2(self):
        """Tests the custom options.
        """
        VoucherOptions.objects.create(
            number_prefix = "DH",
            number_suffix = "XM",
            number_length = 4,
            number_letters = "abcdefghijklmnopqrstuvwxyz",
            )

        number = lfs.voucher.utils.create_voucher_number()
        self.failUnless(len(number) == 8)

        letters = "abcdefghijklmnopqrstuvwxyz"

        for letter in number[2:-2]:
            self.failIf(letter not in letters)

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
            start_date = "2009-12-01",
            end_date = "2009-12-31",
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
        self.assertEqual(self.v1.start_date, "2009-12-01")
        self.assertEqual(self.v1.end_date, "2009-12-31")
        self.assertEqual(self.v1.kind_of, ABSOLUTE)
        self.assertEqual(self.v1.active, True)
        self.assertEqual(self.v1.used, False)
        self.assertEqual(self.v1.used_date, None)
        self.assertEqual(self.v1.value, 10.0)

    def test_prices_absolute(self):
        """
        """
        # No tax
        price = self.v1.get_price()
        self.assertEqual(price, 10)

    def test_prices_percentage(self):
        """
        """
        # 10% discount
        self.v1.kind_of = PERCENTAGE
        self.v1.value = 10.0
        self.v1.save()

        price = self.v1.get_price(self.cart)
        self.assertEqual(price, 11.0)

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
        
        
class VoucherOptionsCase(TestCase):
    """
    """
    def tests_default_values(self):
        """
        """
        vo = VoucherOptions.objects.create()
        self.assertEqual(vo.number_prefix, u"")
        self.assertEqual(vo.number_suffix, u"")
        self.assertEqual(vo.number_length, 5)
        self.assertEqual(vo.number_letters, u"ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        