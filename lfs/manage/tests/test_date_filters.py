"""The date filters of the management interface (orders, carts, customers) work on calendar days in the shop's
time zone: a filter from day A to day B includes everything that happened on A and on B, at any local time."""

from datetime import datetime

import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from lfs.addresses.models import Address
from lfs.cart.models import Cart
from lfs.customer.models import Customer
from lfs.manage.carts.services import CartFilterService
from lfs.manage.customers.services import CustomerFilterService
from lfs.manage.orders.services import OrderFilterService
from lfs.order.models import Order

pytestmark = pytest.mark.django_db


def local(day: int, hour: int, minute: int = 0) -> datetime:
    """Return an aware datetime on 28.11.2026 + ``day`` at the given local time of the shop."""
    return timezone.make_aware(datetime(2026, 11, 28 + day, hour, minute))


def make_order(created: datetime, address: Address) -> Order:
    """Create an order and set its creation time (``created`` is set automatically on create)."""
    content_type = ContentType.objects.get_for_model(Address)
    order = Order.objects.create(
        sa_content_type=content_type, sa_object_id=address.id, ia_content_type=content_type, ia_object_id=address.id
    )
    Order.objects.filter(pk=order.pk).update(created=created)
    return order


def make_cart(modified: datetime) -> Cart:
    """Create a cart and set its modification time (``modification_date`` is set automatically on save)."""
    cart = Cart.objects.create(session=str(modified))
    Cart.objects.filter(pk=cart.pk).update(modification_date=modified)
    return cart


def make_customer(joined: datetime) -> Customer:
    """Create a customer whose user joined at ``joined``."""
    user = User.objects.create(username=str(joined), date_joined=joined)
    return Customer.objects.create(user=user)


@pytest.mark.parametrize("hour,minute", [(0, 30), (12, 0), (23, 30)])
def test_order_filter_for_one_day_includes_orders_of_that_day(hour: int, minute: int, address: Address):
    order = make_order(local(0, hour, minute), address)
    make_order(local(-1, 23, 30), address)
    make_order(local(1, 0, 30), address)

    result = OrderFilterService().filter_orders(Order.objects.all(), {"start": "2026-11-28", "end": "2026-11-28"})

    assert list(result) == [order]


@pytest.mark.parametrize("hour,minute", [(0, 30), (12, 0), (23, 30)])
def test_cart_filter_for_one_day_includes_carts_of_that_day(hour: int, minute: int):
    cart = make_cart(local(0, hour, minute))
    make_cart(local(-1, 23, 30))
    make_cart(local(1, 0, 30))

    result = CartFilterService().filter_carts(Cart.objects.all(), {"start": "2026-11-28", "end": "2026-11-28"})

    assert list(result) == [cart]


@pytest.mark.parametrize("hour,minute", [(0, 30), (12, 0), (23, 30)])
def test_customer_filter_for_one_day_includes_customers_who_joined_that_day(hour: int, minute: int):
    customer = make_customer(local(0, hour, minute))
    make_customer(local(-1, 23, 30))
    make_customer(local(1, 0, 30))

    result = CustomerFilterService().filter_customers(
        Customer.objects.all(), {"start": "2026-11-28", "end": "2026-11-28"}
    )

    assert list(result) == [customer]
