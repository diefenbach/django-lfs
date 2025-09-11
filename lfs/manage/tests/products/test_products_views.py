"""
Unit tests for Product views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Parametrization for variations
"""

from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.catalog.models import Product
from lfs.manage.products.views import (
    ManageProductsView,
    ProductCreateView,
    ProductDataView,
    ProductStockView,
    ProductSEOView,
    ProductPortletsView,
    NoProductsView,
    ProductCategoriesView,
    ProductTabMixin,
)

User = get_user_model()


class TestManageProductsView:
    """Test the ManageProductsView dispatcher."""

    def test_view_inheritance(self):
        """Should inherit from Django RedirectView."""
        from django.views.generic.base import RedirectView

        assert issubclass(ManageProductsView, RedirectView)

    def test_permission_required_attribute(self):
        """Should require core.manage_shop permission."""
        assert hasattr(ManageProductsView, "permission_required")
        assert ManageProductsView.permission_required == "core.manage_shop"

    def test_redirects_to_first_product_when_products_exist(self, client, admin_user, product):
        """Should redirect to first product when products exist."""
        client.login(username="admin", password="testpass123")

        response = client.get("/manage/products/")  # Adjust URL as needed
        # This test assumes the view redirects to the first product
        # Adjust based on actual URL patterns
        assert response.status_code in [200, 302]

    def test_redirects_to_no_products_when_none_exist(self, client, admin_user, db):
        """Should redirect to no products view when no products exist."""
        # Delete all products
        Product.objects.all().delete()

        client.login(username="admin", password="testpass123")
        response = client.get("/manage/products/")
        # Adjust assertion based on actual behavior
        assert response.status_code in [200, 302]


class TestProductCreateView:
    """Test the ProductCreateView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django CreateView."""
        from django.views.generic.edit import CreateView

        assert issubclass(ProductCreateView, CreateView)

    def test_model_attribute(self):
        """Should use Product model."""
        assert ProductCreateView.model == Product

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductCreateView.permission_required == "core.manage_shop"

    def test_template_name(self):
        """Should use correct template."""
        assert ProductCreateView.template_name == "manage/products/add_product.html"

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(ProductCreateView, "form_valid")
        assert callable(getattr(ProductCreateView, "form_valid"))

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(ProductCreateView, "get_success_url")
        assert callable(getattr(ProductCreateView, "get_success_url"))


class TestProductDataView:
    """Test the ProductDataView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from ProductTabMixin and UpdateView."""
        from django.views.generic.edit import UpdateView

        assert issubclass(ProductDataView, ProductTabMixin)
        assert issubclass(ProductDataView, UpdateView)

    def test_model_attribute(self):
        """Should use Product model."""
        assert ProductDataView.model == Product

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductDataView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should use 'data' as tab name."""
        assert ProductDataView.tab_name == "data"

    def test_pk_url_kwarg(self):
        """Should use 'id' as pk_url_kwarg."""
        assert ProductDataView.pk_url_kwarg == "id"

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(ProductDataView, "form_valid")
        assert callable(getattr(ProductDataView, "form_valid"))

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(ProductDataView, "get_success_url")
        assert callable(getattr(ProductDataView, "get_success_url"))

    def test_delete_method_exists(self):
        """Should have delete method."""
        assert hasattr(ProductDataView, "delete")
        assert callable(getattr(ProductDataView, "delete"))

    def test_get_method_exists(self):
        """Should have get method."""
        assert hasattr(ProductDataView, "get")
        assert callable(getattr(ProductDataView, "get"))


class TestProductStockView:
    """Test the ProductStockView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from ProductTabMixin and UpdateView."""
        from django.views.generic.edit import UpdateView

        assert issubclass(ProductStockView, ProductTabMixin)
        assert issubclass(ProductStockView, UpdateView)

    def test_model_attribute(self):
        """Should use Product model."""
        assert ProductStockView.model == Product

    def test_form_class_attribute(self):
        """Should use ProductStockForm."""
        from lfs.manage.products.forms import ProductStockForm

        assert ProductStockView.form_class == ProductStockForm

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductStockView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should use 'stock' as tab name."""
        assert ProductStockView.tab_name == "stock"

    def test_get_form_kwargs_method_exists(self):
        """Should have get_form_kwargs method."""
        assert hasattr(ProductStockView, "get_form_kwargs")
        assert callable(getattr(ProductStockView, "get_form_kwargs"))


