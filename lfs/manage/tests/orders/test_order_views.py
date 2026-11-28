"""The order management, tested through real requests as a shop manager: the list with its filters and paging, an
order's page, changing its state (which mails the customer when it is paid or sent), resending it, and deleting.
Which day the predefined date filters start on is tested in lfs/manage/tests/test_local_day.py."""

import datetime

import pytest
from django.contrib.messages import get_messages
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from lfs.addresses.models import Address
from lfs.catalog.models import Product
from lfs.core.utils import get_default_shop
from lfs.order.models import Order, OrderItem
from lfs.order.settings import CANCELED, PAID, SENT, SUBMITTED
from lfs.payment.models import PaymentMethod

pytestmark = pytest.mark.django_db

LIST = reverse("lfs_manage_orders")


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager; the shop mails from and notifies fixed addresses."""
    default = get_default_shop()
    default.from_email, default.notification_emails = "shop@example.com", "owner@example.com"
    default.save()
    client.force_login(admin_user)
    return client


def order(firstname: str = "Jane", lastname: str = "Doe", state: int = SUBMITTED, created=None, **kwargs) -> Order:
    address = Address.objects.create()
    o = Order.objects.create(
        invoice_address=address,
        shipping_address=address,
        customer_firstname=firstname,
        customer_lastname=lastname,
        customer_email=f"{firstname.lower()}@example.com",
        state=state,
        price=kwargs.pop("price", 10.0),
        **kwargs,
    )
    if created:
        Order.objects.filter(pk=o.pk).update(created=created)
    return o


def at(day: int) -> datetime.datetime:
    """Noon of the given day of November 2026 in the shop's time zone."""
    return timezone.make_aware(datetime.datetime(2026, 11, day, 12))


def listed(manager, **params) -> list[str]:
    """Return the customers' first names in the order the list shows the orders."""
    return [row["order"].customer_firstname for row in manager.get(LIST, params).context["orders_with_data"]]


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


class TestList:
    def test_shows_each_order_newest_first_with_its_total_items_and_products(self, manager):
        older = order("Anna", created=at(1), price=50.0)
        order("Bob", created=at(2))
        lamp = Product.objects.create(name="Lamp", slug="lamp")
        OrderItem.objects.create(order=older, product=lamp, product_amount=2)
        OrderItem.objects.create(order=older, product=None, product_name="Deleted", product_amount=1)

        rows = manager.get(LIST).context["orders_with_data"]

        assert [r["order"].customer_firstname for r in rows] == ["Bob", "Anna"]
        assert (rows[1]["total"], rows[1]["item_count"], rows[1]["products"]) == (50.0, 3, ["Lamp"])
        assert (rows[1]["customer_name"], rows[1]["state_name"]) == ("Anna Doe", "Submitted")

    def test_filters_by_name_state_payment_method_and_days(self, manager):
        invoice = PaymentMethod.objects.create(name="Invoice")
        order("Anna", state=PAID, payment_method=invoice, created=at(10))
        order("Annabel", state=PAID, payment_method=invoice, created=at(20))
        order("Anne", state=SUBMITTED, payment_method=invoice, created=at(10))
        order("Bob", lastname="Annex", state=PAID, created=at(10))

        response = manager.post(
            reverse("lfs_manage_set_order_filter"),
            {"name": "ann", "state": PAID, "payment_method": invoice.id, "start": "09.11.2026", "end": "2026-11-11"},
        )

        assert manager.session["order-filters"] == {
            "name": "ann",
            "state": str(PAID),
            "payment_method": str(invoice.id),
            "start": "2026-11-09",
            "end": "2026-11-11",
        }
        assert response["Location"] == LIST
        assert messages_of(response) == ["Order filters have been updated."]
        assert listed(manager) == ["Anna"]

    def test_the_name_filter_also_finds_the_last_name(self, manager):
        order("Bob", lastname="Annex")
        order("Carl")
        manager.post(reverse("lfs_manage_set_order_filter"), {"name": "annex"})

        assert listed(manager) == ["Bob"]

    def test_an_emptied_filter_is_removed_and_the_order_shown(self, manager):
        jane = order()
        manager.post(reverse("lfs_manage_set_order_filter"), {"name": "ann", "start": "2026-11-01"})

        response = manager.post(reverse("lfs_manage_set_order_filter"), {"name": "", "order-id": jane.id})

        assert manager.session["order-filters"] == {}
        assert response["Location"] == reverse("lfs_manage_order", kwargs={"order_id": jane.id})

    def test_an_invalid_date_keeps_the_filters(self, manager):
        manager.post(reverse("lfs_manage_set_order_filter"), {"name": "ann"})

        response = manager.post(reverse("lfs_manage_set_order_filter"), {"name": "bob", "start": "someday"})

        assert manager.session["order-filters"] == {"name": "ann"}
        assert messages_of(response)[-1] == "Invalid filter input. Please check the date fields."

    def test_reset_clears_the_filters(self, manager):
        jane = order()
        manager.post(reverse("lfs_manage_set_order_filter"), {"name": "ann"})

        response = manager.get(reverse("lfs_manage_reset_order_filters"), {"order_id": jane.id})

        assert "order-filters" not in manager.session
        assert response["Location"] == reverse("lfs_manage_order", kwargs={"order_id": jane.id})

    def test_a_predefined_filter_drops_the_end_day_and_an_unknown_one_is_refused(self, manager):
        manager.post(reverse("lfs_manage_set_order_filter"), {"end": "2026-11-11"})

        manager.get(reverse("lfs_manage_apply_predefined_order_filter", kwargs={"filter_type": "month"}))
        assert set(manager.session["order-filters"]) == {"start"}

        response = manager.get(reverse("lfs_manage_apply_predefined_order_filter", kwargs={"filter_type": "year"}))
        assert messages_of(response)[-1] == "Invalid filter type."

    def test_shows_50_orders_per_page(self, manager):
        for i in range(52):
            order(f"Customer{i}")

        assert len(listed(manager)) == 50
        assert len(listed(manager, page=2)) == 2


