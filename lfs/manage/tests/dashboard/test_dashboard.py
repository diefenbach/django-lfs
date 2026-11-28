"""The dashboard of the management, tested through a real request as a shop manager: the counts of products,
categories and orders, the orders still due for a rating mail, and the best selling product. Which day "this month"
starts on is tested in lfs/manage/tests/test_local_day.py."""

import datetime

import pytest
from django.urls import reverse
from django.utils import timezone

from lfs.addresses.models import Address
from lfs.catalog.models import Category, Product
from lfs.marketing.models import OrderRatingMail
from lfs.order.models import Order, OrderItem
from lfs.order.settings import CLOSED, SUBMITTED

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def dashboard(manager) -> dict:
    return manager.get(reverse("lfs_manage_dashboard")).context


def order(state: int = SUBMITTED, closed_days_ago: int = 0, items=()) -> Order:
    address = Address.objects.create()
    o = Order.objects.create(invoice_address=address, shipping_address=address, state=state)
    Order.objects.filter(pk=o.pk).update(state_modified=timezone.now() - datetime.timedelta(days=closed_days_ago))
    for product, amount in items:
        OrderItem.objects.create(order=o, product=product, product_amount=amount)
    return o


def test_counts_products_categories_and_orders(manager):
    Product.objects.create(name="Lamp", slug="lamp", active=True)
    Product.objects.create(name="Chair", slug="chair", active=False)
    Category.objects.create(name="Lights", slug="lights")
    Category.objects.create(name="Hidden", slug="hidden", exclude_from_navigation=True)
    order()

    context = dashboard(manager)

    assert (context["total_products"], context["active_products"], context["inactive_products"]) == (2, 1, 1)
    assert (context["total_categories"], context["visible_categories"], context["hidden_categories"]) == (2, 1, 1)
    assert (context["total_orders"], context["orders_this_month"], context["orders_this_year"]) == (1, 1, 1)


def test_counts_the_orders_due_for_a_rating_mail(manager):
    due = order(CLOSED, closed_days_ago=20)
    order(CLOSED, closed_days_ago=20)
    OrderRatingMail.objects.create(order=due)
    # Mails sent for orders that are no longer due must not be subtracted.
    OrderRatingMail.objects.create(order=order(CLOSED, closed_days_ago=3))
    OrderRatingMail.objects.create(order=order(SUBMITTED))

    assert dashboard(manager)["eligible_rating_mails"] == 1


def test_shows_the_product_sold_most_often(manager):
    lamp = Product.objects.create(name="Lamp", slug="lamp")
    chair = Product.objects.create(name="Chair", slug="chair")
    order(items=[(lamp, 2), (chair, 1)])
    order(items=[(chair, 3)])

    context = dashboard(manager)

    assert (context["best_selling_product"], context["best_selling_count"]) == (chair, 4)


def test_without_orders_shows_no_best_seller(manager):
    context = dashboard(manager)

    assert (context["best_selling_product"], context["best_selling_count"], context["eligible_rating_mails"]) == (
        None,
        0,
        0,
    )
