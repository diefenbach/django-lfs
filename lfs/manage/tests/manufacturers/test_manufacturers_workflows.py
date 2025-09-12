"""
Comprehensive workflow tests for manufacturer management.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- Complete manufacturer management workflows
- Product assignments
- SEO and metadata workflows
- User permission workflows
"""

from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.manufacturer.models import Manufacturer

User = get_user_model()


class TestManufacturerManagementWorkflow:
    """Test complete manufacturer management workflows."""

    def test_create_manufacturer_workflow(self, client, admin_user):
        """Test complete workflow for creating a manufacturer."""
        client.login(username="admin", password="testpass123")

        # Step 1: Access add manufacturer form
        response = client.get(reverse("lfs_manage_add_manufacturer"))
        assert response.status_code == 200

        # Step 2: Submit manufacturer creation form
        manufacturer_data = {
            "name": "Workflow Test Manufacturer",
            "slug": "workflow-test-manufacturer",
        }

        response = client.post(reverse("lfs_manage_add_manufacturer"), manufacturer_data)
        assert response.status_code == 302

        # Step 3: Verify manufacturer was created
        manufacturer = Manufacturer.objects.get(slug="workflow-test-manufacturer")
        assert manufacturer.name == "Workflow Test Manufacturer"

        # Step 4: Access manufacturer management page
        response = client.get(reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id}))
        assert response.status_code == 200
        assert response.context["manufacturer"] == manufacturer

    def test_update_manufacturer_workflow(self, client, admin_user, manufacturer):
        """Test complete workflow for updating a manufacturer."""
        client.login(username="admin", password="testpass123")

        # Step 1: Access manufacturer data tab
        response = client.get(reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id}))
        assert response.status_code == 200

        # Step 2: Update manufacturer data
        updated_data = {
            "name": "Updated Manufacturer Name",
            "slug": "updated-manufacturer-slug",
            "description": "Updated manufacturer description",
        }

        response = client.post(reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id}), updated_data)
        assert response.status_code == 302

        # Step 3: Verify manufacturer was updated
        manufacturer.refresh_from_db()
        assert manufacturer.name == "Updated Manufacturer Name"
        assert manufacturer.slug == "updated-manufacturer-slug"
        assert manufacturer.description == "Updated manufacturer description"

    def test_manufacturer_navigation_workflow(self, client, admin_user, manufacturers_list):
        """Test navigation between manufacturers."""
        manufacturer1, manufacturer2 = manufacturers_list
        client.login(username="admin", password="testpass123")

        # Navigate to first manufacturer
        response = client.get(reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer1.id}))
        assert response.status_code == 200
        assert response.context["manufacturer"] == manufacturer1

        # Navigate to second manufacturer
        response = client.get(reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer2.id}))
        assert response.status_code == 200
        assert response.context["manufacturer"] == manufacturer2


class TestManufacturerProductAssignmentWorkflow:
    """Test product assignment workflows."""

    def test_assign_products_to_manufacturer_workflow(
        self, client, admin_user, manufacturer, product_without_manufacturer
    ):
        """Test complete workflow for assigning products to manufacturer."""
        client.login(username="admin", password="testpass123")

        # Step 1: Access products tab
        response = client.get(reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id}))
        assert response.status_code == 200

        # Step 2: Assign product to manufacturer
        assign_data = {"assign_products": "1", f"product-{product_without_manufacturer.id}": "on"}

        response = client.post(reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id}), assign_data)
        assert response.status_code == 302

        # Step 3: Verify product was assigned
        product_without_manufacturer.refresh_from_db()
        assert product_without_manufacturer.manufacturer == manufacturer

        # Step 4: Verify product shows up in manufacturer products list
        response = client.get(reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id}))
        assert response.status_code == 200
        assert product_without_manufacturer in response.context["manufacturer_products"]

    def test_remove_products_from_manufacturer_workflow(self, client, admin_user, manufacturer, product):
        """Test complete workflow for removing products from manufacturer."""
        # Product is already assigned to manufacturer via fixture
        assert product.manufacturer == manufacturer

        client.login(username="admin", password="testpass123")

        # Step 1: Access products tab
        response = client.get(reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id}))
        assert response.status_code == 200

        # Step 2: Remove product from manufacturer
        remove_data = {"remove_products": "1", f"product-{product.id}": "on"}

        response = client.post(reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id}), remove_data)
        assert response.status_code == 302

        # Step 3: Verify product was removed
        product.refresh_from_db()
        assert product.manufacturer is None


