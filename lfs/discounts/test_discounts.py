"""Discounts against real carts: which discounts apply (active, criteria, products in the cart), how much they are
worth (absolute, a percentage of the cart or of the discounted products' lines), how their tax is split off, and how
discounts that sum up and those that do not are combined."""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.core.cache import cache
from django.core.management import call_command
from django.test import RequestFactory

from lfs.cart import utils as cart_utils
from lfs.cart.models import CartItem
from lfs.catalog.models import Product
from lfs.criteria.models import CartPriceCriterion
from lfs.discounts.models import Discount
from lfs.discounts.settings import DISCOUNT_TYPE_ABSOLUTE, DISCOUNT_TYPE_PERCENTAGE
from lfs.discounts.utils import get_discounts_data, get_valid_discounts
from lfs.tax.models import Tax

ABSOLUTE, PERCENTAGE = DISCOUNT_TYPE_ABSOLUTE, DISCOUNT_TYPE_PERCENTAGE


@pytest.fixture(autouse=True)
def empty_cache():
    """Start every test with an empty cache: carts and criteria are cached by id, and SQLite hands out the same ids
    again after a test's rollback."""
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


def add_to_cart(request, price: float, amount: int = 1) -> Product:
    """Put ``amount`` pieces of a new product costing ``price`` (gross) into the visitor's cart."""
    cart = cart_utils.get_cart(request) or cart_utils.create_cart(request)
    n = Product.objects.count()
    product = Product.objects.create(name=f"Product {n}", slug=f"product-{n}", price=price, active=True)
    CartItem.objects.create(cart=cart, product=product, amount=amount)
    return product


def discount(name: str = "Summer", value: float = 10.0, type: int = ABSOLUTE, **fields) -> Discount:
    """Create an active discount."""
    return Discount.objects.create(name=name, value=value, type=type, active=True, **fields)


def valid(request) -> dict[str, dict]:
    """Return the valid discounts by name."""
    return {d["name"]: d for d in get_valid_discounts(request)}


class TestWhichDiscountsApply:
    def test_only_active_discounts(self, request_):
        add_to_cart(request_, 100.0)
        discount("Summer")
        Discount.objects.create(name="Winter", value=5.0, active=False)

        assert list(valid(request_)) == ["Summer"]

    def test_a_criterion_decides(self, request_):
        big_carts = discount("Big carts")
        CartPriceCriterion.objects.create(content=big_carts, operator=CartPriceCriterion.GREATER_THAN, value=100)

        add_to_cart(request_, 50.0)
        assert valid(request_) == {}

        cache.clear()
        add_to_cart(request_, 80.0)
        assert list(valid(request_)) == ["Big carts"]

    def test_a_product_discount_needs_one_of_its_products_in_the_cart(self, request_):
        lamp = Product.objects.create(name="Lamp", slug="lamp", price=40.0, active=True)
        lamps = discount("Lamps")
        lamps.products.add(lamp)

        add_to_cart(request_, 100.0)
        assert valid(request_) == {}

        CartItem.objects.create(cart=cart_utils.get_cart(request_), product=lamp, amount=1)
        cache.clear()
        assert list(valid(request_)) == ["Lamps"]

    def test_a_product_discount_does_not_break_a_visitor_without_cart(self, request_):
        lamps = discount("Lamps")
        lamps.products.add(Product.objects.create(name="Lamp", slug="lamp", price=40.0, active=True))

        assert valid(request_) == {}


class TestValue:
    def test_an_absolute_discount_is_its_value(self, request_):
        add_to_cart(request_, 100.0)
        discount(value=15.0)

        assert valid(request_)["Summer"]["price_gross"] == 15.0

    def test_a_percentage_discount_is_a_share_of_the_cart(self, request_):
        add_to_cart(request_, 150.0)
        add_to_cart(request_, 25.0, amount=2)
        discount(value=10.0, type=PERCENTAGE)

        assert valid(request_)["Summer"]["price_gross"] == pytest.approx(20.0)

    def test_a_percentage_product_discount_is_a_share_of_its_products_lines_only(self, request_):
        add_to_cart(request_, 100.0)
        lamp = add_to_cart(request_, 40.0, amount=2)
        lamps = discount("Lamps", value=10.0, type=PERCENTAGE)
        lamps.products.add(lamp)

        assert valid(request_)["Lamps"]["price_gross"] == pytest.approx(8.0)

    def test_the_tax_is_split_off_the_gross_value(self, request_):
        add_to_cart(request_, 100.0)
        discount(value=11.9, tax=Tax.objects.create(rate=19))

        summer = valid(request_)["Summer"]
        assert (summer["price_gross"], summer["tax"], summer["price_net"]) == pytest.approx((11.9, 1.9, 10.0))

    def test_an_absolute_discount_without_tax_has_none(self, request_):
        add_to_cart(request_, 100.0)
        discount(value=10.0)

        assert valid(request_)["Summer"]["tax"] == 0.0


class TestCombiningDiscounts:
    def test_discounts_that_sum_up_are_added(self, request_):
        add_to_cart(request_, 100.0)
        discount("Summer", value=10.0, sums_up=True)
        discount("Loyalty", value=5.0, sums_up=True)

        data = get_discounts_data(request_)

        assert data["summed_up_value"] == 15.0
        assert sorted(d["name"] for d in data["summed_up_discounts"]) == ["Loyalty", "Summer"]

    def test_of_the_discounts_that_do_not_sum_up_the_largest_counts(self, request_):
        add_to_cart(request_, 100.0)
        discount("Small", value=5.0, sums_up=False)
        discount("Large", value=12.0, sums_up=False)

        data = get_discounts_data(request_)

        assert (data["max_value"], [d["name"] for d in data["max_discounts"]]) == (12.0, ["Large"])
        assert data["summed_up_value"] == 0.0
