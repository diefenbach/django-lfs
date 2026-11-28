"""The criteria that decide which shipping and payment methods, prices and discounts apply, evaluated against real
carts, products, customers and countries: each number criterion with each operator at its boundary, the cart's sum
or maximum against the product's own value, the country of the customer, the selected or valid shipping and payment
method, and an object with several criteria that applies only when all of them hold."""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.core.cache import cache
from django.core.management import call_command
from django.test import RequestFactory

from lfs.cart import utils as cart_utils
from lfs.cart.models import CartItem
from lfs.catalog.models import Product
from lfs.core.models import Country
from lfs.criteria.models import (
    CartPriceCriterion,
    CombinedLengthAndGirthCriterion,
    CountryCriterion,
    Criterion,
    HeightCriterion,
    LengthCriterion,
    PaymentMethodCriterion,
    ShippingMethodCriterion,
    WeightCriterion,
    WidthCriterion,
)
from lfs.customer import utils as customer_utils
from lfs.payment.models import PaymentMethod
from lfs.shipping.models import ShippingMethod

EQ, LT, LTE, GT, GTE = (
    Criterion.EQUAL,
    Criterion.LESS_THAN,
    Criterion.LESS_THAN_EQUAL,
    Criterion.GREATER_THAN,
    Criterion.GREATER_THAN_EQUAL,
)


@pytest.fixture(autouse=True)
def empty_cache():
    """Start every test with an empty cache: criteria and carts are cached by id, and SQLite hands out the same ids
    again after a test's rollback."""
    cache.clear()


@pytest.fixture
def shop(db):
    """The default shop of LFS's fixture, without its payment and shipping methods."""
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    PaymentMethod.objects.all().delete()
    ShippingMethod.objects.all().delete()


@pytest.fixture
def request_(shop):
    """A request of an anonymous visitor with a session."""
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    request.session = SessionStore()
    request.session.save()
    return request


@pytest.fixture
def method(shop) -> PaymentMethod:
    """A payment method to attach criteria to."""
    return PaymentMethod.objects.create(name="Invoice", active=True)


def add_to_cart(request, amount: int = 1, **fields) -> Product:
    """Put ``amount`` pieces of a new product with ``fields`` (price, weight, width, height, length) into the cart."""
    cart = cart_utils.get_cart(request) or cart_utils.create_cart(request)
    n = Product.objects.count()
    product = Product.objects.create(name=f"Product {n}", slug=f"product-{n}", active=True, **fields)
    CartItem.objects.create(cart=cart, product=product, amount=amount)
    return product


def holds(criterion, request, product=None) -> bool:
    """Evaluate ``criterion`` for ``request`` (and ``product``) the way the criteria of an object are evaluated."""
    criterion.request = request
    criterion.product = product
    return criterion.is_valid()


# The cart has a value of 500; for each operator, whether the criterion holds for 499, 500 and 501.
OPERATOR_CASES = [
    (EQ, [False, True, False]),
    (LT, [False, False, True]),
    (LTE, [False, True, True]),
    (GT, [True, False, False]),
    (GTE, [True, True, False]),
]


class TestNumberOperators:
    @pytest.mark.parametrize("operator,expected", OPERATOR_CASES)
    def test_cart_price_at_the_boundary(self, request_, method, operator, expected):
        add_to_cart(request_, price=500.0)

        results = [
            holds(CartPriceCriterion.objects.create(content=method, operator=operator, value=v), request_)
            for v in (499, 500, 501)
        ]

        assert results == expected

    @pytest.mark.parametrize("operator,expected", OPERATOR_CASES)
    def test_weight_at_the_boundary(self, request_, method, operator, expected):
        add_to_cart(request_, weight=500.0)

        results = [
            holds(WeightCriterion.objects.create(content=method, operator=operator, value=v), request_)
            for v in (499, 500, 501)
        ]

        assert results == expected


class TestCartAgainstProduct:
    def test_cart_price_is_the_cart_total(self, request_, method):
        add_to_cart(request_, price=300.0)
        add_to_cart(request_, price=100.0, amount=2)

        assert holds(CartPriceCriterion.objects.create(content=method, operator=EQ, value=500), request_)

    def test_with_a_product_its_own_price_counts(self, request_, method):
        add_to_cart(request_, price=1000.0)
        lamp = Product.objects.create(name="Lamp", slug="lamp", price=50.0, active=True)

        assert holds(CartPriceCriterion.objects.create(content=method, operator=EQ, value=50), request_, lamp)

    def test_an_empty_cart_is_worth_nothing(self, request_, method):
        assert holds(CartPriceCriterion.objects.create(content=method, operator=EQ, value=0), request_)

    def test_weight_and_height_add_up_over_amounts(self, request_, method):
        add_to_cart(request_, amount=3, weight=2.0, height=10.0)
        add_to_cart(request_, weight=4.0, height=5.0)

        assert holds(WeightCriterion.objects.create(content=method, operator=EQ, value=10), request_)
        assert holds(HeightCriterion.objects.create(content=method, operator=EQ, value=35), request_)

    def test_width_and_length_are_the_largest_item(self, request_, method):
        add_to_cart(request_, amount=3, width=20.0, length=30.0)
        add_to_cart(request_, width=40.0, length=10.0)

        assert holds(WidthCriterion.objects.create(content=method, operator=EQ, value=40), request_)
        assert holds(LengthCriterion.objects.create(content=method, operator=EQ, value=30), request_)

    def test_combined_length_and_girth_of_the_cart(self, request_, method):
        """2 × largest width + 2 × total height + largest length."""
        add_to_cart(request_, width=20.0, height=10.0, length=30.0)
        add_to_cart(request_, width=40.0, height=5.0, length=10.0)

        expected = 2 * 40 + 2 * (10 + 5) + 30
        assert holds(
            CombinedLengthAndGirthCriterion.objects.create(content=method, operator=EQ, value=expected), request_
        )

    def test_combined_length_and_girth_of_a_product(self, request_, method):
        lamp = Product.objects.create(name="Lamp", slug="lamp", width=20.0, height=10.0, length=30.0, active=True)

        criterion = CombinedLengthAndGirthCriterion.objects.create(
            content=method, operator=EQ, value=2 * 20 + 2 * 10 + 30
        )
        assert holds(criterion, request_, lamp)


