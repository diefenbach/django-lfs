"""The cart management, tested through real requests as a shop manager: the list of carts with their totals, items
and customers, a cart's page, the date filters (entered, predefined, reset) and deleting a cart."""

import datetime

import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from lfs.cart.models import Cart, CartItem
from lfs.catalog.models import Product
from lfs.customer.models import Customer

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def cart_with(*lines: tuple[str, float, int], session: str = "s1", user=None, modified=None) -> Cart:
    """Create a cart with lines of (product name, gross price, amount)."""
    cart = Cart.objects.create(session=session, user=user)
    for name, price, amount in lines:
        product = Product.objects.get_or_create(
            slug=name.lower(), defaults={"name": name, "price": price, "active": True}
        )[0]
        CartItem.objects.create(cart=cart, product=product, amount=amount)
    if modified:
        Cart.objects.filter(pk=cart.pk).update(modification_date=modified)
    return cart


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def set_filters(manager, **filters) -> None:
    """Store cart filters in the manager's session."""
    session = manager.session
    session["cart-filters"] = filters
    session.save()


class TestList:
    def test_shows_each_cart_with_total_items_and_products_newest_first(self, manager):
        older = cart_with(("Lamp", 40.0, 2), modified=timezone.now() - datetime.timedelta(days=1))
        newer = cart_with(("Chair", 100.0, 1), ("Lamp", 40.0, 1), session="s2")

        rows = manager.get(reverse("lfs_manage_carts")).context["carts_with_data"]

        assert [r["cart"] for r in rows] == [newer, older]
        assert (rows[0]["total"], rows[0]["item_count"], sorted(rows[0]["products"])) == (140.0, 2, ["Chair", "Lamp"])
        assert (rows[1]["total"], rows[1]["item_count"]) == (80.0, 2)

    def test_finds_the_customer_by_user_or_by_session(self, manager):
        user = User.objects.create_user("jane")
        by_user = Customer.objects.create(user=user)
        by_session = Customer.objects.create(session="anonymous")
        cart_with(("Lamp", 40.0, 1), user=user, session="")
        cart_with(("Lamp", 40.0, 1), session="anonymous")
        cart_with(("Lamp", 40.0, 1), session="nobody")

        rows = manager.get(reverse("lfs_manage_carts")).context["carts_with_data"]

        assert sorted(str(r["customer"] and r["customer"].pk) for r in rows) == sorted(
            [str(by_user.pk), str(by_session.pk), "None"]
        )

    def test_applies_the_stored_date_filter(self, manager):
        cart_with(("Lamp", 40.0, 1), modified=timezone.make_aware(datetime.datetime(2026, 11, 1, 12)))
        recent = cart_with(
            ("Lamp", 40.0, 1), session="s2", modified=timezone.make_aware(datetime.datetime(2026, 11, 20, 12))
        )
        set_filters(manager, start="2026-11-15")

        rows = manager.get(reverse("lfs_manage_carts")).context["carts_with_data"]

        assert [r["cart"] for r in rows] == [recent]

    def test_shows_50_carts_per_page(self, manager):
        for i in range(55):
            Cart.objects.create(session=f"s{i}")

        assert len(manager.get(reverse("lfs_manage_carts")).context["carts_with_data"]) == 50
        assert len(manager.get(reverse("lfs_manage_carts"), {"page": 2}).context["carts_with_data"]) == 5


class TestCartPage:
    def test_shows_the_carts_total_products_items_and_customer(self, manager):
        customer = Customer.objects.create(session="s1")
        cart = cart_with(("Chair", 100.0, 1), ("Lamp", 40.0, 2))

        context = manager.get(reverse("lfs_manage_cart", kwargs={"id": cart.id})).context

        assert context["cart_total"] == 180.0
        assert sorted(context["cart_products"].split(", ")) == ["Chair", "Lamp"]
        assert context["customer"] == customer
        assert [i.product.name for i in context["cart_items"]] == ["Chair", "Lamp"]

    def test_an_unknown_cart_is_not_found(self, manager):
        assert manager.get(reverse("lfs_manage_cart", kwargs={"id": 99999})).status_code == 404


class TestFilters:
    def test_entered_dates_are_stored_and_the_list_shown(self, manager):
        response = manager.post(
            reverse("lfs_manage_apply_cart_filters_list"), {"start": "2026-11-01", "end": "2026-11-30"}
        )

        assert manager.session["cart-filters"] == {"start": "2026-11-01", "end": "2026-11-30"}
        assert response["Location"] == reverse("lfs_manage_carts")
        assert messages_of(response) == ["Cart filters have been updated."]

    def test_an_emptied_date_is_removed_and_the_cart_shown(self, manager):
        cart = cart_with(("Lamp", 40.0, 1))
        set_filters(manager, start="2026-11-01", end="2026-11-30")

        response = manager.post(
            reverse("lfs_manage_apply_cart_filters", kwargs={"id": cart.id}), {"start": "", "end": "2026-11-30"}
        )

        assert manager.session["cart-filters"] == {"end": "2026-11-30"}
        assert response["Location"] == reverse("lfs_manage_cart", kwargs={"id": cart.id})

    def test_an_invalid_date_is_not_stored(self, manager):
        manager.post(reverse("lfs_manage_apply_cart_filters_list"), {"start": "not a date"})

        assert "cart-filters" not in manager.session

    def test_reset_clears_the_filters(self, manager):
        cart = cart_with(("Lamp", 40.0, 1))
        set_filters(manager, start="2026-11-01")

        response = manager.get(reverse("lfs_manage_reset_cart_filters"), {"cart_id": cart.id})

        assert "cart-filters" not in manager.session
        assert response["Location"] == reverse("lfs_manage_cart", kwargs={"id": cart.id})
        assert messages_of(response) == ["Cart filters have been reset."]

    @pytest.mark.parametrize(
        "filter_type,start", [("today", "2026-11-29"), ("week", "2026-11-23"), ("month", "2026-11-01")]
    )
    def test_a_predefined_filter_starts_on_the_shops_local_day(
        self, manager, monkeypatch, filter_type: str, start: str
    ):
        """At 0:30 on 29 November in Berlin it is still 28 November in UTC; "today" must mean the 29th."""
        monkeypatch.setattr(
            timezone, "now", lambda: datetime.datetime(2026, 11, 28, 23, 30, tzinfo=datetime.timezone.utc)
        )
        set_filters(manager, end="2026-12-31")

        response = manager.get(
            reverse("lfs_manage_apply_predefined_cart_filter_list", kwargs={"filter_type": filter_type})
        )

        assert manager.session["cart-filters"] == {"start": start}
        assert response["Location"] == reverse("lfs_manage_carts")

    def test_an_unknown_predefined_filter_is_refused(self, manager):
        response = manager.get(reverse("lfs_manage_apply_predefined_cart_filter_list", kwargs={"filter_type": "year"}))

        assert "cart-filters" not in manager.session
        assert messages_of(response) == ["Invalid filter type."]


class TestDeleting:
    def test_confirmation_names_the_cart(self, manager):
        cart = cart_with(("Lamp", 40.0, 1))

        assert manager.get(reverse("lfs_manage_delete_cart_confirm", kwargs={"id": cart.id})).context["cart"] == cart

    def test_deletes_the_cart_and_shows_the_list(self, manager):
        cart = cart_with(("Lamp", 40.0, 1))

        response = manager.post(reverse("lfs_manage_delete_cart", kwargs={"id": cart.id}))

        assert not Cart.objects.exists()
        assert response["Location"] == reverse("lfs_manage_carts")
        assert messages_of(response) == ["Cart has been deleted."]
