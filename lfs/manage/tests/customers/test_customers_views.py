"""The customer management, tested through real requests as a shop manager: the list with its filters, ordering
and paging, and a customer's page with orders, cart and addresses. Which day the predefined date filters start on is
tested in lfs/manage/tests/test_local_day.py."""

import datetime

import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from lfs.addresses.models import Address
from lfs.cart.models import Cart, CartItem
from lfs.catalog.models import Product
from lfs.customer.models import Customer
from lfs.order.models import Order

pytestmark = pytest.mark.django_db

LIST = reverse("lfs_manage_customers")


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def customer(firstname: str, lastname: str = "Doe", joined=None, email=None, session: str = "") -> Customer:
    """A registered customer with an address."""
    user = User.objects.create_user(firstname.lower(), email=email or f"{firstname.lower()}@example.com")
    if joined:
        User.objects.filter(pk=user.pk).update(date_joined=joined)
    c = Customer.objects.create(user=user, session=session)
    address = Address.objects.create(customer=c, firstname=firstname, lastname=lastname)
    c.selected_invoice_address = c.selected_shipping_address = address
    c.save()
    return c


def order_of(c: Customer, session: str = "") -> Order:
    address = Address.objects.create()
    return Order.objects.create(user=c.user, session=session, invoice_address=address, shipping_address=address)


def at(day: int) -> datetime.datetime:
    """Noon of the given day of November 2026 in the shop's time zone."""
    return timezone.make_aware(datetime.datetime(2026, 11, day, 12))


def listed(manager, **params) -> list[str]:
    """Return the customers' user names in the order the list shows them."""
    return [row["customer"].user.username for row in manager.get(LIST, params).context["customers_with_data"]]


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


class TestList:
    def test_shows_each_customer_with_orders_and_cart(self, manager):
        anna = customer("Anna")
        order_of(anna)
        order_of(anna)
        cart = Cart.objects.create(user=anna.user)
        CartItem.objects.create(
            cart=cart, product=Product.objects.create(name="Lamp", slug="lamp", price=20, active=True), amount=2
        )

        row = manager.get(LIST).context["customers_with_data"][0]

        assert (row["customer"], row["orders_count"], row["cart_price"]) == (anna, 2, 40.0)

    def test_a_registered_customer_shows_the_orders_of_all_sessions(self, manager):
        """After registering, the customer keeps the session it started with; later orders have other sessions."""
        anna = customer("Anna", session="first-visit")
        order_of(anna, session="first-visit")
        order_of(anna, session="a-later-visit")

        assert manager.get(LIST).context["customers_with_data"][0]["orders_count"] == 2
        page = manager.get(reverse("lfs_manage_customer", kwargs={"customer_id": anna.id}))
        assert len(page.context["orders"]) == 2

    def test_filters_by_address_name_and_registration_days(self, manager):
        customer("Anna", joined=at(10))
        customer("Annabel", joined=at(20))
        customer("Bob", lastname="Annex", joined=at(10))
        customer("Carl", joined=at(10))

        response = manager.post(
            reverse("lfs_apply_customer_filters_list"), {"name": "ann", "start": "2026-11-09", "end": "2026-11-11"}
        )

        assert manager.session["customer-filters"] == {"name": "ann", "start": "2026-11-09", "end": "2026-11-11"}
        assert response["Location"] == LIST
        assert messages_of(response) == ["Customer filters have been updated."]
        assert sorted(listed(manager)) == ["anna", "bob"]

    def test_an_emptied_filter_is_removed_and_reset_clears_all(self, manager):
        anna = customer("Anna")
        manager.post(reverse("lfs_apply_customer_filters_list"), {"name": "ann", "start": "2026-11-09"})

        manager.post(reverse("lfs_apply_customer_filters_list"), {"name": "ann"})
        assert manager.session["customer-filters"] == {"name": "ann"}

        response = manager.get(reverse("lfs_reset_customer_filters"), {"customer_id": anna.id})
        assert "customer-filters" not in manager.session
        assert response["Location"] == reverse("lfs_manage_customer", kwargs={"customer_id": anna.id})

    def test_ordering_by_a_column_and_again_reverses_it(self, manager):
        customer("Bob", lastname="Smith", email="b@example.com")
        customer("Anna", lastname="Young", email="c@example.com")
        customer("Carl", lastname="Adams", email="a@example.com")

        manager.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "lastname"}))
        by_lastname = listed(manager)
        manager.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "lastname"}))
        by_lastname_reversed = listed(manager)
        manager.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "email"}))
        by_email = listed(manager)

        assert by_lastname == ["carl", "bob", "anna"]
        assert by_lastname_reversed == ["anna", "bob", "carl"]
        assert by_email == ["carl", "bob", "anna"]

    def test_shows_30_customers_per_page(self, manager):
        for i in range(32):
            customer(f"Customer{i}")

        assert len(listed(manager)) == 30
        assert len(listed(manager, page=2)) == 2


class TestCustomer:
    def test_shows_orders_cart_and_addresses(self, manager):
        anna = customer("Anna", lastname="Smith")
        first = order_of(anna)
        Cart.objects.create(user=anna.user)

        context = manager.get(reverse("lfs_manage_customer", kwargs={"customer_id": anna.id})).context

        assert context["customer"] == anna
        assert list(context["orders"]) == [first]
        assert context["cart"].user == anna.user
        assert "Smith" in context["invoice_address"] and "Smith" in context["shipping_address"]

    def test_an_unknown_customer_is_not_found(self, manager):
        assert manager.get(reverse("lfs_manage_customer", kwargs={"customer_id": 99999})).status_code == 404

    def test_a_predefined_filter_returns_to_the_customer(self, manager):
        anna = customer("Anna")

        response = manager.get(
            reverse("lfs_apply_predefined_customer_filter", kwargs={"customer_id": anna.id, "filter_type": "week"})
        )

        assert set(manager.session["customer-filters"]) == {"start"}
        assert response["Location"] == reverse("lfs_manage_customer", kwargs={"customer_id": anna.id})


def test_an_unknown_ordering_is_ignored(manager):
    """The ordering comes from the URL and is kept in the session; an unknown one must not break the pages."""
    anna = customer("Anna")

    manager.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "no_such_field"}))

    assert listed(manager) == ["anna"]
    assert manager.get(reverse("lfs_manage_customer", kwargs={"customer_id": anna.id})).status_code == 200