class TestManufacturerSEOWorkflow:
    """Test SEO and metadata workflows."""

    def test_update_manufacturer_seo_data_workflow(self, client, admin_user, manufacturer):
        """Test complete workflow for updating manufacturer SEO data."""
        client.login(username="admin", password="testpass123")

        # Step 1: Access SEO tab
        response = client.get(reverse("lfs_manage_manufacturer_seo", kwargs={"id": manufacturer.id}))
        assert response.status_code == 200

        # Step 2: Update SEO data
        seo_data = {
            "meta_title": "Updated Meta Title",
            "meta_description": "Updated meta description for SEO",
            "meta_keywords": "keyword1, keyword2, keyword3",
        }

        response = client.post(reverse("lfs_manage_manufacturer_seo", kwargs={"id": manufacturer.id}), seo_data)
        assert response.status_code == 302

        # Step 3: Verify SEO data was updated
        manufacturer.refresh_from_db()
        assert manufacturer.meta_title == "Updated Meta Title"
        assert manufacturer.meta_description == "Updated meta description for SEO"
        assert manufacturer.meta_keywords == "keyword1, keyword2, keyword3"

    def test_seo_data_persistence_workflow(self, client, admin_user, manufacturer):
        """Test that SEO data persists through manufacturer updates."""
        # Set initial SEO data
        manufacturer.meta_title = "Initial Title"
        manufacturer.meta_description = "Initial description"
        manufacturer.save()

        client.login(username="admin", password="testpass123")

        # Update other manufacturer data (not SEO)
        update_data = {"name": "Updated Name", "slug": "updated-slug", "description": "Updated description"}

        response = client.post(reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id}), update_data)
        assert response.status_code == 302

        # Verify SEO data is still there
        manufacturer.refresh_from_db()
        assert manufacturer.meta_title == "Initial Title"
        assert manufacturer.meta_description == "Initial description"


class TestManufacturerDeletionWorkflow:
    """Test manufacturer deletion workflows."""

    def test_delete_manufacturer_with_products_workflow(self, client, admin_user, manufacturer, product):
        """Test workflow for deleting manufacturer with products."""
        # Product is assigned to manufacturer via fixture
        assert product.manufacturer == manufacturer

        client.login(username="admin", password="testpass123")

        # Step 1: Access delete confirmation
        response = client.get(reverse("lfs_delete_manufacturer_confirm", kwargs={"id": manufacturer.id}))
        assert response.status_code == 200

        # Step 2: Confirm deletion
        response = client.post(reverse("lfs_delete_manufacturer", kwargs={"id": manufacturer.id}))
        assert response.status_code == 302

        # Step 3: Verify manufacturer was deleted
        assert not Manufacturer.objects.filter(id=manufacturer.id).exists()

        # Step 4: Verify product manufacturer was set to None
        product.refresh_from_db()
        assert product.manufacturer is None

    def test_delete_empty_manufacturer_workflow(self, client, admin_user, manufacturer):
        """Test workflow for deleting manufacturer without products."""
        client.login(username="admin", password="testpass123")

        # Step 1: Access delete confirmation
        response = client.get(reverse("lfs_delete_manufacturer_confirm", kwargs={"id": manufacturer.id}))
        assert response.status_code == 200

        # Step 2: Confirm deletion
        response = client.post(reverse("lfs_delete_manufacturer", kwargs={"id": manufacturer.id}))
        assert response.status_code == 302

        # Step 3: Verify manufacturer was deleted
        assert not Manufacturer.objects.filter(id=manufacturer.id).exists()


class TestManufacturerRedirectionWorkflow:
    """Test redirection workflows."""

    def test_manufacturer_dispatcher_with_existing_manufacturers(self, client, admin_user, manufacturer):
        """Test dispatcher redirects to first manufacturer when manufacturers exist."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_manufacturers"))

        assert response.status_code == 302
        expected_url = reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id})
        assert response.url == expected_url

    def test_manufacturer_dispatcher_with_no_manufacturers(self, client, admin_user, db):
        """Test dispatcher redirects to no manufacturers view when none exist."""
        # Ensure no manufacturers exist
        Manufacturer.objects.all().delete()

        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_manufacturers"))

        assert response.status_code == 302
        expected_url = reverse("lfs_manage_no_manufacturers")
        assert response.url == expected_url

    def test_manufacturer_view_by_id_workflow(self, client, admin_user, manufacturer):
        """Test view by ID redirects to manufacturer detail page."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manufacturer_by_id", kwargs={"id": manufacturer.id}))

        assert response.status_code == 302
        expected_url = reverse("lfs_manufacturer", kwargs={"slug": manufacturer.slug})
        assert response.url == expected_url


class TestNoManufacturersWorkflow:
    """Test no manufacturers view workflow."""

    def test_no_manufacturers_page_workflow(self, client, admin_user, db):
        """Test no manufacturers page displays correctly when no manufacturers exist."""
        # Ensure no manufacturers exist
        Manufacturer.objects.all().delete()

        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_no_manufacturers"))

        assert response.status_code == 200
        content = response.content.decode()
        assert "no manufacturers" in content.lower() or "no content" in content.lower()
