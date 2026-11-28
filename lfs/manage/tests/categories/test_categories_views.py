from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.catalog.models import Category
from lfs.manage.categories.views import (
    ManageCategoriesView,
    CategoryDataView,
    CategoryViewView,
    CategoryProductsView,
    CategorySEOView,
    CategoryCreateView,
    CategoryDeleteView,
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


class TestCategoryDataView:
    """Test CategoryDataView behavior."""



    def test_success_url_uses_category_id(self, root_category):
        """Should redirect to category data tab after successful save."""
        view = CategoryDataView()
        view.object = root_category

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_category", kwargs={"id": root_category.pk})
        assert url == expected_url


class TestCategoryViewView:
    """Test CategoryViewView behavior."""



    def test_success_url_uses_category_id(self, root_category):
        """Should redirect to category view tab after successful save."""
        view = CategoryViewView()
        view.object = root_category

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_category_view", kwargs={"id": root_category.pk})
        assert url == expected_url


class TestCategoryProductsView:
    """Test CategoryProductsView behavior."""



    def test_success_url_uses_category_id(self, root_category):
        """Should redirect to category products tab."""
        view = CategoryProductsView()
        view.kwargs = {"id": root_category.pk}

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_category_products", kwargs={"id": root_category.pk})
        assert url == expected_url


class TestCategorySEOView:
    """Test CategorySEOView behavior."""



    def test_success_url_uses_category_id(self, root_category):
        """Should redirect to category SEO tab after successful save."""
        view = CategorySEOView()
        view.object = root_category

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_category_seo", kwargs={"id": root_category.pk})
        assert url == expected_url



class TestCategoryCreateView:
    """Test CategoryCreateView behavior."""


    def test_success_url_uses_created_category_id(self, root_category):
        """Should redirect to created category after successful creation."""
        view = CategoryCreateView()
        view.object = root_category

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_category", kwargs={"id": root_category.pk})
        assert url == expected_url



class TestCategoryDeleteView:
    """Test CategoryDeleteView behavior."""


    def test_success_url_goes_to_categories_list(self):
        """Should redirect to categories list after deletion."""
        view = CategoryDeleteView()

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_categories")
        assert url == expected_url




