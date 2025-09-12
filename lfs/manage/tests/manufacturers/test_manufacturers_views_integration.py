"""
Comprehensive integration tests for manufacturer management views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Integration testing with real HTTP requests

Tests cover:
- ManageManufacturersView (redirect logic)
- ManufacturerDataView (data tab)
- ManufacturerProductsView (products tab)
- ManufacturerSEOView (SEO tab)
- ManufacturerPortletsView (portlets tab)
- ManufacturerCreateView (creation)
- ManufacturerDeleteConfirmView and ManufacturerDeleteView (deletion)
- NoManufacturersView (empty state)
- ManufacturersAjaxView (AJAX functionality)
- Authentication and permission requirements
- Session handling
- Template rendering
- Error handling
"""

import json

from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.manufacturer.models import Manufacturer

User = get_user_model()


class TestManageManufacturersViewIntegration:
    """Integration tests for ManageManufacturersView."""

    def test_redirect_to_first_manufacturer_with_existing_manufacturers(self, client, admin_user, manufacturer):
        """Should redirect to first manufacturer when manufacturers exist."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_manufacturers"))

        assert response.status_code == 302
        expected_url = reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id})
        assert response.url == expected_url

    def test_redirect_to_no_manufacturers_with_no_manufacturers(self, client, admin_user, db):
        """Should redirect to no manufacturers view when no manufacturers exist."""
        # Ensure no manufacturers exist
        Manufacturer.objects.all().delete()

        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_manufacturers"))

        assert response.status_code == 302
        expected_url = reverse("lfs_manage_no_manufacturers")
        assert response.url == expected_url

    def test_requires_login(self, client):
        """Should require login."""
        response = client.get(reverse("lfs_manage_manufacturers"))

        assert response.status_code == 302
        assert "/login/" in response.url


class TestManufacturerDataViewIntegration:
    """Integration tests for ManufacturerDataView."""

    def test_get_manufacturer_data_tab(self, client, admin_user, manufacturer):
        """Should render manufacturer data tab correctly."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id}))

        assert response.status_code == 200
        assert "manufacturer" in response.context
        assert response.context["manufacturer"] == manufacturer
        assert response.context["active_tab"] == "data"

    def test_post_manufacturer_data_updates_manufacturer(self, client, admin_user, manufacturer):
        """Should update manufacturer data on POST."""
        client.login(username="admin", password="testpass123")

        new_name = "Updated Manufacturer Name"
        data = {"name": new_name, "slug": "updated-slug", "description": "Updated description"}

        response = client.post(reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id}), data)

        assert response.status_code == 302
        manufacturer.refresh_from_db()
        assert manufacturer.name == new_name

    def test_requires_permission(self, client, regular_user, manufacturer):
        """Should require proper permissions."""
        client.login(username="user", password="testpass123")

        response = client.get(reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id}))

        # Should redirect or deny access
        assert response.status_code in [302, 403]

    def test_image_deletion_functionality(self, client, admin_user, manufacturer):
        """Should handle image deletion when checkbox is checked."""
        client.login(username="admin", password="testpass123")

        # Test with delete_image checkbox
        data = {
            "name": manufacturer.name,
            "slug": manufacturer.slug,
            "description": manufacturer.description,
            "delete_image": "on",
        }

        response = client.post(reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id}), data)

        assert response.status_code == 302
        # Image should be handled (deleted if it existed)


