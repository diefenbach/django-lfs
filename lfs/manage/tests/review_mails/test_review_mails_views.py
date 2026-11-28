"""Rating mails of the management, tested through real requests as a shop manager: which orders get a mail, who
receives it and that a sent mail is not sent again.

The mail texts come from the theme; the tests use minimal templates of their own so that they test django-lfs."""

import datetime

import pytest
from django.contrib.messages import get_messages
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from lfs.addresses.models import Address
from lfs.catalog.models import Product
from lfs.core.utils import get_default_shop
from lfs.marketing.models import OrderRatingMail
from lfs.order.models import Order, OrderItem
from lfs.order.settings import CLOSED, SUBMITTED

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def rating_mail_templates(settings, tmp_path):
    """Minimal rating mail templates listing the products the mail asks to review."""
    folder = tmp_path / "lfs" / "reviews"
    folder.mkdir(parents=True)
    (folder / "rating_mail.txt").write_text("Please review your products.")
    (folder / "rating_mail.html").write_text("{% for item in order_items %}{{ item.product_name }};{% endfor %}")
    settings.TEMPLATES = [{**settings.TEMPLATES[0], "DIRS": [str(tmp_path), *settings.TEMPLATES[0]["DIRS"]]}]


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager; the shop sends from and notifies fixed addresses.

    Other test folders leave a shop of their own behind, so this configures the shop the mails actually use."""
    shop = get_default_shop()
    shop.from_email = "shop@example.com"
    shop.notification_emails = "owner@example.com, office@example.com"
    shop.save()
    client.force_login(admin_user)
    return client


def order(email: str, state: int = CLOSED, closed_days_ago: int = 20, products=()) -> Order:
    """Create an order of the given state whose state changed the given number of days ago."""
    address = Address.objects.create()
    o = Order.objects.create(invoice_address=address, shipping_address=address, customer_email=email, state=state)
    Order.objects.filter(pk=o.pk).update(state_modified=timezone.now() - datetime.timedelta(days=closed_days_ago))
    for product in products:
        OrderItem.objects.create(order=o, product=product, product_amount=1)
    return o


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def test_lists_orders_closed_for_two_weeks_without_a_rating_mail(manager):
    due = order("due@example.com")
    order("recent@example.com", closed_days_ago=3)
    order("open@example.com", state=SUBMITTED)
    OrderRatingMail.objects.create(order=order("asked@example.com"))

    response = manager.get(reverse("lfs_manage_rating_mails"))

    assert response.context["eligible_orders"] == [due]


def test_sends_each_due_customer_a_mail_and_marks_the_order(manager):
    first = order("first@example.com")
    second = order("second@example.com")

    response = manager.post(reverse("lfs_send_rating_mails"))

    assert sorted(m.to[0] for m in mail.outbox) == ["first@example.com", "second@example.com"]
    assert all(m.bcc == [] and m.from_email == "shop@example.com" for m in mail.outbox)
    assert set(OrderRatingMail.objects.values_list("order", flat=True)) == {first.pk, second.pk}
    assert messages_of(response) == ["Rating mails sent to 2 customers."]

    mail.outbox.clear()
    manager.post(reverse("lfs_send_rating_mails"))
    assert mail.outbox == []


def test_bcc_sends_a_copy_to_the_shops_notification_addresses(manager):
    order("customer@example.com")

    manager.post(reverse("lfs_send_rating_mails"), {"bcc": "on"})

    assert mail.outbox[0].bcc == ["owner@example.com", "office@example.com"]


def test_a_test_run_mails_the_shop_and_marks_nothing(manager):
    order("customer@example.com")

    response = manager.post(reverse("lfs_send_rating_mails"), {"test": "on"})

    assert [m.to for m in mail.outbox] == [["owner@example.com", "office@example.com"]]
    assert not OrderRatingMail.objects.exists()
    assert messages_of(response) == ["Test mails sent to shop notification emails."]


def test_the_mail_asks_for_the_parent_of_a_bought_variant(manager):
    lamp = Product.objects.create(name="Lamp", slug="lamp", sub_type="1")
    red_lamp = Product.objects.create(name="Red lamp", slug="red-lamp", sub_type="2", parent=lamp)
    order("customer@example.com", products=[red_lamp])

    manager.post(reverse("lfs_send_rating_mails"))

    assert mail.outbox[0].alternatives[0][0] == "Lamp;"
