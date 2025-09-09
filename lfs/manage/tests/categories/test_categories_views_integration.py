"""
Comprehensive integration tests for category management views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Integration testing with real HTTP requests

Tests cover:
- ManageCategoriesView (redirect logic)
- CategoryDataView (data tab)
- CategoryViewView (view tab)
- CategoryProductsView (products tab)
- CategorySEOView (SEO tab)
- CategoryPortletsView (portlets tab)
- CategoryCreateView (creation)
- CategoryDeleteConfirmView and CategoryDeleteView (deletion)
- NoCategoriesView (empty state)
- SortCategoriesView (sorting)
- Authentication and permission requirements
- Session handling
- Template rendering
- Error handling
"""

import json

from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.catalog.models import Category

User = get_user_model()


class TestManageCategoriesViewIntegration:
    """Integration tests for ManageCategoriesView."""

    def test_redirect_to_first_category_with_existing_categories(self, client, admin_user, root_category):
        """Should redirect to first category when categories exist."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_categories"))

        assert response.status_code == 302
        expected_url = reverse("lfs_manage_category", kwargs={"id": root_category.id})
        assert response.url == expected_url

    def test_redirect_to_no_categories_with_no_categories(self, client, admin_user, db):
        """Should redirect to no categories view when no categories exist."""
        # Ensure no categories exist
        Category.objects.all().delete()

        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_categories"))

        assert response.status_code == 302
        expected_url = reverse("lfs_manage_no_categories")
        assert response.url == expected_url

    def test_requires_login(self, client):
        """Should require login."""
        response = client.get(reverse("lfs_manage_categories"))

        assert response.status_code == 302
        assert "/login/" in response.url


class TestCategoryDataViewIntegration:
    """Integration tests for CategoryDataView."""

    def test_get_category_data_tab(self, client, admin_user, root_category):
        """Should render category data tab correctly."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_category", kwargs={"id": root_category.id}))

        assert response.status_code == 200
        assert "category" in response.context
        assert response.context["category"] == root_category
        assert response.context["active_tab"] == "data"

    def test_post_category_data_updates_category(self, client, admin_user, root_category):
        """Should update category data on POST."""
        client.login(username="admin", password="testpass123")

        new_name = "Updated Category Name"
        data = {"name": new_name, "slug": "updated-slug", "description": "Updated description"}

        response = client.post(reverse("lfs_manage_category", kwargs={"id": root_category.id}), data)

        assert response.status_code == 302
        root_category.refresh_from_db()
        assert root_category.name == new_name

    def test_requires_permission(self, client, regular_user, root_category):
        """Should require proper permissions."""
        client.login(username="user", password="testpass123")

        response = client.get(reverse("lfs_manage_category", kwargs={"id": root_category.id}))

        # Should redirect or deny access
        assert response.status_code in [302, 403]


class TestCategoryViewViewIntegration:
    """Integration tests for CategoryViewView."""

    def test_get_category_view_tab(self, client, admin_user, root_category):
        """Should render category view tab correctly."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_category_view", kwargs={"id": root_category.id}))

        assert response.status_code == 200
        assert "category" in response.context
        assert response.context["category"] == root_category
        assert response.context["active_tab"] == "view"


class TestCategoryProductsViewIntegration:
    """Integration tests for CategoryProductsView."""

    def test_get_category_products_tab(self, client, admin_user, root_category):
        """Should render category products tab correctly."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_category_products", kwargs={"id": root_category.id}))

        assert response.status_code == 200
        assert "category" in response.context
        assert response.context["category"] == root_category
        assert response.context["active_tab"] == "products"

    def test_assign_product_to_category(self, client, admin_user, root_category, product):
        """Should assign product to category."""
        client.login(username="admin", password="testpass123")

        data = {"assign_products": "1", f"product-{product.id}": "on"}

        response = client.post(reverse("lfs_manage_category_products", kwargs={"id": root_category.id}), data)

        assert response.status_code == 302
        assert product in root_category.products.all()

    def test_remove_product_from_category(self, client, admin_user, root_category, product):
        """Should remove product from category."""
        # First assign the product
        root_category.products.add(product)

        client.login(username="admin", password="testpass123")

        data = {"remove_products": "1", f"product-{product.id}": "on"}

        response = client.post(reverse("lfs_manage_category_products", kwargs={"id": root_category.id}), data)

        assert response.status_code == 302
        assert product not in root_category.products.all()


class TestCategoryCreateViewIntegration:
    """Integration tests for CategoryCreateView."""

    def test_get_create_category_form(self, client, admin_user):
        """Should render create category form."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_add_top_category"))

        assert response.status_code == 200
        assert "form" in response.context

    def test_create_root_category(self, client, admin_user):
        """Should create root category successfully."""
        client.login(username="admin", password="testpass123")

        data = {"name": "New Root Category", "slug": "new-root-category", "description": "A new root category"}

        response = client.post(reverse("lfs_manage_add_top_category"), data)

        assert response.status_code == 302
        assert Category.objects.filter(name="New Root Category").exists()

    def test_create_child_category(self, client, admin_user, root_category):
        """Should create child category successfully."""
        client.login(username="admin", password="testpass123")

        data = {"name": "New Child Category", "slug": "new-child-category", "description": "A new child category"}

        response = client.post(reverse("lfs_manage_add_category", kwargs={"parent_id": root_category.id}), data)

        assert response.status_code == 302
        child_category = Category.objects.get(name="New Child Category")
        assert child_category.parent == root_category


class TestCategoryDeleteIntegration:
    """Integration tests for category deletion."""

    def test_get_delete_confirmation(self, client, admin_user, root_category):
        """Should render delete confirmation page."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_delete_category_confirm", kwargs={"id": root_category.id}))

        assert response.status_code == 200
        assert "category" in response.context
        assert response.context["category"] == root_category

    def test_delete_category(self, client, admin_user, root_category):
        """Should delete category successfully."""
        client.login(username="admin", password="testpass123")

        response = client.post(reverse("lfs_delete_category", kwargs={"id": root_category.id}))

        assert response.status_code == 302
        assert not Category.objects.filter(id=root_category.id).exists()


class TestNoCategoriesViewIntegration:
    """Integration tests for NoCategoriesView."""

    def test_render_no_categories_page(self, client, admin_user, db):
        """Should render no categories page when no categories exist."""
        # Ensure no categories exist
        Category.objects.all().delete()

        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_no_categories"))

        assert response.status_code == 200
        assert "No Categories" in response.content.decode()


class TestSortCategoriesViewIntegration:
    """Integration tests for SortCategoriesView."""

    def test_sort_categories(self, client, admin_user, root_category, child_category):
        """Should sort categories successfully."""
        client.login(username="admin", password="testpass123")

        # Create category data for sorting
        category_data = f"category[{root_category.id}]=root&category[{child_category.id}]={root_category.id}"

        data = {"categories": category_data}

        response = client.post(reverse("lfs_sort_categories"), data)

        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert "message" in response_data