class TestManufacturerProductsViewIntegration:
    """Integration tests for ManufacturerProductsView."""

    def test_get_manufacturer_products_tab(self, client, admin_user, manufacturer):
        """Should render manufacturer products tab correctly."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id}))

        assert response.status_code == 200
        assert "manufacturer" in response.context
        assert response.context["manufacturer"] == manufacturer
        assert response.context["active_tab"] == "products"

    def test_assign_product_to_manufacturer(self, client, admin_user, manufacturer, product_without_manufacturer):
        """Should assign product to manufacturer."""
        client.login(username="admin", password="testpass123")

        data = {"assign_products": "1", f"product-{product_without_manufacturer.id}": "on"}

        response = client.post(reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id}), data)

        assert response.status_code == 302
        product_without_manufacturer.refresh_from_db()
        assert product_without_manufacturer.manufacturer == manufacturer

    def test_remove_product_from_manufacturer(self, client, admin_user, manufacturer, product):
        """Should remove product from manufacturer."""
        # Product is already assigned to manufacturer via fixture
        assert product.manufacturer == manufacturer

        client.login(username="admin", password="testpass123")

        data = {"remove_products": "1", f"product-{product.id}": "on"}

        response = client.post(reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id}), data)

        assert response.status_code == 302
        product.refresh_from_db()
        assert product.manufacturer is None

    def test_products_filtering_functionality(self, client, admin_user, manufacturer):
        """Should handle product filtering."""
        client.login(username="admin", password="testpass123")

        # Test with filter parameter
        response = client.get(
            reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id}), {"filter": "test"}
        )

        assert response.status_code == 200
        assert "filter" in response.context
        assert response.context["filter"] == "test"

    def test_products_pagination(self, client, admin_user, manufacturer):
        """Should handle product pagination."""
        client.login(username="admin", password="testpass123")

        # Test with page parameter
        response = client.get(
            reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id}), {"page": "1"}
        )

        assert response.status_code == 200
        assert "page" in response.context

    def test_category_filter_functionality(self, client, admin_user, manufacturer, category):
        """Should handle category filtering."""
        client.login(username="admin", password="testpass123")

        # Test with category filter
        response = client.get(
            reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id}),
            {"products_category_filter": category.id},
        )

        assert response.status_code == 200
        assert "category_filter" in response.context


class TestManufacturerSEOViewIntegration:
    """Integration tests for ManufacturerSEOView."""

    def test_get_manufacturer_seo_tab(self, client, admin_user, manufacturer):
        """Should render manufacturer SEO tab correctly."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_manufacturer_seo", kwargs={"id": manufacturer.id}))

        assert response.status_code == 200
        assert "manufacturer" in response.context
        assert response.context["manufacturer"] == manufacturer
        assert response.context["active_tab"] == "seo"

    def test_post_manufacturer_seo_updates_seo_data(self, client, admin_user, manufacturer):
        """Should update manufacturer SEO data on POST."""
        client.login(username="admin", password="testpass123")

        seo_data = {
            "meta_title": "New Meta Title",
            "meta_description": "New meta description",
            "meta_keywords": "keyword1, keyword2",
        }

        response = client.post(reverse("lfs_manage_manufacturer_seo", kwargs={"id": manufacturer.id}), seo_data)

        assert response.status_code == 302
        manufacturer.refresh_from_db()
        assert manufacturer.meta_title == "New Meta Title"
        assert manufacturer.meta_description == "New meta description"
        assert manufacturer.meta_keywords == "keyword1, keyword2"


class TestManufacturerPortletsViewIntegration:
    """Integration tests for ManufacturerPortletsView."""

    def test_get_manufacturer_portlets_tab(self, client, admin_user, manufacturer):
        """Should render manufacturer portlets tab correctly."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_manufacturer_portlets", kwargs={"id": manufacturer.id}))

        assert response.status_code == 200
        assert "manufacturer" in response.context
        assert response.context["manufacturer"] == manufacturer
        assert response.context["active_tab"] == "portlets"


class TestManufacturerCreateViewIntegration:
    """Integration tests for ManufacturerCreateView."""

    def test_get_create_manufacturer_form(self, client, admin_user):
        """Should render create manufacturer form."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_add_manufacturer"))

        assert response.status_code == 200
        assert "form" in response.context

    def test_create_manufacturer(self, client, admin_user):
        """Should create manufacturer successfully."""
        client.login(username="admin", password="testpass123")

        data = {"name": "New Test Manufacturer", "slug": "new-test-manufacturer"}

        response = client.post(reverse("lfs_manage_add_manufacturer"), data)

        assert response.status_code == 302
        assert Manufacturer.objects.filter(name="New Test Manufacturer").exists()

    def test_create_manufacturer_with_invalid_data(self, client, admin_user):
        """Should handle invalid data gracefully."""
        client.login(username="admin", password="testpass123")

        # Missing required fields
        data = {"name": ""}

        response = client.post(reverse("lfs_manage_add_manufacturer"), data)

        assert response.status_code == 200  # Should stay on form page
        assert "form" in response.context
        assert response.context["form"].errors

    def test_create_manufacturer_with_duplicate_slug(self, client, admin_user, manufacturer):
        """Should handle duplicate slug validation."""
        client.login(username="admin", password="testpass123")

        data = {"name": "Another Manufacturer", "slug": manufacturer.slug}

        response = client.post(reverse("lfs_manage_add_manufacturer"), data)

        assert response.status_code == 200  # Should stay on form page
        assert "form" in response.context
        assert response.context["form"].errors


