"""
Comprehensive integration tests for property views.

Following TDD principles:
- Test complete view behavior including templates and HTTP responses
- Test real Django request/response cycle
- Test authentication and permissions
- Test URL routing and view dispatching
- Clear test names describing integration scenarios
- Arrange-Act-Assert structure for each integration test

Integration tests cover:
- Complete HTTP request/response cycles
- Template rendering and context data
- URL routing and reverse URL generation
- Authentication and permission checking
- Session management and persistence
- Form processing and validation
- Redirects and success/error handling
- AJAX and non-AJAX responses
"""

import pytest
from unittest.mock import patch

from django.urls import reverse

from lfs.catalog.models import Property, PropertyOption
from lfs.catalog.settings import PROPERTY_NUMBER_FIELD, PROPERTY_STEP_TYPE_FIXED_STEP
from lfs.manage.properties.forms import PropertyAddForm


class TestPropertyViewsIntegration:
    """Test property views with full Django integration."""

    @pytest.mark.django_db
    def test_manage_properties_view_redirects_to_first_property(self, client, admin_user, sample_properties):
        """Test that manage properties view redirects to first property when properties exist."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_properties"))

        # Should redirect to first property
        first_property = Property.objects.filter(local=False).order_by("name").first()
        expected_url = reverse("lfs_manage_property", kwargs={"id": first_property.id})

        assert response.status_code == 302
        assert response.url == expected_url

    @pytest.mark.django_db
    def test_manage_properties_view_redirects_to_add_when_no_properties(self, client, admin_user):
        """Test that manage properties view redirects to add form when no properties exist."""
        client.login(username="admin", password="testpass123")

        # Ensure no properties exist
        Property.objects.all().delete()

        response = client.get(reverse("lfs_manage_properties"))

        # Should redirect to add property form
        expected_url = reverse("lfs_add_property")

        assert response.status_code == 302
        assert response.url == expected_url

    @pytest.mark.django_db
    def test_property_data_view_renders_correct_template(self, client, admin_user, sample_properties):
        """Test that property data view renders the correct template."""
        client.login(username="admin", password="testpass123")

        property_obj = sample_properties[0]
        url = reverse("lfs_manage_property", kwargs={"id": property_obj.id})

        response = client.get(url)

        assert response.status_code == 200
        assert "manage/properties/property.html" in [t.name for t in response.templates]

    @pytest.mark.django_db
    def test_property_data_view_context_includes_property_data(self, client, admin_user, sample_properties):
        """Test that property data view context includes all necessary property data."""
        client.login(username="admin", password="testpass123")

        property_obj = sample_properties[0]
        url = reverse("lfs_manage_property", kwargs={"id": property_obj.id})

        response = client.get(url)

        assert response.status_code == 200
        assert "property" in response.context
        assert "properties" in response.context
        assert "page" in response.context
        assert response.context["property"] == property_obj

    @pytest.mark.django_db
    def test_property_create_view_renders_add_form(self, client, admin_user):
        """Test that property create view renders the add property form."""
        client.login(username="admin", password="testpass123")

        url = reverse("lfs_add_property")
        response = client.get(url)

        assert response.status_code == 200
        assert "manage/properties/add_property.html" in [t.name for t in response.templates]
        assert "form" in response.context
        assert isinstance(response.context["form"], PropertyAddForm)

    @pytest.mark.django_db
    def test_property_create_view_creates_property_successfully(self, client, admin_user):
        """Test that property create view creates property and redirects correctly."""
        client.login(username="admin", password="testpass123")

        url = reverse("lfs_add_property")
        form_data = {"name": "Integration Test Property"}

        with patch("lfs.manage.properties.views.messages.success"):
            response = client.post(url, form_data)

        # Should redirect to the created property
        created_property = Property.objects.get(name="Integration Test Property")
        expected_url = reverse("lfs_manage_property", kwargs={"id": created_property.id})

        assert response.status_code == 302
        assert response.url == expected_url
        assert created_property.title == "Integration Test Property"
        assert created_property.position == 10  # Position updated by _update_property_positions

    @pytest.mark.django_db
    def test_property_create_view_handles_invalid_form(self, client, admin_user):
        """Test that property create view handles invalid form data correctly."""
        client.login(username="admin", password="testpass123")

        url = reverse("lfs_add_property")
        form_data = {"name": ""}  # Invalid: empty name

        response = client.post(url, form_data)

        assert response.status_code == 200  # Should re-render form with errors
        assert "form" in response.context
        assert response.context["form"].is_valid() is False
        assert "name" in response.context["form"].errors

    @pytest.mark.django_db
    def test_property_data_view_updates_property_successfully(self, client, admin_user, sample_properties):
        """Test that property data view updates property data successfully."""
        client.login(username="admin", password="testpass123")

        property_obj = sample_properties[0]
        url = reverse("lfs_manage_property", kwargs={"id": property_obj.id})

        form_data = {
            "name": "Updated Property",
            "title": "Updated Title",
            "unit": "kg",
            "type": PROPERTY_NUMBER_FIELD,
            "variants": True,
            "filterable": True,
            "configurable": False,
            "required": True,
            "display_on_product": True,
            "display_price": False,
            "add_price": True,
            "decimal_places": 2,
            "unit_min": 0,
            "unit_max": 100,
            "unit_step": 1,
            "step_type": PROPERTY_STEP_TYPE_FIXED_STEP,
            "step": 5,
        }

        with patch("lfs.manage.properties.views.messages.success"), patch(
            "lfs.manage.properties.views.invalidate_cache_group_id"
        ), patch("lfs.manage.properties.views.property_type_changed.send"):

            response = client.post(url, form_data)

        # Should redirect back to the property
        expected_url = reverse("lfs_manage_property", kwargs={"id": property_obj.id})

        assert response.status_code == 302
        assert response.url == expected_url

        # Verify property was updated
        property_obj.refresh_from_db()
        assert property_obj.name == "Updated Property"
        assert property_obj.title == "Updated Title"
        assert property_obj.unit == "kg"
        assert property_obj.type == PROPERTY_NUMBER_FIELD
        assert property_obj.filterable is True

    @pytest.mark.django_db
    def test_property_delete_confirm_view_renders_confirmation(self, client, admin_user, sample_properties):
        """Test that property delete confirm view renders confirmation template."""
        client.login(username="admin", password="testpass123")

        property_obj = sample_properties[0]
        url = reverse("lfs_delete_property_confirm", kwargs={"id": property_obj.id})

        response = client.get(url)

        assert response.status_code == 200
        assert "property" in response.context
        assert response.context["property"] == property_obj

    @pytest.mark.django_db
    def test_property_delete_view_deletes_property_successfully(self, client, admin_user, sample_properties):
        """Test that property delete view deletes property and redirects correctly."""
        client.login(username="admin", password="testpass123")

        property_obj = sample_properties[0]
        url = reverse("lfs_delete_property", kwargs={"id": property_obj.id})

        with patch("lfs.manage.properties.views.invalidate_cache_group_id"):
            response = client.post(url)

        # Should redirect to properties list
        expected_url = reverse("lfs_manage_properties")

        assert response.status_code == 302
        assert response.url == expected_url
        assert not Property.objects.filter(id=property_obj.id).exists()

    @pytest.mark.django_db
    def test_property_search_integration(self, client, admin_user, sample_properties):
        """Test that property search works correctly in the full request cycle."""
        client.login(username="admin", password="testpass123")

        # Test search functionality
        property_obj = sample_properties[0]  # Color property
        url = reverse("lfs_manage_property", kwargs={"id": property_obj.id}) + "?q=col"

        response = client.get(url)

        assert response.status_code == 200
        assert "search_query" in response.context
        assert response.context["search_query"] == "col"

        # The properties queryset should be filtered
        # (This would be tested more thoroughly in unit tests for the mixin)

    @pytest.mark.django_db
    def test_property_option_add_integration(self, client, admin_user, sample_properties):
        """Test that property option add works in the full request cycle."""
        client.login(username="admin", password="testpass123")

        property_obj = sample_properties[0]
        url = reverse("lfs_add_property_option", kwargs={"property_id": property_obj.id})

        form_data = {"name": "New Option", "price": "25.50"}

        with patch("lfs.manage.properties.views.invalidate_cache_group_id"):
            response = client.post(url, form_data)

        # Should redirect back to property
        expected_url = reverse("lfs_manage_property", kwargs={"id": property_obj.id})

        assert response.status_code == 302
        assert response.url == expected_url
        assert property_obj.options.filter(name="New Option").exists()

    @pytest.mark.django_db
    def test_property_option_update_integration(self, client, admin_user, sample_properties):
        """Test that property option update works in the full request cycle."""
        client.login(username="admin", password="testpass123")

        property_obj = sample_properties[0]
        option = PropertyOption.objects.create(name="Test Option", property=property_obj, price=10.00)

        url = reverse("lfs_update_property_option", kwargs={"property_id": property_obj.id})

        form_data = {"option_id": option.id, "name": "Updated Option", "price": "15.75"}

        with patch("lfs.manage.properties.views.invalidate_cache_group_id"):
            response = client.post(url, form_data)

        # Should redirect back to property
        expected_url = reverse("lfs_manage_property", kwargs={"id": property_obj.id})

        assert response.status_code == 302
        assert response.url == expected_url

        option.refresh_from_db()
        assert option.name == "Updated Option"
        assert option.price == 15.75

    @pytest.mark.django_db
    def test_property_option_delete_integration(self, client, admin_user, sample_properties):
        """Test that property option delete works in the full request cycle."""
        client.login(username="admin", password="testpass123")

        property_obj = sample_properties[0]
        option = PropertyOption.objects.create(name="Test Option", property=property_obj, price=10.00)

        url = reverse("lfs_delete_property_option", kwargs={"option_id": option.id})

        with patch("lfs.manage.properties.views.invalidate_cache_group_id"):
            response = client.post(url)

        # Should redirect back to property
        expected_url = reverse("lfs_manage_property", kwargs={"id": property_obj.id})

        assert response.status_code == 302
        assert response.url == expected_url
        assert not PropertyOption.objects.filter(id=option.id).exists()

    @pytest.mark.django_db
    def test_unauthorized_access_redirects_to_login(self, client, regular_user):
        """Test that unauthorized access redirects to login page."""
        # Don't login - should redirect to login
        url = reverse("lfs_manage_properties")

        response = client.get(url)

        # Should redirect to login page
        assert response.status_code == 302
        assert "/login/" in response.url or "login" in response.url

    @pytest.mark.django_db
    def test_invalid_property_id_returns_404(self, client, admin_user):
        """Test that accessing invalid property ID returns 404."""
        client.login(username="admin", password="testpass123")

        url = reverse("lfs_manage_property", kwargs={"id": 99999})

        response = client.get(url)

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_property_form_validation_errors_displayed(self, client, admin_user, sample_properties):
        """Test that form validation errors are displayed correctly."""
        client.login(username="admin", password="testpass123")

        property_obj = sample_properties[0]
        url = reverse("lfs_manage_property", kwargs={"id": property_obj.id})

        # Submit invalid form data
        form_data = {
            "name": "",  # Invalid: empty name
            "title": "Valid Title",
        }

        response = client.post(url, form_data)

        assert response.status_code == 200  # Should re-render form
        assert "form" in response.context
        assert not response.context["form"].is_valid()
        assert "name" in response.context["form"].errors