class TestOrder:
    def test_shows_the_order_with_its_items_and_the_filtered_orders_beside_it(self, manager):
        jane = order("Jane", price=42.0)
        order("Bob")
        OrderItem.objects.create(order=jane, product=Product.objects.create(name="Lamp", slug="lamp"), product_amount=1)
        manager.post(
            reverse("lfs_manage_set_order_filter"), {"name": "jane", "start": "2000-01-01", "end": "2999-12-31"}
        )

        context = manager.get(reverse("lfs_manage_order", kwargs={"order_id": jane.id})).context

        assert (context["current_order"], context["order_total"], context["order_products"]) == (jane, 42.0, "Lamp")
        assert context["customer_name"] == "Jane Doe"
        assert list(context["orders_page"]) == [jane]
        assert [s["id"] for s in context["states"] if s["selected_order"]] == [SUBMITTED]
        assert (context["filter_form"].initial["start"], context["filter_form"].initial["end"]) == (
            datetime.date(2000, 1, 1),
            datetime.date(2999, 12, 31),
        )

    def test_an_unknown_order_is_not_found(self, manager):
        assert manager.get(reverse("lfs_manage_order", kwargs={"order_id": 99999})).status_code == 404


class TestState:
    def change(self, manager, o: Order, state) -> object:
        return manager.post(reverse("lfs_manage_change_order_state"), {"order-id": o.id, "new-state": state})

    def test_changes_the_state_and_its_date(self, manager):
        jane = order(state=SUBMITTED)
        Order.objects.filter(pk=jane.pk).update(state_modified=at(1))

        response = self.change(manager, jane, CANCELED)

        jane.refresh_from_db()
        assert jane.state == CANCELED and jane.state_modified > at(1)
        assert response["Location"] == reverse("lfs_manage_order", kwargs={"order_id": jane.id})
        assert messages_of(response) == ["Order state has been changed"]
        assert mail.outbox == []

    @pytest.mark.parametrize("state", [PAID, SENT])
    def test_paid_and_sent_mail_the_customer(self, manager, state: int):
        jane = order(state=SUBMITTED)

        self.change(manager, jane, state)

        assert [m.to for m in mail.outbox] == [["jane@example.com"]]

    def test_the_order_page_shows_the_new_state_at_once(self, manager):
        """The order is cached; changing its state must not leave the old one on the page."""
        jane = order(state=SUBMITTED)
        url = reverse("lfs_manage_order", kwargs={"order_id": jane.id})
        manager.get(url)

        self.change(manager, jane, CANCELED)

        assert manager.get(url).context["current_order"].state == CANCELED

    def test_a_state_that_is_not_a_number_is_refused(self, manager):
        jane = order(state=SUBMITTED)

        response = self.change(manager, jane, "paid")

        assert Order.objects.get(pk=jane.pk).state == SUBMITTED
        assert messages_of(response) == ["Invalid state selected."]


class TestSendAndDelete:
    def test_confirmation_names_the_order(self, manager):
        jane = order()

        assert (
            manager.get(reverse("lfs_manage_delete_order_confirm", kwargs={"order_id": jane.id})).context["order"]
            == jane
        )

    def test_deletes_the_order(self, manager):
        jane = order()

        response = manager.post(reverse("lfs_manage_delete_order", kwargs={"order_id": jane.id}))

        assert not Order.objects.exists()
        assert response["Location"] == LIST
        assert messages_of(response) == ["Order has been deleted."]