class TestManufacturerDeleteIntegration:
    """Integration tests for manufacturer deletion."""

    def test_get_delete_confirmation(self, client, admin_user, manufacturer):
        """Should render delete confirmation page."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_delete_manufacturer_confirm", kwargs={"id": manufacturer.id}))

        assert response.status_code == 200
        assert "manufacturer" in response.context
        assert response.context["manufacturer"] == manufacturer

    def test_delete_manufacturer(self, client, admin_user, manufacturer):
        """Should delete manufacturer successfully."""
        client.login(username="admin", password="testpass123")

        response = client.post(reverse("lfs_delete_manufacturer", kwargs={"id": manufacturer.id}))

        assert response.status_code == 302
        assert not Manufacturer.objects.filter(id=manufacturer.id).exists()

    def test_delete_nonexistent_manufacturer(self, client, admin_user):
        """Should handle deletion of nonexistent manufacturer."""
        client.login(username="admin", password="testpass123")

        response = client.post(reverse("lfs_delete_manufacturer", kwargs={"id": 99999}))

        assert response.status_code == 404


class TestManufacturerViewByIDIntegration:
    """Integration tests for ManufacturerViewByIDView."""

    def test_redirect_to_manufacturer_detail(self, client, admin_user, manufacturer):
        """Should redirect to manufacturer detail page."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manufacturer_by_id", kwargs={"id": manufacturer.id}))

        assert response.status_code == 302
        expected_url = reverse("lfs_manufacturer", kwargs={"slug": manufacturer.slug})
        assert response.url == expected_url

    def test_redirect_with_nonexistent_manufacturer(self, client, admin_user):
        """Should handle nonexistent manufacturer gracefully."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manufacturer_by_id", kwargs={"id": 99999}))

        assert response.status_code == 404


class TestNoManufacturersViewIntegration:
    """Integration tests for NoManufacturersView."""

    def test_render_no_manufacturers_page(self, client, admin_user, db):
        """Should render no manufacturers page when no manufacturers exist."""
        # Ensure no manufacturers exist
        Manufacturer.objects.all().delete()

        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_no_manufacturers"))

        assert response.status_code == 200
        content = response.content.decode()
        assert "no manufacturers" in content.lower() or "no content" in content.lower()


class TestManufacturersAjaxViewIntegration:
    """Integration tests for ManufacturersAjaxView."""

    def test_ajax_manufacturers_search(self, client, admin_user, manufacturer):
        """Should return manufacturers for autocomplete."""
        client.login(username="admin", password="testpass123")

        response = client.get(
            reverse("lfs_manufacturers_ajax"), {"term": manufacturer.name[:3]}  # Search with first 3 characters
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert isinstance(data, list)

        # Should find our manufacturer
        manufacturer_found = any(item["value"] == manufacturer.pk for item in data)
        assert manufacturer_found

    def test_ajax_manufacturers_search_no_results(self, client, admin_user):
        """Should return empty list when no manufacturers match."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manufacturers_ajax"), {"term": "nonexistent"})

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data == []

    def test_ajax_manufacturers_search_without_term(self, client, admin_user, manufacturer):
        """Should handle search without term parameter."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manufacturers_ajax"))

        assert response.status_code == 200
        data = json.loads(response.content)
        assert isinstance(data, list)

    def test_ajax_manufacturers_search_limit(self, client, admin_user, db):
        """Should limit results to 10 manufacturers."""
        client.login(username="admin", password="testpass123")

        # Create 15 manufacturers with similar names
        for i in range(15):
            Manufacturer.objects.create(name=f"Test Manufacturer {i:02d}", slug=f"test-manufacturer-{i:02d}")

        response = client.get(reverse("lfs_manufacturers_ajax"), {"term": "Test"})

        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data) <= 10  # Should be limited to 10 results


class TestManufacturerTabNavigation:
    """Integration tests for tab navigation."""

    def test_tab_navigation_with_search_parameter(self, client, admin_user, manufacturer):
        """Should preserve search parameter in tab navigation."""
        client.login(username="admin", password="testpass123")

        # Access manufacturer with search parameter
        response = client.get(reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id}), {"q": "search term"})

        assert response.status_code == 200
        assert response.context["search_query"] == "search term"

        # Check that tabs include search parameter
        tabs = response.context["tabs"]
        for tab_name, tab_url in tabs:
            if "q=search+term" in tab_url:
                # At least one tab should include the search parameter
                break
        else:
            # If we reach here, no tab had the search parameter
            assert False, "Search parameter should be preserved in tab URLs"

    def test_manufacturer_context_in_all_tabs(self, client, admin_user, manufacturer):
        """Should include manufacturer context in all tabs."""
        client.login(username="admin", password="testpass123")

        tab_urls = [
            reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id}),
            reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id}),
            reverse("lfs_manage_manufacturer_seo", kwargs={"id": manufacturer.id}),
            reverse("lfs_manage_manufacturer_portlets", kwargs={"id": manufacturer.id}),
        ]

        for url in tab_urls:
            response = client.get(url)
            assert response.status_code == 200
            assert "manufacturer" in response.context
            assert response.context["manufacturer"] == manufacturer
