"""
Comprehensive unit tests for property service-like functionality.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- Property creation and management logic
- Property position updating
- Property type change handling
- Business logic validation
"""

import pytest
from unittest.mock import patch

from lfs.catalog.models import Property
from lfs.catalog.settings import PROPERTY_TEXT_FIELD, PROPERTY_NUMBER_FIELD
from lfs.manage.properties.views import PropertyDataView, PropertyCreateView


class TestPropertyDataViewServices:
    """Test PropertyDataView service-like methods."""

    @pytest.mark.django_db
    def test_get_success_url_returns_correct_url(self, mock_request_with_user, admin_user):
        """Test that get_success_url returns the correct URL."""
        property_obj = Property.objects.create(name="Test Property", title="Test Property")
        view = PropertyDataView()
        view.request = mock_request_with_user
        view.object = property_obj

        url = view.get_success_url()

        assert f"/manage/property/{property_obj.id}" in url

    @pytest.mark.django_db
    def test_form_valid_saves_property_with_success_message(self, mock_request_with_user, admin_user):
        """Test that form_valid saves the property and shows success message."""
        property_obj = Property.objects.create(name="Test Property", title="Test Property")
        view = PropertyDataView()
        view.request = mock_request_with_user
        view.object = property_obj
        view.kwargs = {"id": property_obj.id}

        class DummyForm:
            def __init__(self):
                self.cleaned_data = {}

            def save(self, commit=True):
                return property_obj

        dummy_form = DummyForm()

        with patch("lfs.manage.properties.views.messages.success") as mock_messages, patch.object(
            view, "get_success_url", return_value="/success/"
        ), patch("lfs.manage.properties.views.invalidate_cache_group_id") as mock_invalidate, patch.object(
            view, "_update_property_positions"
        ) as mock_update_positions:

            response = view.form_valid(dummy_form)

            mock_messages.assert_called_once()
            mock_invalidate.assert_called_once_with("global-properties-version")
            mock_update_positions.assert_called_once()
            assert response is not None

    @pytest.mark.django_db
    def test_form_valid_sends_signal_when_type_changes(self, mock_request_with_user, admin_user):
        """Test that form_valid sends signal when property type changes."""
        property_obj = Property.objects.create(name="Test Property", title="Test Property", type=PROPERTY_TEXT_FIELD)
        view = PropertyDataView()
        view.request = mock_request_with_user
        view.object = property_obj
        view.kwargs = {"id": property_obj.id}

        class DummyForm:
            def __init__(self):
                self.cleaned_data = {}

            def save(self, commit=True):
                # Simulate type change
                property_obj.type = PROPERTY_NUMBER_FIELD
                property_obj.save()
                return property_obj

        dummy_form = DummyForm()

        with patch("lfs.manage.properties.views.property_type_changed.send") as mock_send, patch(
            "lfs.manage.properties.views.messages.success"
        ), patch.object(view, "get_success_url", return_value="/success/"), patch(
            "lfs.manage.properties.views.invalidate_cache_group_id"
        ), patch.object(
            view, "_update_property_positions"
        ):

            response = view.form_valid(dummy_form)

            mock_send.assert_called_once_with(property_obj)

    @pytest.mark.django_db
    def test_form_valid_does_not_send_signal_when_type_unchanged(self, mock_request_with_user, admin_user):
        """Test that form_valid does not send signal when property type doesn't change."""
        original_type = PROPERTY_TEXT_FIELD
        property_obj = Property.objects.create(name="Test Property", title="Test Property", type=original_type)
        view = PropertyDataView()
        view.request = mock_request_with_user
        view.object = property_obj
        view.kwargs = {"id": property_obj.id}

        class DummyForm:
            def __init__(self):
                self.cleaned_data = {}

            def save(self, commit=True):
                # Type remains the same
                return property_obj

        dummy_form = DummyForm()

        with patch("lfs.manage.properties.views.property_type_changed.send") as mock_send, patch(
            "lfs.manage.properties.views.messages.success"
        ), patch.object(view, "get_success_url", return_value="/success/"), patch(
            "lfs.manage.properties.views.invalidate_cache_group_id"
        ), patch.object(
            view, "_update_property_positions"
        ):

            response = view.form_valid(dummy_form)

            mock_send.assert_not_called()

    @pytest.mark.django_db
    def test_update_property_positions_sets_correct_positions(self, mock_request_with_user, admin_user):
        """Test that _update_property_positions sets correct position values."""
        # Create properties with various positions
        prop1 = Property.objects.create(name="Property A", title="Property A", local=False)
        prop2 = Property.objects.create(name="Property B", title="Property B", local=False)
        prop3 = Property.objects.create(name="Property C", title="Property C", local=False)
        # Create a local property that should be excluded
        Property.objects.create(name="Local Property", title="Local Property", local=True)

        view = PropertyDataView()
        view.request = mock_request_with_user
        view._update_property_positions()

        # Refresh from database
        prop1.refresh_from_db()
        prop2.refresh_from_db()
        prop3.refresh_from_db()

        # Check positions are set correctly (10, 20, 30, etc.)
        assert prop1.position == 10
        assert prop2.position == 20
        assert prop3.position == 30


class TestPropertyCreateViewServices:
    """Test PropertyCreateView service-like methods."""

    @pytest.mark.django_db
    def test_get_success_url_returns_correct_url(self, mock_request_with_user, admin_user):
        """Test that get_success_url returns the correct URL."""
        property_obj = Property.objects.create(name="Test Property", title="Test Property")
        view = PropertyCreateView()
        view.request = mock_request_with_user
        view.object = property_obj

        url = view.get_success_url()

        assert f"/manage/property/{property_obj.id}" in url

    @pytest.mark.django_db
    def test_form_valid_sets_default_values(self, mock_request_with_user, admin_user):
        """Test that form_valid sets default values for new property."""
        view = PropertyCreateView()
        view.request = mock_request_with_user

        class DummyForm:
            def __init__(self):
                self.cleaned_data = {}

            def save(self, commit=True):
                return Property.objects.create(name="New Property")

        dummy_form = DummyForm()

        with patch.object(view, "get_success_url", return_value="/success/"), patch(
            "lfs.manage.properties.views.messages.success"
        ):

            response = view.form_valid(dummy_form)

            # Check that the property was created with default values
            created_property = Property.objects.get(name="New Property")
            assert created_property.position == 10  # Position is recalculated by _update_property_positions
            assert created_property.title == "New Property"  # Should match name initially

    @pytest.mark.django_db
    def test_form_valid_saves_with_success_message(self, mock_request_with_user, admin_user):
        """Test that form_valid saves and shows success message."""
        view = PropertyCreateView()
        view.request = mock_request_with_user

        class DummyForm:
            def __init__(self):
                self.cleaned_data = {}

            def save(self, commit=True):
                return Property.objects.create(name="New Property")

        dummy_form = DummyForm()

        with patch.object(view, "get_success_url", return_value="/success/"), patch(
            "lfs.manage.properties.views.messages.success"
        ) as mock_messages:

            response = view.form_valid(dummy_form)

            mock_messages.assert_called_once()
            assert response is not None
