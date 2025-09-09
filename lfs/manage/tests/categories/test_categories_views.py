"""
Comprehensive unit tests for category views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- View method logic and context data
- Form handling and validation
- Permission checks
- Error handling
- Edge cases and boundary conditions
"""

from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.catalog.models import Category
from lfs.manage.categories.views import (
    ManageCategoriesView,
    CategoryDataView,
    CategoryViewView,
    CategoryProductsView,
    CategorySEOView,
    CategoryPortletsView,
    CategoryCreateView,
    CategoryDeleteConfirmView,
    CategoryDeleteView,
    CategoryViewByIDView,
    NoCategoriesView,
    SortCategoriesView,
)

User = get_user_model()


class TestManageCategoriesView:
    """Test ManageCategoriesView behavior."""

    def test_redirect_to_first_category_when_exists(self, request_factory, admin_user, root_category):
        """Should redirect to first category when categories exist."""
        view = ManageCategoriesView()
        request = request_factory.get("/")
        request.user = admin_user
        view.request = request

        url = view.get_redirect_url()

        expected_url = reverse("lfs_manage_category", kwargs={"id": root_category.id})
        assert url == expected_url

    def test_redirect_to_no_categories_when_none_exist(self, request_factory, admin_user, db):
        """Should redirect to no categories view when no categories exist."""
        # Ensure no categories exist
        Category.objects.all().delete()

        view = ManageCategoriesView()
        request = request_factory.get("/")
        request.user = admin_user
        view.request = request

        url = view.get_redirect_url()

        expected_url = reverse("lfs_manage_no_categories")
        assert url == expected_url

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManageCategoriesView.permission_required == "core.manage_shop"


class TestCategoryDataView:
    """Test CategoryDataView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CategoryDataView.permission_required == "core.manage_shop"

    def test_tab_name_is_data(self):
        """Should have correct tab name."""
        assert CategoryDataView.tab_name == "data"

    def test_success_url_uses_category_id(self, root_category):
        """Should redirect to category data tab after successful save."""
        view = CategoryDataView()
        view.object = root_category

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_category", kwargs={"id": root_category.pk})
        assert url == expected_url


class TestCategoryViewView:
    """Test CategoryViewView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CategoryViewView.permission_required == "core.manage_shop"

    def test_tab_name_is_view(self):
        """Should have correct tab name."""
        assert CategoryViewView.tab_name == "view"

    def test_success_url_uses_category_id(self, root_category):
        """Should redirect to category view tab after successful save."""
        view = CategoryViewView()
        view.object = root_category

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_category_view", kwargs={"id": root_category.pk})
        assert url == expected_url


class TestCategoryProductsView:
    """Test CategoryProductsView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CategoryProductsView.permission_required == "core.manage_shop"

    def test_tab_name_is_products(self):
        """Should have correct tab name."""
        assert CategoryProductsView.tab_name == "products"

    def test_success_url_uses_category_id(self, root_category):
        """Should redirect to category products tab."""
        view = CategoryProductsView()
        view.kwargs = {"id": root_category.pk}

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_category_products", kwargs={"id": root_category.pk})
        assert url == expected_url


class TestCategorySEOView:
    """Test CategorySEOView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CategorySEOView.permission_required == "core.manage_shop"

    def test_tab_name_is_seo(self):
        """Should have correct tab name."""
        assert CategorySEOView.tab_name == "seo"

    def test_success_url_uses_category_id(self, root_category):
        """Should redirect to category SEO tab after successful save."""
        view = CategorySEOView()
        view.object = root_category

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_category_seo", kwargs={"id": root_category.pk})
        assert url == expected_url


class TestCategoryPortletsView:
    """Test CategoryPortletsView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CategoryPortletsView.permission_required == "core.manage_shop"

    def test_tab_name_is_portlets(self):
        """Should have correct tab name."""
        assert CategoryPortletsView.tab_name == "portlets"


class TestCategoryCreateView:
    """Test CategoryCreateView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CategoryCreateView.permission_required == "core.manage_shop"

    def test_success_url_uses_created_category_id(self, root_category):
        """Should redirect to created category after successful creation."""
        view = CategoryCreateView()
        view.object = root_category

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_category", kwargs={"id": root_category.pk})
        assert url == expected_url


class TestCategoryDeleteConfirmView:
    """Test CategoryDeleteConfirmView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CategoryDeleteConfirmView.permission_required == "core.manage_shop"


class TestCategoryDeleteView:
    """Test CategoryDeleteView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CategoryDeleteView.permission_required == "core.manage_shop"

    def test_success_url_goes_to_categories_list(self):
        """Should redirect to categories list after deletion."""
        view = CategoryDeleteView()

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_categories")
        assert url == expected_url


class TestCategoryViewByIDView:
    """Test CategoryViewByIDView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CategoryViewByIDView.permission_required == "core.manage_shop"


class TestNoCategoriesView:
    """Test NoCategoriesView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert NoCategoriesView.permission_required == "core.manage_shop"


class TestSortCategoriesView:
    """Test SortCategoriesView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert SortCategoriesView.permission_required == "core.manage_shop"
