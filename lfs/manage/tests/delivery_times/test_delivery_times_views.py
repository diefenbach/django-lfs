"""The delivery time management, tested through real requests as a shop manager: the start page, searching the
list, adding, saving and deleting a delivery time, and keeping the search query while doing so."""

from urllib.parse import parse_qs, urlparse

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from lfs.catalog.models import DeliveryTime
from lfs.catalog.settings import (
    DELIVERY_TIME_UNIT_DAYS,
    DELIVERY_TIME_UNIT_HOURS,
    DELIVERY_TIME_UNIT_MONTHS,
    DELIVERY_TIME_UNIT_WEEKS,
)

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def no_delivery_times(db):
    """Start without the delivery times other fixtures may have created."""
    DeliveryTime.objects.all().delete()


@pytest.fixture
def manager(client, admin_user):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def page(dt: DeliveryTime) -> str:
    """Return the URL of the delivery time's page."""
    return reverse("lfs_manage_delivery_time", kwargs={"pk": dt.pk})


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def listed(manager, dt: DeliveryTime, query: str) -> list[DeliveryTime]:
    """Return the delivery times listed beside ``dt``'s page for the search ``query``."""
    return list(manager.get(page(dt), {"q": query}).context["delivery_times"])


class TestStartPage:
    def test_opens_a_delivery_time(self, manager):
        dt = DeliveryTime.objects.create(min=1, max=3, unit=DELIVERY_TIME_UNIT_DAYS)

        assert manager.get(reverse("lfs_manage_delivery_times"))["Location"] == page(dt)

    def test_without_delivery_times_shows_the_empty_page(self, manager):
        response = manager.get(reverse("lfs_manage_delivery_times"))

        assert response["Location"] == reverse("lfs_no_delivery_times")


class TestSearch:
    @pytest.fixture
    def times(self) -> dict[str, DeliveryTime]:
        """One delivery time per unit, ordered by their minimum."""
        return {
            "hours": DeliveryTime.objects.create(min=24, max=48, unit=DELIVERY_TIME_UNIT_HOURS, description="Express"),
            "days": DeliveryTime.objects.create(min=1, max=3, unit=DELIVERY_TIME_UNIT_DAYS, description="Standard"),
            "weeks": DeliveryTime.objects.create(min=2, max=4, unit=DELIVERY_TIME_UNIT_WEEKS),
            "months": DeliveryTime.objects.create(min=3, max=6, unit=DELIVERY_TIME_UNIT_MONTHS),
        }

    def test_lists_all_by_minimum_without_a_search(self, manager, times):
        assert listed(manager, times["days"], "") == [times["days"], times["weeks"], times["months"], times["hours"]]

    def test_finds_by_description_case_insensitive(self, manager, times):
        assert listed(manager, times["days"], "express") == [times["hours"]]

    @pytest.mark.parametrize(
        "query,unit", [("Hours", "hours"), ("days", "days"), ("Wee", "weeks"), ("months", "months")]
    )
    def test_finds_by_unit_name_also_in_part(self, manager, times, query: str, unit: str):
        assert listed(manager, times["days"], query) == [times[unit]]

    def test_a_match_by_description_and_unit_is_listed_once(self, manager, times):
        times["days"].description = "Delivery in days"
        times["days"].save()

        assert listed(manager, times["days"], "days") == [times["days"]]

    def test_finds_nothing_for_an_unknown_term(self, manager, times):
        assert listed(manager, times["days"], "nonexistent") == []