class TestCountry:
    @pytest.fixture
    def countries(self, shop) -> tuple[Country, Country]:
        """The shop's default country and another one."""
        from lfs.core.utils import get_default_shop

        default = get_default_shop().get_default_country()
        other = Country.objects.exclude(pk=default.pk).first() or Country.objects.create(code="xx", name="Other")
        return default, other

    def test_without_a_choice_the_shops_default_country_counts(self, request_, method, countries):
        default, other = countries
        criterion = CountryCriterion.objects.create(content=method, operator=Criterion.IS_SELECTED)
        criterion.value.set([default])

        assert holds(criterion, request_)

    def test_the_country_of_the_customers_shipping_address_counts(self, request_, method, countries):
        default, other = countries
        customer = customer_utils.get_or_create_customer(request_)
        customer.selected_shipping_address.country = other
        customer.selected_shipping_address.save()
        criterion = CountryCriterion.objects.create(content=method, operator=Criterion.IS_SELECTED)
        criterion.value.set([default])

        assert not holds(criterion, request_)

    def test_is_not_selected_inverts(self, request_, method, countries):
        default, other = countries
        criterion = CountryCriterion.objects.create(content=method, operator=Criterion.IS_NOT_SELECTED)
        criterion.value.set([other])

        assert holds(criterion, request_)


class TestSelectedMethods:
    def test_selected_payment_method(self, request_, shop):
        invoice = PaymentMethod.objects.create(name="Invoice", active=True, priority=1)
        prepayment = PaymentMethod.objects.create(name="Prepayment", active=True, priority=2)
        discount_holder = ShippingMethod.objects.create(name="Standard", active=True)
        customer = customer_utils.get_or_create_customer(request_)
        customer.selected_payment_method = prepayment
        customer.save()

        selected = PaymentMethodCriterion.objects.create(content=discount_holder, operator=Criterion.IS_SELECTED)
        selected.value.set([prepayment])
        not_selected = PaymentMethodCriterion.objects.create(
            content=discount_holder, operator=Criterion.IS_NOT_SELECTED
        )
        not_selected.value.set([invoice])

        assert holds(selected, request_)
        assert holds(not_selected, request_)

    def test_selected_shipping_method(self, request_, shop):
        standard = ShippingMethod.objects.create(name="Standard", active=True, priority=1)
        express = ShippingMethod.objects.create(name="Express", active=True, priority=2)
        payment = PaymentMethod.objects.create(name="Cash on delivery", active=True)
        customer = customer_utils.get_or_create_customer(request_)
        customer.selected_shipping_method = express
        customer.save()

        criterion = ShippingMethodCriterion.objects.create(content=payment, operator=Criterion.IS_SELECTED)
        criterion.value.set([express])
        other = ShippingMethodCriterion.objects.create(content=payment, operator=Criterion.IS_SELECTED)
        other.value.set([standard])

        assert holds(criterion, request_)
        assert not holds(other, request_)

    def test_is_valid_and_is_not_valid_follow_the_criteria_of_the_named_method(self, request_, shop):
        """Cash on delivery only when express shipping is valid, which it is only above a cart of 100."""
        express = ShippingMethod.objects.create(name="Express", active=True)
        CartPriceCriterion.objects.create(content=express, operator=GT, value=100)
        cod = PaymentMethod.objects.create(name="Cash on delivery", active=True)
        valid = ShippingMethodCriterion.objects.create(content=cod, operator=Criterion.IS_VALID)
        valid.value.set([express])
        not_valid = ShippingMethodCriterion.objects.create(content=cod, operator=Criterion.IS_NOT_VALID)
        not_valid.value.set([express])

        add_to_cart(request_, price=50.0)
        assert (holds(valid, request_), holds(not_valid, request_)) == (False, True)

        cache.clear()
        add_to_cart(request_, price=80.0)
        assert (holds(valid, request_), holds(not_valid, request_)) == (True, False)


class TestSeveralCriteria:
    def test_an_object_applies_only_when_all_its_criteria_hold(self, request_, method):
        """Between 100 and 500: both bounds must hold."""
        CartPriceCriterion.objects.create(content=method, operator=GT, value=100, position=1)
        CartPriceCriterion.objects.create(content=method, operator=LT, value=500, position=2)

        add_to_cart(request_, price=50.0)
        assert not method.is_valid(request_)

        cache.clear()
        add_to_cart(request_, price=250.0)
        assert method.is_valid(request_)

        cache.clear()
        add_to_cart(request_, price=300.0)
        assert not method.is_valid(request_)
