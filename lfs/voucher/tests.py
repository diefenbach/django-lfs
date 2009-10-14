# django imports
from django.contrib.auth.models import User
from django.contrib.sessions.backends.file import SessionStore
from django.core.urlresolvers import reverse
from django.test import TestCase

# lfs imports
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

    def test_prices(self):
        """
        """
        # Absolute without tax
        price_net = self.v1.get_price_net()
        self.assertEqual(price_net, 10)

        price_gross = self.v1.get_price_gross()
        self.assertEqual(price_gross, 10)

        tax = self.v1.get_tax()
        self.assertEqual(tax, 0.0)

        # Absolute with tax
        self.v1.tax = Tax.objects.create(rate=19.0)
        self.v1.save()

        price_net = self.v1.get_price_net()
        self.assertEqual("%.2f" % price_net, "%.2f" % 8.4)

        price_gross = self.v1.get_price_gross()
        self.assertEqual(price_gross, 10)

        tax = self.v1.get_tax()
        self.assertEqual("%.2f" % tax, "%.2f" % 1.6)

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
