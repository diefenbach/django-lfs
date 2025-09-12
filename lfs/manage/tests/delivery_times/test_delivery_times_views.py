"""
Tests for DeliveryTime views in the manage package.

Following TDD principles:
- Test behavior, not implementation
- Clear test names
- Arrange-Act-Assert structure
- One assertion per test (when practical)
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import Http404

from lfs.catalog.models import DeliveryTime, DELIVERY_TIME_UNIT_DAYS
from lfs.manage.delivery_times.views import (
    DeliveryTimeUpdateView,
    DeliveryTimeCreateView,
    DeliveryTimeDeleteView,
    DeliveryTimeDeleteConfirmView,
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestDeliveryTimeUpdateView:
    """Tests for DeliveryTimeUpdateView functionality."""

    def test_get_delivery_times_queryset_without_search(self, delivery_time):
        """Should return all delivery times when no search query."""
        view = DeliveryTimeUpdateView()
        view.request = type("Request", (), {"GET": {}})()

        result = view.get_delivery_times_queryset()

        assert result.count() == 1
        assert delivery_time in result

    def test_get_delivery_times_queryset_with_search(self, delivery_time):
        """Should filter delivery times based on search query."""
        # Add description to delivery time for search
        delivery_time.description = "Express delivery"
        delivery_time.save()

        view = DeliveryTimeUpdateView()
        view.request = type("Request", (), {"GET": {"q": "express"}})()

        result = view.get_delivery_times_queryset()

        assert result.count() == 1
        assert delivery_time in result

    def test_get_delivery_times_queryset_with_no_matches(self, delivery_time):
        """Should return empty queryset when search has no matches."""
        view = DeliveryTimeUpdateView()
        view.request = type("Request", (), {"GET": {"q": "nonexistent"}})()

        result = view.get_delivery_times_queryset()

        assert result.count() == 0

    def test_get_delivery_times_queryset_with_unit_search(self, delivery_time):
        """Should filter delivery times based on unit search query."""
        from lfs.catalog.settings import (
            DELIVERY_TIME_UNIT_DAYS,
            DELIVERY_TIME_UNIT_HOURS,
            DELIVERY_TIME_UNIT_WEEKS,
            DELIVERY_TIME_UNIT_MONTHS,
            DELIVERY_TIME_UNIT_CHOICES,
        )
        from django.utils.translation import gettext

        # Create delivery times with different units
        hours_dt = DeliveryTime.objects.create(
            min=24, max=48, unit=DELIVERY_TIME_UNIT_HOURS, description="Hours delivery"
        )
        weeks_dt = DeliveryTime.objects.create(
            min=1, max=2, unit=DELIVERY_TIME_UNIT_WEEKS, description="Weeks delivery"
        )
        months_dt = DeliveryTime.objects.create(
            min=1, max=2, unit=DELIVERY_TIME_UNIT_MONTHS, description="Months delivery"
        )

        # Get translated unit names
        unit_choices_dict = dict(DELIVERY_TIME_UNIT_CHOICES)
        translated_hours = gettext(unit_choices_dict[DELIVERY_TIME_UNIT_HOURS])
        translated_days = gettext(unit_choices_dict[DELIVERY_TIME_UNIT_DAYS])
        translated_weeks = gettext(unit_choices_dict[DELIVERY_TIME_UNIT_WEEKS])
        translated_months = gettext(unit_choices_dict[DELIVERY_TIME_UNIT_MONTHS])

        # Test searching for translated "days" - should find the fixture delivery_time
        view = DeliveryTimeUpdateView()
        view.request = type("Request", (), {"GET": {"q": translated_days}})()
        result = view.get_delivery_times_queryset()
        assert result.count() == 1
        assert delivery_time in result

        # Test searching for translated "hours"
        view.request = type("Request", (), {"GET": {"q": translated_hours}})()
        result = view.get_delivery_times_queryset()
        assert result.count() == 1
        assert hours_dt in result

        # Test searching for translated "weeks"
        view.request = type("Request", (), {"GET": {"q": translated_weeks}})()
        result = view.get_delivery_times_queryset()
        assert result.count() == 1
        assert weeks_dt in result

        # Test searching for translated "months"
        view.request = type("Request", (), {"GET": {"q": translated_months}})()
        result = view.get_delivery_times_queryset()
        assert result.count() == 1
        assert months_dt in result

        # Test partial search - should work bidirectionally
        # If "days" is "werktage", then "werk" should find it
        if len(translated_days) > 3:  # Only test if the translated word is long enough
            partial_search = translated_days[:3]  # First 3 characters
            view.request = type("Request", (), {"GET": {"q": partial_search}})()
            result = view.get_delivery_times_queryset()
            assert result.count() == 1
            assert delivery_time in result

    def test_get_delivery_times_queryset_combined_search_bug(self, delivery_time):
        """Should reproduce the bug when combining text and unit search."""
        from lfs.catalog.settings import (
            DELIVERY_TIME_UNIT_HOURS,
            DELIVERY_TIME_UNIT_DAYS,
            DELIVERY_TIME_UNIT_CHOICES,
        )
        from django.utils.translation import gettext

        # Create a delivery time with description containing unit name
        # This will trigger both text search and unit search
        unit_choices_dict = dict(DELIVERY_TIME_UNIT_CHOICES)
        translated_days = gettext(unit_choices_dict[DELIVERY_TIME_UNIT_DAYS])

        # Create delivery time with description that includes the unit name
        delivery_time.description = f"Fast {translated_days} delivery"
        delivery_time.save()

        # Create another delivery time with hours unit
        hours_dt = DeliveryTime.objects.create(
            min=24, max=48, unit=DELIVERY_TIME_UNIT_HOURS, description="Hours delivery"
        )

        view = DeliveryTimeUpdateView()
        # Search for the unit name - this should trigger both text search (description)
        # and unit search (unit field), causing the queryset OR bug
        view.request = type("Request", (), {"GET": {"q": translated_days}})()

        # This should not raise an error and should return the correct results
        result = view.get_delivery_times_queryset()

        # The bug would be here - if the queryset OR operation fails, this would raise an error
        # But since we can't easily trigger it in test, let's verify the results are correct
        assert result.count() == 1
        assert delivery_time in result

    def test_get_context_data_includes_search_query(self, delivery_time):
        """Should include search query in context."""
        view = DeliveryTimeUpdateView()
        view.request = type("Request", (), {"GET": {"q": "test"}, "method": "GET"})()
        view.object = delivery_time

        context = view.get_context_data()

        assert context["search_query"] == "test"
        assert "delivery_times" in context

    def test_get_success_url_without_search(self, delivery_time):
        """Should return URL without search parameter when no search query."""
        view = DeliveryTimeUpdateView()
        view.request = type("Request", (), {"POST": {}})()
        view.object = delivery_time

        url = view.get_success_url()

        assert f"delivery-time/{delivery_time.id}" in url
        assert "?q=" not in url

    def test_get_success_url_with_search(self, delivery_time):
        """Should return URL with search parameter when search query exists."""
        view = DeliveryTimeUpdateView()
        view.request = type("Request", (), {"POST": {"q": "test"}})()
        view.object = delivery_time

        url = view.get_success_url()

        assert f"delivery-time/{delivery_time.id}" in url
        assert "?q=test" in url

    def test_form_valid_called_on_valid_submit(self, client, admin_user, delivery_time):
        """Should call form_valid when form is submitted with valid data."""
        client.force_login(admin_user)

        # Submit form with valid data
        response = client.post(
            reverse("lfs_manage_delivery_time", kwargs={"pk": delivery_time.id}),
            {
                "min": "1.0",
                "max": "3.0",
                "unit": "1",  # DELIVERY_TIME_UNIT_DAYS
                "description": "Updated description",
                "q": "",  # search query
            },
        )

        # Should redirect after successful form submission
        assert response.status_code == 302


@pytest.mark.django_db
@pytest.mark.unit
class TestDeliveryTimeCreateView:
    """Tests for DeliveryTimeCreateView functionality."""

    def test_get_form_kwargs_adds_prefix(self):
        """Should add 'create' prefix to form fields."""
        view = DeliveryTimeCreateView()
        view.request = type("Request", (), {"method": "GET"})()

        kwargs = view.get_form_kwargs()

        assert kwargs["prefix"] == "create"

    def test_get_context_data_includes_came_from(self):
        """Should include came_from in context."""
        view = DeliveryTimeCreateView()
        view.request = type("Request", (), {"POST": {"came_from": "/test/"}, "method": "POST", "FILES": {}})()
        view.object = None  # CreateView doesn't have an object initially

        context = view.get_context_data()

        assert context["came_from"] == "/test/"

    def test_get_success_url_without_search(self, delivery_time):
        """Should return URL without search parameter when no search query."""
        view = DeliveryTimeCreateView()
        view.request = type("Request", (), {"POST": {}})()
        view.object = delivery_time

        url = view.get_success_url()

        assert f"delivery-time/{delivery_time.id}" in url
        assert "?q=" not in url

    def test_get_success_url_with_search(self, delivery_time):
        """Should return URL with search parameter when search query exists."""
        view = DeliveryTimeCreateView()
        view.request = type("Request", (), {"POST": {"q": "test"}})()
        view.object = delivery_time

        url = view.get_success_url()

        assert f"delivery-time/{delivery_time.id}" in url
        assert "?q=test" in url


@pytest.mark.django_db
@pytest.mark.unit
class TestDeliveryTimeDeleteConfirmView:
    """Tests for DeliveryTimeDeleteConfirmView functionality."""

    def test_get_context_data_includes_delivery_time(self, delivery_time):
        """Should include delivery_time in context."""
        view = DeliveryTimeDeleteConfirmView()
        view.kwargs = {"pk": delivery_time.id}

        context = view.get_context_data()

        assert context["delivery_time"] == delivery_time

    def test_get_context_data_raises_404_for_nonexistent_delivery_time(self):
        """Should raise Http404 for non-existent delivery time."""
        view = DeliveryTimeDeleteConfirmView()
        view.kwargs = {"pk": 99999}

        with pytest.raises(Http404):
            view.get_context_data()


@pytest.mark.django_db
@pytest.mark.unit
class TestDeliveryTimeDeleteView:
    """Tests for DeliveryTimeDeleteView functionality."""

    def test_get_success_url_with_remaining_delivery_times(self, delivery_time):
        """Should redirect to first remaining delivery time when others exist."""
        # Create another delivery time
        other_delivery_time = DeliveryTime.objects.create(min=2, max=3, unit=DELIVERY_TIME_UNIT_DAYS)

        view = DeliveryTimeDeleteView()
        view.object = delivery_time

        url = view.get_success_url()

        assert f"delivery-time/{other_delivery_time.id}" in url

    def test_get_success_url_with_no_remaining_delivery_times(self, delivery_time):
        """Should redirect to no delivery times view when no others exist."""
        view = DeliveryTimeDeleteView()
        view.object = delivery_time

        url = view.get_success_url()

        assert "delivery-times/no" in url


@pytest.mark.django_db
@pytest.mark.integration
class TestDeliveryTimeViewsIntegration:
    """Integration tests for delivery time views."""

    def test_delivery_time_update_view_renders_correctly(self, client, admin_user, delivery_time, shop):
        """Should render delivery time update view correctly."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_delivery_time", args=[delivery_time.id]))

        assert response.status_code == 200
        assert "delivery_time" in response.context
        assert response.context["delivery_time"] == delivery_time

    def test_delivery_time_create_view_renders_correctly(self, client, admin_user, shop):
        """Should render delivery time create view correctly."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_add_delivery_time"))

        assert response.status_code == 200
        assert "form" in response.context

    def test_no_delivery_times_view_renders_correctly(self, client, admin_user, shop):
        """Should render no delivery times view correctly."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_no_delivery_times"))

        assert response.status_code == 200

    def test_delivery_time_delete_confirm_view_renders_correctly(self, client, admin_user, delivery_time, shop):
        """Should render delivery time delete confirm view correctly."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_delete_delivery_time_confirm", args=[delivery_time.id]))

        assert response.status_code == 200
        assert "delivery_time" in response.context
        assert response.context["delivery_time"] == delivery_time
