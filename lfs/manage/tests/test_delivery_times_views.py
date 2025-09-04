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

        assert "no-delivery-times" in url


@pytest.mark.django_db
@pytest.mark.integration
class TestDeliveryTimeViewsIntegration:
    """Integration tests for delivery time views."""

    def test_delivery_time_update_view_renders_correctly(self, client, manage_user, delivery_time, shop):
        """Should render delivery time update view correctly."""
        client.force_login(manage_user)

        response = client.get(reverse("lfs_manage_delivery_time", args=[delivery_time.id]))

        assert response.status_code == 200
        assert "delivery_time" in response.context
        assert response.context["delivery_time"] == delivery_time

    def test_delivery_time_create_view_renders_correctly(self, client, manage_user, shop):
        """Should render delivery time create view correctly."""
        client.force_login(manage_user)

        response = client.get(reverse("lfs_manage_add_delivery_time"))

        assert response.status_code == 200
        assert "form" in response.context

    def test_no_delivery_times_view_renders_correctly(self, client, manage_user, shop):
        """Should render no delivery times view correctly."""
        client.force_login(manage_user)

        response = client.get(reverse("lfs_no_delivery_times"))

        assert response.status_code == 200

    def test_delivery_time_delete_confirm_view_renders_correctly(self, client, manage_user, delivery_time, shop):
        """Should render delivery time delete confirm view correctly."""
        client.force_login(manage_user)

        response = client.get(reverse("lfs_manage_delete_delivery_time_confirm", args=[delivery_time.id]))

        assert response.status_code == 200
        assert "delivery_time" in response.context
        assert response.context["delivery_time"] == delivery_time