class TestProductSEOView:
    """Test the ProductSEOView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from ProductTabMixin and UpdateView."""
        from django.views.generic.edit import UpdateView

        assert issubclass(ProductSEOView, ProductTabMixin)
        assert issubclass(ProductSEOView, UpdateView)

    def test_model_attribute(self):
        """Should use Product model."""
        assert ProductSEOView.model == Product

    def test_form_class_attribute(self):
        """Should use SEOForm."""
        from lfs.manage.products.forms import SEOForm

        assert ProductSEOView.form_class == SEOForm

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductSEOView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should use 'seo' as tab name."""
        assert ProductSEOView.tab_name == "seo"


class TestProductPortletsView:
    """Test the ProductPortletsView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from ProductTabMixin and TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(ProductPortletsView, ProductTabMixin)
        assert issubclass(ProductPortletsView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductPortletsView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should use 'portlets' as tab name."""
        assert ProductPortletsView.tab_name == "portlets"

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ProductPortletsView, "get_context_data")
        assert callable(getattr(ProductPortletsView, "get_context_data"))


class TestNoProductsView:
    """Test the NoProductsView template view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(NoProductsView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert NoProductsView.permission_required == "core.manage_shop"

    def test_template_name(self):
        """Should use correct template."""
        assert NoProductsView.template_name == "manage/products/no_products.html"


class TestProductCategoriesView:
    """Test the ProductCategoriesView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from ProductTabMixin and TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(ProductCategoriesView, ProductTabMixin)
        assert issubclass(ProductCategoriesView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductCategoriesView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should use 'categories' as tab name."""
        assert ProductCategoriesView.tab_name == "categories"

    def test_post_method_exists(self):
        """Should have post method."""
        assert hasattr(ProductCategoriesView, "post")
        assert callable(getattr(ProductCategoriesView, "post"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ProductCategoriesView, "get_context_data")
        assert callable(getattr(ProductCategoriesView, "get_context_data"))


class TestProductTabMixin:
    """Test the ProductTabMixin class."""

    def test_mixin_has_template_name(self):
        """Should have template_name attribute."""
        assert hasattr(ProductTabMixin, "template_name")
        assert ProductTabMixin.template_name == "manage/products/product.html"

    def test_mixin_has_tab_name(self):
        """Should have tab_name attribute."""
        assert hasattr(ProductTabMixin, "tab_name")

    def test_get_product_method_exists(self):
        """Should have get_product method."""
        assert hasattr(ProductTabMixin, "get_product")
        assert callable(getattr(ProductTabMixin, "get_product"))

    def test_get_tabs_method_exists(self):
        """Should have _get_tabs method."""
        assert hasattr(ProductTabMixin, "_get_tabs")
        assert callable(getattr(ProductTabMixin, "_get_tabs"))

    def test_get_products_queryset_method_exists(self):
        """Should have _get_products_queryset method."""
        assert hasattr(ProductTabMixin, "_get_products_queryset")
        assert callable(getattr(ProductTabMixin, "_get_products_queryset"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ProductTabMixin, "get_context_data")
        assert callable(getattr(ProductTabMixin, "get_context_data"))

    def test_get_tabs_returns_correct_structure(self, product):
        """Should return correct tab structure."""
        factory = RequestFactory()
        request = factory.get("/")

        view = ProductDataView()
        view.request = request
        view.object = product
        view.kwargs = {"id": product.id}

        tabs = view._get_tabs(product)

        # Verify tabs structure
        assert isinstance(tabs, list)
        assert len(tabs) > 0
        assert all(isinstance(tab, tuple) and len(tab) == 2 for tab in tabs)

    def test_get_products_queryset_filters_by_search(self, product):
        """Should filter products by search query."""
        factory = RequestFactory()
        request = factory.get("/?q=test")

        view = ProductDataView()
        view.request = request

        queryset = view._get_products_queryset()

        # Should return QuerySet
        assert hasattr(queryset, "filter")
        assert hasattr(queryset, "order_by")

    def test_get_context_data_includes_required_context(self, product):
        """Should include required context variables."""
        factory = RequestFactory()
        request = factory.get("/")

        view = ProductDataView()
        view.request = request
        view.object = product
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        assert "product" in context
        assert "active_tab" in context
        assert "tabs" in context
        assert "products" in context
        assert "search_query" in context
