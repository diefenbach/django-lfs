# python imports
import datetime

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
            number_prefix="DH",
            number_suffix="XM",
            number_length=4,
            number_letters="abcdefghijklmnopqrstuvwxyz",
            )

        number = lfs.voucher.utils.create_voucher_number()
        self.failUnless(len(number) == 8)

        letters = "abcdefghijklmnopqrstuvwxyz"

        for letter in number[2:-2]:
            self.failIf(letter not in letters)


class VoucherTestCase(TestCase):
    """
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        self.request = RequestFactory().get("/")
        self.request.session = SessionStore()
        self.request.user = User(id=1)

        self.vg = VoucherGroup.objects.create(
            name="xmas",
            creator=self.request.user,
        )

        self.v1 = Voucher.objects.create(
            number="AAAA",
            group=self.vg,
            creator=self.request.user,
            start_date=datetime.date(2009, 12, 1),
            end_date=datetime.date(2009, 12, 31),
            effective_from=0,
            kind_of=ABSOLUTE,
            value=10.0,
            limit=2,
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
        self.assertEqual(self.v1.start_date, datetime.date(2009, 12, 1),)
        self.assertEqual(self.v1.end_date, datetime.date(2009, 12, 31),)
        self.assertEqual(self.v1.effective_from, 0.0)
        self.assertEqual(self.v1.kind_of, ABSOLUTE)
        self.assertEqual(self.v1.active, True)
        self.assertEqual(self.v1.used_amount, 0)
        self.assertEqual(self.v1.last_used_date, None)
        self.assertEqual(self.v1.value, 10.0)
        self.assertEqual(self.v1.tax, None)

    def test_prices_absolute(self):
        """
        """
        # No tax
        price_net = self.v1.get_price_net(self.request)
        self.assertEqual(price_net, 10)

        price_gross = self.v1.get_price_gross(self.request)
        self.assertEqual(price_gross, 10)

        tax = self.v1.get_tax(self.request)
        self.assertEqual(tax, 0.0)

        # With tax
        self.v1.tax = Tax.objects.create(rate=19.0)
        self.v1.save()

        price_net = self.v1.get_price_net(self.request)
        self.assertEqual("%.2f" % price_net, "%.2f" % 8.4)

        price_gross = self.v1.get_price_gross(self.request)
        self.assertEqual(price_gross, 10)

        tax = self.v1.get_tax(self.request)
        self.assertEqual("%.2f" % tax, "%.2f" % 1.6)

    def test_prices_percentage(self):
        """
        """
        # 10% discount
        self.v1.kind_of = PERCENTAGE
        self.v1.value = 10.0
        self.v1.save()

        # No tax
        price_gross = self.v1.get_price_gross(self.request, self.cart)
        self.assertEqual(price_gross, 11.0)

        price_net = self.v1.get_price_net(self.request, self.cart)
        self.assertEqual(price_net, 11.0)

        tax = self.v1.get_tax(self.request, self.cart)
        self.assertEqual(tax, 0.0)

        # With tax
        # Note: If the voucher is pecentage the tax is taken from the several
        # products not from the voucher itself.
        tax = Tax.objects.create(rate=19.0)
        self.p1.tax = tax
        self.p1.save()
        self.p2.tax = tax
        self.p2.save()

        price_gross = self.v1.get_price_gross(self.request, self.cart)
        self.assertEqual(price_gross, 11.0)

        price_net = self.v1.get_price_net(self.request, self.cart)
        self.assertEqual("%.2f" % price_net, "%.2f" % 9.24)

        tax = self.v1.get_tax(self.request, self.cart)
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
        self.assertEqual(self.v1.used_amount, 0)
        self.assertEqual(self.v1.last_used_date, None)

        self.v1.mark_as_used()

        self.assertEqual(self.v1.used_amount, 1)
        self.failIf(self.v1.last_used_date is None)

    def test_is_effective(self):
        """
        """
        current_year = datetime.datetime.now().year

        # True
        self.v1.start_date = datetime.date(2000, 1, 1)
        self.v1.end_date = datetime.date(2999, 12, 31)
        self.v1.active = True
        self.v1.used_amount = 1
        self.v1.effective_from = 0
        self.assertEqual(self.v1.is_effective(self.request, self.cart)[0], True)

        # start / end
        self.v1.start_date = datetime.date(current_year, 12, 31)
        self.v1.end_date = datetime.date(current_year, 12, 31)
        self.v1.active = True
        self.v1.used_amount = 1
        self.v1.effective_from = 0
        self.assertEqual(self.v1.is_effective(self.request, self.cart)[0], False)

        # effective from
        self.v1.start_date = datetime.date(current_year, 1, 1)
        self.v1.end_date = datetime.date(current_year, 12, 31)
        self.v1.active = True
        self.v1.used_amount = 1
        self.v1.effective_from = 1000
        self.assertEqual(self.v1.is_effective(self.request, self.cart)[0], False)

        # Used
        self.v1.start_date = datetime.date(current_year, 1, 1)
        self.v1.end_date = datetime.date(current_year, 12, 31)
        self.v1.active = True
        self.v1.used_amount = 1
        self.v1.effective_from = 0
        self.assertEqual(self.v1.is_effective(self.request, self.cart)[0], True)

        self.v1.mark_as_used()
        self.assertEqual(self.v1.is_effective(self.request, self.cart)[0], False)

        # unlimited amount
        self.v1.limit = 0
        self.assertEqual(self.v1.is_effective(self.request, self.cart)[0], True)

        # Not active
        self.v1.start_date = datetime.date(current_year, 1, 1)
        self.v1.end_date = datetime.date(current_year, 12, 31)
        self.v1.active = False
        self.v1.used_amount = 1
        self.v1.effective_from = 0
        self.assertEqual(self.v1.is_effective(self.request, self.cart)[0], False)


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
