"""Date filters and counts of the management use the shop's day, not the UTC day. At 0:30 on 1 December in Berlin it
is still 30 November in UTC: "today" must mean 1 December, "this month" December and "this year" must not count the
orders of the previous month."""

import datetime

import pytest
from django.urls import reverse
from django.utils import timezone

from lfs.addresses.models import Address
from lfs.order.models import Order

pytestmark = pytest.mark.django_db

# 0:30 on 1 December 2026 in Berlin.
NOW = datetime.datetime(2026, 11, 30, 23, 30, tzinfo=datetime.timezone.utc)


@pytest.fixture(autouse=True)
def berlin_just_after_midnight(monkeypatch, settings):
    """Run the tests at 0:30 on 1 December in Berlin."""
    settings.TIME_ZONE = "Europe/Berlin"
    monkeypatch.setattr(timezone, "now", lambda: NOW)


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


EXPECTED_START = [("today", "2026-12-01"), ("week", "2026-11-25"), ("month", "2026-12-01")]


@pytest.mark.parametrize("filter_type,start", EXPECTED_START)
def test_predefined_order_filter_starts_on_the_shops_day(manager, filter_type: str, start: str):
    manager.get(reverse("lfs_manage_apply_predefined_order_filter", kwargs={"filter_type": filter_type}))

    assert manager.session["order-filters"]["start"] == start


@pytest.mark.parametrize("filter_type,start", EXPECTED_START)
def test_predefined_customer_filter_starts_on_the_shops_day(manager, filter_type: str, start: str):
    manager.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": filter_type}))

    assert manager.session["customer-filters"]["start"] == start


def test_dashboard_counts_the_orders_of_the_shops_month_and_year(manager):
    address = Address.objects.create()

    def order(at: datetime.datetime) -> None:
        o = Order.objects.create(invoice_address=address, shipping_address=address)
        Order.objects.filter(pk=o.pk).update(created=at)

    order(timezone.make_aware(datetime.datetime(2026, 12, 1, 0, 10)))  # this month
    order(timezone.make_aware(datetime.datetime(2026, 11, 30, 12, 0)))  # last month, this year
    order(timezone.make_aware(datetime.datetime(2025, 12, 31, 23, 50)))  # last year

    context = manager.get(reverse("lfs_manage_dashboard")).context

    assert (context["orders_this_month"], context["orders_this_year"]) == (1, 2)
