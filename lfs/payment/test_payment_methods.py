"""Which payment methods a customer can choose and what they cost, with real criteria, carts and customers: only
active methods whose criteria hold are offered, the first of them by priority is the default, a customer's own choice
wins while it stays valid, and the price comes from the first valid payment price or else the method itself."""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.core.management import call_command
from django.test import RequestFactory

from lfs.cart import utils as cart_utils
from lfs.cart.models import CartItem
from lfs.catalog.models import Product
from lfs.criteria.models import CartPriceCriterion
from lfs.customer import utils as customer_utils
from lfs.payment import utils as payment_utils
from lfs.payment.models import PaymentMethod, PaymentMethodPrice
from lfs.tax.models import Tax

LESS_THAN = CartPriceCriterion.LESS_THAN
GREATER_THAN = CartPriceCriterion.GREATER_THAN


@pytest.fixture(autouse=True)
def empty_cache():
    """Start every test with an empty cache: criteria are cached by the id of their object, and SQLite hands out
    the same ids again after a test's rollback."""
    from django.core.cache import cache

    cache.clear()


@pytest.fixture
def shop(db):
    """The default shop of LFS's fixture, without the payment methods it brings."""
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    PaymentMethod.objects.all().delete()


@pytest.fixture
def request_(shop):
    """A request of an anonymous visitor with a session."""
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    request.session = SessionStore()
    request.session.save()
    return request


def fill_cart(request, total: float) -> None:
    """Put one product costing ``total`` (gross) into the visitor's cart."""
    cart = cart_utils.get_cart(request) or cart_utils.create_cart(request)
    product = Product.objects.create(name=f"Product {total}", slug=f"product-{total}", price=total, active=True)
    CartItem.objects.create(cart=cart, product=product, amount=1)


def method(name: str, priority: int = 10, active: bool = True, **fields) -> PaymentMethod:
    """Create a payment method."""
    return PaymentMethod.objects.create(name=name, priority=priority, active=active, **fields)


class TestValidPaymentMethods:
    def test_offers_only_active_methods(self, request_):
        invoice = method("Invoice")
        method("Disabled", active=False)

        assert payment_utils.get_valid_payment_methods(request_) == [invoice]

    @pytest.mark.parametrize("cart_total,offered", [(100.0, True), (600.0, False)])
    def test_a_cart_price_criterion_decides(self, request_, cart_total: float, offered: bool):
        """Cash on delivery only for carts below 500."""
        invoice = method("Invoice", priority=1)
        cod = method("Cash on delivery", priority=2)
        CartPriceCriterion.objects.create(content=cod, operator=LESS_THAN, value=500)
        fill_cart(request_, cart_total)

        valid = payment_utils.get_valid_payment_methods(request_)

        assert valid == ([invoice, cod] if offered else [invoice])

    def test_no_methods_no_offer(self, request_):
        assert payment_utils.get_valid_payment_methods(request_) == []


class TestDefaultAndSelectedPaymentMethod:
    def test_default_is_the_first_valid_by_priority(self, request_):
        prepayment = method("Prepayment", priority=1)
        CartPriceCriterion.objects.create(content=prepayment, operator=GREATER_THAN, value=1000)
        invoice = method("Invoice", priority=2)
        method("Cash on delivery", priority=3)
        fill_cart(request_, 50.0)

        assert payment_utils.get_default_payment_method(request_) == invoice

    def test_no_valid_method_no_default(self, request_):
        method("Disabled", active=False)

        assert payment_utils.get_default_payment_method(request_) is None

    def test_the_customers_choice_wins_over_the_default(self, request_):
        method("Invoice", priority=1)
        prepayment = method("Prepayment", priority=2)
        customer = customer_utils.get_or_create_customer(request_)
        customer.selected_payment_method = prepayment
        customer.save()

        assert payment_utils.get_selected_payment_method(request_) == prepayment

    def test_without_a_choice_the_default_is_selected(self, request_):
        invoice = method("Invoice", priority=1)
        method("Prepayment", priority=2)

        assert payment_utils.get_selected_payment_method(request_) == invoice

    def test_a_choice_that_became_invalid_is_replaced_by_the_default(self, request_):
        invoice = method("Invoice", priority=1)
        cod = method("Cash on delivery", priority=2)
        CartPriceCriterion.objects.create(content=cod, operator=LESS_THAN, value=500)
        customer = customer_utils.get_or_create_customer(request_)
        customer.selected_payment_method = cod
        customer.save()
        fill_cart(request_, 600.0)

        payment_utils.update_to_valid_payment_method(request_, customer, save=True)

        customer.refresh_from_db()
        assert customer.selected_payment_method == invoice

    def test_a_valid_choice_is_kept(self, request_):
        method("Invoice", priority=1)
        cod = method("Cash on delivery", priority=2)
        customer = customer_utils.get_or_create_customer(request_)
        customer.selected_payment_method = cod
        customer.save()

        payment_utils.update_to_valid_payment_method(request_, customer, save=True)

        customer.refresh_from_db()
        assert customer.selected_payment_method == cod


class TestPaymentCosts:
    def test_the_methods_own_price_is_gross_and_split_by_its_tax(self, request_):
        cod = method("Cash on delivery", price=11.9, tax=Tax.objects.create(rate=19))

        costs = payment_utils.get_payment_costs(request_, cod)

        assert costs["price_gross"] == 11.9
        assert costs["tax"] == pytest.approx(1.9)
        assert costs["price_net"] == pytest.approx(10.0)

    def test_without_tax_the_whole_price_is_net(self, request_):
        cod = method("Cash on delivery", price=5.0)

        assert payment_utils.get_payment_costs(request_, cod) == {"price_net": 5.0, "tax": 0.0, "price_gross": 5.0}

    def test_the_first_valid_payment_price_replaces_the_methods_price(self, request_):
        """Cash on delivery costs 5, but 2 for carts above 100; a higher priority price that does not apply is
        skipped."""
        cod = method("Cash on delivery", price=5.0)
        never = PaymentMethodPrice.objects.create(payment_method=cod, price=0.0, priority=1, active=True)
        CartPriceCriterion.objects.create(content=never, operator=GREATER_THAN, value=10000)
        big_cart = PaymentMethodPrice.objects.create(payment_method=cod, price=2.0, priority=2, active=True)
        CartPriceCriterion.objects.create(content=big_cart, operator=GREATER_THAN, value=100)

        fill_cart(request_, 50.0)
        assert payment_utils.get_payment_costs(request_, cod)["price_gross"] == 5.0

        fill_cart(request_, 80.0)
        assert payment_utils.get_payment_costs(request_, cod)["price_gross"] == 2.0

    def test_no_method_costs_nothing(self, request_):
        assert payment_utils.get_payment_costs(request_, None) == {"price_net": 0.0, "tax": 0.0, "price_gross": 0.0}
