"""Vouchers against real carts: when a voucher can be redeemed (active, not used up, within its dates, cart above
its minimum), what it is worth (absolute with its tax split off, or a share of the cart), counting its uses, the
voucher a customer entered in the session, and the numbers generated for new vouchers."""

import datetime

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.core.cache import cache
from django.core.management import call_command
from django.test import RequestFactory

from lfs.cart import utils as cart_utils
from lfs.cart.models import CartItem
from lfs.catalog.models import Product
from lfs.tax.models import Tax
from lfs.voucher import utils as voucher_utils
from lfs.voucher.models import Voucher, VoucherOptions
from lfs.voucher.settings import ABSOLUTE, MESSAGES, PERCENTAGE

TODAY = datetime.date.today()
DAY = datetime.timedelta(days=1)


@pytest.fixture(autouse=True)
def empty_cache():
    """Start every test with an empty cache: carts are cached by id, and SQLite hands out the same ids again after
    a test's rollback."""
    cache.clear()


@pytest.fixture
def request_(db):
    """A request of an anonymous visitor with a session, in LFS's default shop."""
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    request.session = SessionStore()
    request.session.save()
    return request


def cart_with(request, price: float, tax: Tax | None = None):
    """Return the visitor's cart holding one product that costs ``price`` (gross)."""
    cart = cart_utils.get_cart(request) or cart_utils.create_cart(request)
    n = Product.objects.count()
    product = Product.objects.create(name=f"Product {n}", slug=f"product-{n}", price=price, tax=tax, active=True)
    CartItem.objects.create(cart=cart, product=product, amount=1)
    return cart


def voucher(**fields) -> Voucher:
    """Create a voucher worth 10, valid from yesterday to tomorrow, usable once."""
    values = {"number": "AAAA", "kind_of": ABSOLUTE, "value": 10.0, "start_date": TODAY - DAY, "end_date": TODAY + DAY}
    values.update(fields)
    return Voucher.objects.create(**values)


class TestWhenAVoucherCanBeRedeemed:
    def test_a_valid_voucher(self, request_):
        assert voucher().is_effective(request_, cart_with(request_, 50.0)) == (True, MESSAGES[0])

    @pytest.mark.parametrize(
        "fields,message",
        [
            ({"active": False}, MESSAGES[1]),
            ({"limit": 2, "used_amount": 2}, MESSAGES[2]),
            ({"start_date": TODAY + DAY}, MESSAGES[3]),
            ({"end_date": TODAY - DAY}, MESSAGES[4]),
            ({"effective_from": 50.01}, MESSAGES[5]),
        ],
        ids=["inactive", "used up", "not yet", "expired", "cart below minimum"],
    )
    def test_is_refused_with_the_reason(self, request_, fields: dict, message: str):
        assert voucher(**fields).is_effective(request_, cart_with(request_, 50.0)) == (False, message)

    def test_is_valid_on_its_first_and_last_day(self, request_):
        assert voucher(start_date=TODAY, end_date=TODAY).is_effective(request_, cart_with(request_, 50.0))[0]

    def test_a_cart_exactly_at_the_minimum_is_enough(self, request_):
        assert voucher(effective_from=50.0).is_effective(request_, cart_with(request_, 50.0))[0]

    def test_a_limit_of_zero_means_unlimited(self, request_):
        assert voucher(limit=0, used_amount=99).is_effective(request_, cart_with(request_, 50.0))[0]

    def test_each_use_is_counted_until_the_limit(self, request_):
        v = voucher(limit=2)
        cart = cart_with(request_, 50.0)

        v.mark_as_used()
        assert (v.used_amount, v.last_used_date is not None, v.is_effective(request_, cart)[0]) == (1, True, True)
        v.mark_as_used()
        assert (v.used_amount, v.is_effective(request_, cart)[0]) == (2, False)


class TestValue:
    def test_an_absolute_voucher_is_its_value_with_its_tax_split_off(self, request_):
        v = voucher(value=11.9, tax=Tax.objects.create(rate=19))

        assert (v.get_price_gross(request_), v.get_tax(request_), v.get_price_net(request_)) == pytest.approx(
            (11.9, 1.9, 10.0)
        )

    def test_an_absolute_voucher_without_tax_is_all_net(self, request_):
        v = voucher(value=10.0)

        assert (v.get_price_gross(request_), v.get_tax(request_), v.get_price_net(request_)) == (10.0, 0.0, 10.0)

    def test_a_percentage_voucher_is_a_share_of_the_cart_and_its_tax(self, request_):
        cart = cart_with(request_, 119.0, tax=Tax.objects.create(rate=19))
        v = voucher(kind_of=PERCENTAGE, value=10.0)

        assert (v.get_price_gross(request_, cart), v.get_tax(request_, cart), v.get_price_net(request_, cart)) == (
            pytest.approx((11.9, 1.9, 10.0))
        )


class TestTheVoucherInTheSession:
    def test_an_effective_voucher_entered_by_the_customer_is_applied(self, request_):
        cart = cart_with(request_, 50.0)
        voucher(number="SUMMER", value=10.0)
        voucher_utils.set_current_voucher_number(request_, "SUMMER")

        data = voucher_utils.get_voucher_data(request_, cart)

        assert (data["voucher"].number, data["voucher_value"], data["voucher_message"]) == ("SUMMER", 10.0, MESSAGES[0])

    def test_a_voucher_that_is_not_effective_is_not_applied_but_explained(self, request_):
        cart = cart_with(request_, 50.0)
        voucher(number="SUMMER", effective_from=100.0)
        voucher_utils.set_current_voucher_number(request_, "SUMMER")

        data = voucher_utils.get_voucher_data(request_, cart)

        assert (data["voucher"], data["voucher_value"], data["voucher_message"]) == (None, 0.0, MESSAGES[5])

    def test_an_unknown_number_is_explained(self, request_):
        voucher_utils.set_current_voucher_number(request_, "NOPE")

        data = voucher_utils.get_voucher_data(request_, cart_with(request_, 50.0))

        assert (data["voucher"], data["voucher_message"]) == (None, MESSAGES[6])

    def test_removing_the_number_from_the_session(self, request_):
        voucher_utils.set_current_voucher_number(request_, "SUMMER")

        voucher_utils.delete_current_voucher_number(request_)

        assert voucher_utils.get_current_voucher_number(request_) == ""


class TestNewNumbers:
    def test_use_the_options(self, db):
        VoucherOptions.objects.create(number_prefix="LFS-", number_suffix="-X", number_length=8, number_letters="AB")

        number = voucher_utils.create_voucher_number()

        assert number.startswith("LFS-") and number.endswith("-X")
        assert len(number) == len("LFS-") + 8 + len("-X")
        assert set(number[4:-2]) <= {"A", "B"}

    def test_without_options_are_five_capital_letters(self, db):
        number = voucher_utils.create_voucher_number()

        assert len(number) == 5 and number.isalpha() and number.isupper()