class TestSaving:
    def test_stores_the_data_and_shows_a_message(self, manager):
        dt = DeliveryTime.objects.create(min=1, max=3, unit=DELIVERY_TIME_UNIT_DAYS)

        response = manager.post(
            page(dt), {"min": "2", "max": "4", "unit": str(DELIVERY_TIME_UNIT_WEEKS), "description": "Slow"}
        )

        dt.refresh_from_db()
        assert (dt.min, dt.max, dt.unit, dt.description) == (2, 4, DELIVERY_TIME_UNIT_WEEKS, "Slow")
        assert response["Location"] == page(dt)
        assert messages_of(response) == ["Delivery time has been saved."]

    def test_keeps_the_search_query(self, manager):
        dt = DeliveryTime.objects.create(min=1, max=3, unit=DELIVERY_TIME_UNIT_DAYS)

        response = manager.post(page(dt), {"min": "1", "max": "3", "unit": str(DELIVERY_TIME_UNIT_DAYS), "q": "std"})

        assert response["Location"] == page(dt) + "?q=std"

    def test_keeps_a_search_query_with_special_characters_intact(self, manager):
        dt = DeliveryTime.objects.create(min=1, max=3, unit=DELIVERY_TIME_UNIT_DAYS)

        response = manager.post(page(dt), {"min": "1", "max": "3", "unit": str(DELIVERY_TIME_UNIT_DAYS), "q": "1 & 2"})

        location = urlparse(response["Location"])
        assert (location.path, parse_qs(location.query)) == (page(dt), {"q": ["1 & 2"]})


class TestAdding:
    def test_adds_a_delivery_time_and_opens_it(self, manager):
        response = manager.post(
            reverse("lfs_manage_add_delivery_time"),
            {"create-min": "1", "create-max": "2", "create-unit": str(DELIVERY_TIME_UNIT_DAYS)},
        )

        dt = DeliveryTime.objects.get()
        assert (dt.min, dt.max, dt.unit) == (1, 2, DELIVERY_TIME_UNIT_DAYS)
        assert response["Location"] == page(dt)
        assert messages_of(response) == ["Delivery time has been added."]

    def test_keeps_the_search_query(self, manager):
        response = manager.post(
            reverse("lfs_manage_add_delivery_time"),
            {"create-min": "1", "create-max": "2", "create-unit": str(DELIVERY_TIME_UNIT_DAYS), "q": "std"},
        )

        assert response["Location"] == page(DeliveryTime.objects.get()) + "?q=std"

    def test_refuses_a_missing_unit(self, manager):
        response = manager.post(reverse("lfs_manage_add_delivery_time"), {"create-min": "1", "create-max": "2"})

        assert not DeliveryTime.objects.exists()
        assert "unit" in response.context["form"].errors


class TestDeleting:
    def test_confirmation_names_the_delivery_time(self, manager):
        dt = DeliveryTime.objects.create(min=1, max=3, unit=DELIVERY_TIME_UNIT_DAYS)

        response = manager.get(reverse("lfs_manage_delete_delivery_time_confirm", kwargs={"pk": dt.pk}))

        assert response.context["delivery_time"] == dt

    def test_confirmation_of_an_unknown_delivery_time_is_not_found(self, manager):
        response = manager.get(reverse("lfs_manage_delete_delivery_time_confirm", kwargs={"pk": 99999}))

        assert response.status_code == 404

    def test_opens_a_remaining_delivery_time(self, manager):
        deleted = DeliveryTime.objects.create(min=1, max=3, unit=DELIVERY_TIME_UNIT_DAYS)
        remaining = DeliveryTime.objects.create(min=2, max=3, unit=DELIVERY_TIME_UNIT_DAYS)

        response = manager.post(reverse("lfs_manage_delete_delivery_time", kwargs={"pk": deleted.pk}))

        assert list(DeliveryTime.objects.all()) == [remaining]
        assert response["Location"] == page(remaining)

    def test_deleting_the_last_one_shows_the_empty_page(self, manager):
        dt = DeliveryTime.objects.create(min=1, max=3, unit=DELIVERY_TIME_UNIT_DAYS)

        response = manager.post(reverse("lfs_manage_delete_delivery_time", kwargs={"pk": dt.pk}))

        assert response["Location"] == reverse("lfs_no_delivery_times")
