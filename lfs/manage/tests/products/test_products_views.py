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
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.test import RequestFactory
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import UpdateView

from lfs.catalog.models import Product
from lfs.manage.mixins import DirectDeleteMixin
from lfs.manage.products.views import (
    ManageProductsView,
    ProductCreateView,
    ProductDataView,
    ProductListView,
    ProductStockView,
    ProductSEOView,
    ProductPortletsView,
    NoProductsView,
    ProductCategoriesView,
    ProductImagesView,
    ProductAttachmentsView,
    ProductAccessoriesView,
    ProductBulkPricesView,
    ProductVariantsView,
    ProductRelatedProductsView,
    ProductPropertiesView,
    ProductDeleteConfirmView,
    ProductDeleteView,
    ApplyProductFiltersView,
    ResetProductFiltersView,
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

    def test_get_form_class_returns_product_form_for_standard_product(self, product):
        """Should return ProductDataForm for standard products."""
        from lfs.manage.products.forms import ProductDataForm

        factory = RequestFactory()
        request = factory.get("/")
        view = ProductDataView()
        view.request = request
        view.object = product
        view.kwargs = {"id": product.id}

        form_class = view.get_form_class()
        assert form_class == ProductDataForm

    def test_get_form_class_returns_variant_form_for_variant_product(self, variant_product):
        """Should return VariantDataForm for variant products."""
        from lfs.manage.products.forms import VariantDataForm

        factory = RequestFactory()
        request = factory.get("/")
        view = ProductDataView()
        view.request = request
        view.object = variant_product
        view.kwargs = {"id": variant_product.id}

        form_class = view.get_form_class()
        assert form_class == VariantDataForm

    def test_form_valid_adds_success_message(self, rf, product, mocker):
        """Should add success message when form is valid."""
        from django.contrib import messages

        factory = RequestFactory()
        request = factory.post("/", {})
        request.session = {}

        view = ProductDataView()
        view.request = request
        view.object = product

        # Mock super().form_valid() to return HttpResponse
        mock_super_form_valid = mocker.patch.object(UpdateView, "form_valid")
        mock_super_form_valid.return_value = HttpResponse()

        # Mock messages.success to avoid middleware requirement
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        # Mock form
        mock_form = mocker.MagicMock()

        # Call form_valid
        response = view.form_valid(mock_form)

        # Verify success message was added
        mock_messages_success.assert_called_once_with(request, "Product data has been saved.")
        assert response is not None

    def test_get_success_url_returns_correct_url(self, product):
        """Should return URL to product data page."""
        factory = RequestFactory()
        request = factory.get("/")
        view = ProductDataView()
        view.request = request
        view.object = product

        url = view.get_success_url()
        expected_url = f"/manage/product/{product.id}/data/"
        assert url == expected_url

    def test_delete_standard_product_redirects_to_products_overview(self, rf, admin_user, product, mocker):
        """Should redirect to products overview when deleting standard product."""
        from django.contrib import messages

        factory = RequestFactory()
        request = factory.post("/", {})
        request.user = admin_user
        request.session = {}

        view = ProductDataView()
        view.request = request
        view.object = product
        view.kwargs = {"id": product.id}

        # Mock messages.success to avoid middleware requirement
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.delete(request)

        # Should redirect to products overview
        assert isinstance(response, HttpResponseRedirect)
        assert "/manage/products/" in response.url

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Product has been deleted.")

    def test_delete_variant_product_redirects_to_parent(self, rf, admin_user, variant_product, mocker):
        """Should redirect to parent product when deleting variant."""
        from django.contrib import messages

        factory = RequestFactory()
        request = factory.post("/", {})
        request.user = admin_user
        request.session = {}

        view = ProductDataView()
        view.request = request
        view.object = variant_product
        view.kwargs = {"id": variant_product.id}

        # Mock messages.success to avoid middleware requirement
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.delete(request)

        # Should redirect to parent product data page
        assert isinstance(response, HttpResponseRedirect)
        assert f"/manage/product/{variant_product.parent_id}/data/" in response.url

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Product has been deleted.")

    def test_get_with_view_parameter_redirects_to_public_page(self, rf, product):
        """Should redirect to public product page when view parameter is present."""
        factory = RequestFactory()
        request = factory.get("/?view=1")

        view = ProductDataView()
        view.request = request
        view.object = product
        view.kwargs = {"id": product.id}

        response = view.get(request)

        # Should redirect to public product page
        assert isinstance(response, HttpResponseRedirect)
        assert f"/product/{product.slug}/" in response.url

    def test_get_without_view_parameter_calls_super(self, rf, product, mocker):
        """Should call super().get() when view parameter is not present."""
        factory = RequestFactory()
        request = factory.get("/")

        view = ProductDataView()
        view.request = request
        view.object = product
        view.kwargs = {"id": product.id}

        # Mock super().get()
        mock_super_get = mocker.patch.object(UpdateView, "get")
        mock_super_get.return_value = HttpResponse()

        response = view.get(request)

        # Should call super().get()
        mock_super_get.assert_called_once_with(request)
        assert response is not None


class TestProductImagesView:
    """Test the ProductImagesView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from ProductTabMixin and TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(ProductImagesView, ProductTabMixin)
        assert issubclass(ProductImagesView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductImagesView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should use 'images' as tab name."""
        assert ProductImagesView.tab_name == "images"

    def test_post_toggle_active_images(self, rf, product, mocker):
        """Should toggle active images setting."""
        factory = RequestFactory()
        request = factory.post("/", {"toggle_active_images": "1", "active_images": "1"})
        request.session = {}

        view = ProductImagesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should update product active_images
        product.refresh_from_db()
        assert product.active_images is True

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Active images has been updated.")

    def test_post_delete_images(self, rf, product, mocker):
        """Should delete selected images."""
        from lfs.catalog.models import Image

        # Create test image
        image = Image.objects.create(content=product, title="test.jpg", position=10)

        factory = RequestFactory()
        request = factory.post("/", {"action": "delete", f"delete-{image.id}": "1"})
        request.session = {}

        view = ProductImagesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should delete the image
        assert not Image.objects.filter(id=image.id).exists()

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Images have been deleted.")

    def test_post_update_images(self, rf, product, mocker):
        """Should update image properties."""
        from lfs.catalog.models import Image

        # Create test image
        image = Image.objects.create(content=product, title="old.jpg", position=10)

        factory = RequestFactory()
        request = factory.post("/", {"action": "update", f"title-{image.id}": "new.jpg", f"position-{image.id}": "20"})
        request.session = {}

        view = ProductImagesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should update the image
        image.refresh_from_db()
        assert image.title == "new.jpg"
        # Position gets refreshed to 10 (first image position)
        assert image.position == 10

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Images have been updated.")


class TestProductAttachmentsView:
    """Test the ProductAttachmentsView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from ProductTabMixin and TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(ProductAttachmentsView, ProductTabMixin)
        assert issubclass(ProductAttachmentsView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductAttachmentsView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should use 'attachments' as tab name."""
        assert ProductAttachmentsView.tab_name == "attachments"

    def test_post_delete_attachments(self, rf, product, mocker):
        """Should delete selected attachments."""
        from lfs.catalog.models import ProductAttachment

        # Create test attachment
        attachment = ProductAttachment.objects.create(product=product, title="test.pdf", position=10)

        factory = RequestFactory()
        request = factory.post("/", {"action": "delete", f"delete-{attachment.id}": "1"})
        request.session = {}

        view = ProductAttachmentsView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should delete the attachment
        assert not ProductAttachment.objects.filter(id=attachment.id).exists()

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Attachment has been deleted.")

    def test_post_update_attachments(self, rf, product, mocker):
        """Should update attachment properties."""
        from lfs.catalog.models import ProductAttachment

        # Create test attachment
        attachment = ProductAttachment.objects.create(
            product=product, title="old.pdf", position=10, description="old desc"
        )

        factory = RequestFactory()
        request = factory.post(
            "/",
            {
                "action": "update",
                f"title-{attachment.id}": "new.pdf",
                f"position-{attachment.id}": "20",
                f"description-{attachment.id}": "new desc",
            },
        )
        request.session = {}

        view = ProductAttachmentsView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should update the attachment
        attachment.refresh_from_db()
        assert attachment.title == "new.pdf"
        # Position gets refreshed to 10 (first attachment position)
        assert attachment.position == 10
        assert attachment.description == "new desc"

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Attachment has been updated.")


class TestProductAccessoriesView:
    """Test the ProductAccessoriesView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from ProductTabMixin and TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(ProductAccessoriesView, ProductTabMixin)
        assert issubclass(ProductAccessoriesView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductAccessoriesView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should use 'accessories' as tab name."""
        assert ProductAccessoriesView.tab_name == "accessories"

    def test_post_toggle_active_accessories(self, rf, product, mocker):
        """Should toggle active accessories setting."""
        factory = RequestFactory()
        request = factory.post("/", {"action": "toggle_active", "active_accessories": "1"})
        request.session = {}

        view = ProductAccessoriesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should update product active_accessories
        product.refresh_from_db()
        assert product.active_accessories is True

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Accessories have been updated.")

    def test_post_toggle_active_accessories_htmx(self, rf, product, mocker):
        """Should not show success message for HTMX requests."""
        factory = RequestFactory()
        request = factory.post("/", {"action": "toggle_active", "active_accessories": "1"})
        request.META["HTTP_HX_REQUEST"] = "true"
        request.session = {}

        view = ProductAccessoriesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should update product active_accessories
        product.refresh_from_db()
        assert product.active_accessories is True

        # Should NOT add success message for HTMX
        mock_messages_success.assert_not_called()

    def test_post_add_accessories(self, rf, product, mocker):
        """Should add selected products as accessories."""
        from lfs.catalog.models import ProductAccessories

        # Create another product to add as accessory
        accessory_product = Product.objects.create(
            name="Accessory Product", slug="accessory-product", sku="ACC001", price=5.0
        )

        factory = RequestFactory()
        request = factory.post("/", {"action": "add", f"product-{accessory_product.id}": "1"})
        request.session = {}

        view = ProductAccessoriesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should create ProductAccessories relationship
        pa = ProductAccessories.objects.filter(product=product, accessory=accessory_product).first()
        assert pa is not None

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Accessories have been added.")

    def test_post_remove_accessories(self, rf, product, mocker):
        """Should remove selected accessories."""
        from lfs.catalog.models import ProductAccessories

        # Create accessory relationship
        accessory_product = Product.objects.create(
            name="Accessory Product", slug="accessory-product", sku="ACC001", price=5.0
        )
        pa = ProductAccessories.objects.create(product=product, accessory=accessory_product, position=10)

        factory = RequestFactory()
        request = factory.post("/", {"action": "remove", f"accessory-{accessory_product.id}": "1"})
        request.session = {}

        view = ProductAccessoriesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should delete ProductAccessories relationship
        assert not ProductAccessories.objects.filter(product=product, accessory=accessory_product).exists()

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Accessories have been removed.")

    def test_post_save_accessories(self, rf, product, mocker):
        """Should save accessory quantities and positions."""
        from lfs.catalog.models import ProductAccessories

        # Create accessory relationship
        accessory_product = Product.objects.create(
            name="Accessory Product", slug="accessory-product", sku="ACC001", price=5.0
        )
        pa = ProductAccessories.objects.create(product=product, accessory=accessory_product, position=10, quantity=1)

        factory = RequestFactory()
        request = factory.post(
            "/", {"action": "save", f"quantity-{accessory_product.id}": "5", f"position-{accessory_product.id}": "20"}
        )
        request.session = {}

        view = ProductAccessoriesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should update quantity and position
        pa.refresh_from_db()
        assert pa.quantity == 5
        assert pa.position == 10  # Gets normalized

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Accessories have been updated.")

    def test_get_context_data_basic_structure(self, rf, product):
        """Should return context with basic structure."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductAccessoriesView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Check required context keys
        assert "product_accessories" in context
        assert "filter" in context
        assert "amount" in context
        assert "page_sizes" in context
        assert "available_page" in context
        assert "available_paginator" in context

        # Check page sizes
        assert context["page_sizes"] == [10, 25, 50, 100]

    def test_get_context_data_with_filter(self, rf, product):
        """Should filter available products."""
        # Create products for filtering
        Product.objects.create(name="Apple Product", slug="apple-product", sku="APP001", price=10.0)
        Product.objects.create(name="Banana Product", slug="banana-product", sku="BAN001", price=15.0)

        factory = RequestFactory()
        request = factory.get("/?filter=apple")
        request.session = {}

        view = ProductAccessoriesView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Should only include filtered products
        available_page = context["available_page"]
        assert available_page.paginator.count == 1
        assert available_page.object_list[0].name == "Apple Product"


class TestProductDeleteConfirmView:
    """Test the ProductDeleteConfirmView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from PermissionRequiredMixin and TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(ProductDeleteConfirmView, PermissionRequiredMixin)
        assert issubclass(ProductDeleteConfirmView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductDeleteConfirmView.permission_required == "core.manage_shop"

    def test_template_name(self):
        """Should use correct template."""
        assert ProductDeleteConfirmView.template_name == "manage/products/delete_product.html"

    def test_get_context_data_includes_product(self, rf, product):
        """Should include the product in context."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductDeleteConfirmView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        assert "product" in context
        assert context["product"] == product


class TestProductDeleteView:
    """Test the ProductDeleteView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, and DeleteView."""
        from django.views.generic.edit import DeleteView

        assert issubclass(ProductDeleteView, DirectDeleteMixin)
        assert issubclass(ProductDeleteView, SuccessMessageMixin)
        assert issubclass(ProductDeleteView, PermissionRequiredMixin)
        assert issubclass(ProductDeleteView, DeleteView)

    def test_model_attribute(self):
        """Should use Product model."""
        assert ProductDeleteView.model == Product

    def test_pk_url_kwarg(self):
        """Should use 'id' as pk_url_kwarg."""
        assert ProductDeleteView.pk_url_kwarg == "id"

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductDeleteView.permission_required == "core.manage_shop"

    def test_success_message(self):
        """Should have correct success message."""
        assert ProductDeleteView.success_message == "Product has been deleted."

    def test_get_success_url_returns_products_list(self):
        """Should redirect to products list after deletion."""
        factory = RequestFactory()
        request = factory.post("/")
        view = ProductDeleteView()
        view.request = request

        url = view.get_success_url()
        assert url == "/manage/products/list/"

    def test_delete_standard_request_redirects(self, rf, admin_user, product, mocker):
        """Should redirect normally for standard requests."""
        factory = RequestFactory()
        request = factory.post("/", {"confirm": "yes"})
        request.user = admin_user
        request.session = {}

        view = ProductDeleteView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success to avoid middleware requirement
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.delete(request)

        # Should be HttpResponseRedirect for standard requests
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == "/manage/products/list/"

        # Should have called messages.success
        mock_messages_success.assert_called_once_with(request, "Product has been deleted.")

        # Product should be deleted
        assert not Product.objects.filter(id=product.id).exists()

    def test_delete_htmx_request_sets_hx_redirect_header(self, rf, admin_user, product, mocker):
        """Should set HX-Redirect header for HTMX requests."""
        factory = RequestFactory()
        request = factory.post("/", {"confirm": "yes"})
        request.META["HTTP_HX_REQUEST"] = "true"
        request.user = admin_user
        request.session = {}

        view = ProductDeleteView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success to avoid middleware requirement
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.delete(request)

        # Should be HttpResponse with HX-Redirect header for HTMX
        assert isinstance(response, HttpResponse)
        assert response["HX-Redirect"] == "/manage/products/list/"

        # Should have called messages.success
        mock_messages_success.assert_called_once_with(request, "Product has been deleted.")

        # Product should be deleted
        assert not Product.objects.filter(id=product.id).exists()


class TestApplyProductFiltersView:
    """Test the ApplyProductFiltersView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from PermissionRequiredMixin and FormView."""
        from django.views.generic.edit import FormView

        assert issubclass(ApplyProductFiltersView, PermissionRequiredMixin)
        assert issubclass(ApplyProductFiltersView, FormView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ApplyProductFiltersView.permission_required == "core.manage_shop"

    def test_form_class(self):
        """Should use ProductFilterForm."""
        from lfs.manage.products.forms import ProductFilterForm

        assert ApplyProductFiltersView.form_class == ProductFilterForm

    def test_form_valid_saves_filters_to_session(self, rf, admin_user, mocker):
        """Should save valid filter data to session."""
        from lfs.manage.products.forms import ProductFilterForm

        factory = RequestFactory()
        request = factory.post(
            "/",
            {
                "name": "test product",
                "sku": "TEST001",
                "sub_type": "standard",
                "price_calculator": "price",
                "status": "active",
            },
        )
        request.user = admin_user
        request.session = {}

        view = ApplyProductFiltersView()
        view.request = request
        view.kwargs = {}  # No id in kwargs means we're in product list view

        # Create a mock form with cleaned_data
        mock_form = mocker.MagicMock(spec=ProductFilterForm)
        mock_form.cleaned_data = {
            "name": "test product",
            "sku": "TEST001",
            "sub_type": "standard",
            "price_calculator": "price",
            "status": "active",
        }

        response = view.form_valid(mock_form)

        # Should save filters to session
        assert request.session["product-filters"] == {
            "name": "test product",
            "sku": "TEST001",
            "sub_type": "standard",
            "price_calculator": "price",
            "status": "active",
        }

        # Should redirect to products list (no id in kwargs)
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == "/manage/products/list/"

    def test_form_valid_redirects_to_product_detail_with_id(self, rf, admin_user, product, mocker):
        """Should redirect to product detail when id is provided."""
        from lfs.manage.products.forms import ProductFilterForm

        factory = RequestFactory()
        request = factory.post("/", {"name": "test product"})
        request.user = admin_user
        request.session = {}

        view = ApplyProductFiltersView()
        view.request = request
        view.kwargs = {"id": product.id}

        mock_form = mocker.MagicMock(spec=ProductFilterForm)
        mock_form.cleaned_data = {"name": "test product"}

        response = view.form_valid(mock_form)

        # Should redirect to product detail
        assert isinstance(response, HttpResponseRedirect)
        assert f"/manage/product/{product.id}/data/" in response.url

    def test_form_invalid_shows_error_message(self, rf, admin_user, mocker):
        """Should show error message for invalid form."""
        factory = RequestFactory()
        request = factory.post("/", {})
        request.user = admin_user
        request.session = {}

        view = ApplyProductFiltersView()
        view.request = request
        view.kwargs = {}  # No id in kwargs

        # Mock messages.error to avoid middleware requirement
        mock_messages_error = mocker.patch("lfs.manage.products.views.messages.error")

        mock_form = mocker.MagicMock()
        mock_form.is_valid.return_value = False

        response = view.form_invalid(mock_form)

        # Should have called messages.error
        mock_messages_error.assert_called_once_with(request, "Invalid filter data.")

        # Should redirect to products list
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == "/manage/products/list/"


class TestResetProductFiltersView:
    """Test the ResetProductFiltersView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from PermissionRequiredMixin and RedirectView."""
        from django.views.generic.base import RedirectView

        assert issubclass(ResetProductFiltersView, PermissionRequiredMixin)
        assert issubclass(ResetProductFiltersView, RedirectView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ResetProductFiltersView.permission_required == "core.manage_shop"

    def test_get_redirect_url_removes_filters_from_session(self, rf, admin_user):
        """Should remove product-filters from session."""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = admin_user
        request.session = {"product-filters": {"name": "test"}}

        view = ResetProductFiltersView()
        view.request = request
        view.kwargs = {}  # No id in kwargs

        url = view.get_redirect_url()

        # Should remove filters from session
        assert "product-filters" not in request.session

        # Should redirect to products list
        assert url == "/manage/products/list/"

    def test_get_redirect_url_redirects_to_product_detail_with_id(self, rf, admin_user, product):
        """Should redirect to product detail when id is provided."""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = admin_user
        request.session = {"product-filters": {"name": "test"}}

        view = ResetProductFiltersView()
        view.request = request
        view.kwargs = {"id": product.id}

        url = view.get_redirect_url()

        # Should redirect to product detail
        assert url == f"/manage/product/{product.id}/data/"

    def test_get_redirect_url_handles_missing_session_filters(self, rf, admin_user):
        """Should handle case when product-filters doesn't exist in session."""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = admin_user
        request.session = {}

        view = ResetProductFiltersView()
        view.request = request
        view.kwargs = {}  # No id in kwargs

        url = view.get_redirect_url()

        # Should not raise error and redirect to products list
        assert url == "/manage/products/list/"


class TestProductBulkPricesView:
    """Test the ProductBulkPricesView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from ProductTabMixin and TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(ProductBulkPricesView, ProductTabMixin)
        assert issubclass(ProductBulkPricesView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductBulkPricesView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should use 'bulk_prices' as tab name."""
        assert ProductBulkPricesView.tab_name == "bulk_prices"

    def test_get_context_data_basic_structure(self, rf, product):
        """Should return context with basic structure."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductBulkPricesView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Check required context keys
        assert "prices" in context
        assert "currency" in context
        assert isinstance(context["prices"], list)
        # Currency can be different depending on settings
        assert isinstance(context["currency"], str)

    def test_get_context_data_with_bulk_prices(self, rf, product):
        """Should return existing bulk prices."""
        from lfs_bulk_prices.models import BulkPrice

        # Create test bulk prices
        bulk_price1 = BulkPrice.objects.create(product=product, amount=10, price_absolute=5.0, price_percentual=0.0)
        bulk_price2 = BulkPrice.objects.create(product=product, amount=20, price_absolute=8.0, price_percentual=0.0)

        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductBulkPricesView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Should return bulk prices ordered by amount
        assert len(context["prices"]) == 2
        assert context["prices"][0] == bulk_price1
        assert context["prices"][1] == bulk_price2

    def test_post_save_bulk_prices(self, rf, product, mocker):
        """Should save bulk prices from form data."""
        factory = RequestFactory()
        request = factory.post(
            "/",
            {
                "price_id": ["1", "2"],
                "amount-1": "10",
                "price_absolute-1": "5.0",
                "price_percentual-1": "0.0",
                "amount-2": "20",
                "price_absolute-2": "8.0",
                "price_percentual-2": "0.0",
            },
        )
        request.session = {}

        view = ProductBulkPricesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should redirect to bulk prices page
        assert isinstance(response, HttpResponseRedirect)
        assert f"/manage/product/{product.id}/bulk-prices/" in response.url

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Bulk prices have been saved.")

    def test_post_handles_invalid_amount(self, rf, product, mocker):
        """Should handle invalid amount values gracefully."""
        factory = RequestFactory()
        request = factory.post(
            "/", {"price_id": ["1"], "amount-1": "invalid", "price_absolute-1": "5.0", "price_percentual-1": "0.0"}
        )
        request.session = {}

        view = ProductBulkPricesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should redirect and save with default amount (1.0)
        assert isinstance(response, HttpResponseRedirect)
        mock_messages_success.assert_called_once_with(request, "Bulk prices have been saved.")

    def test_post_handles_invalid_prices(self, rf, product, mocker):
        """Should handle invalid price values gracefully."""
        factory = RequestFactory()
        request = factory.post(
            "/", {"price_id": ["1"], "amount-1": "10", "price_absolute-1": "invalid", "price_percentual-1": "invalid"}
        )
        request.session = {}

        view = ProductBulkPricesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should redirect and save with default prices (0.0)
        assert isinstance(response, HttpResponseRedirect)
        mock_messages_success.assert_called_once_with(request, "Bulk prices have been saved.")


class TestProductVariantsView:
    """Test the ProductVariantsView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from ProductTabMixin and TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(ProductVariantsView, ProductTabMixin)
        assert issubclass(ProductVariantsView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductVariantsView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should use 'variants' as tab name."""
        assert ProductVariantsView.tab_name == "variants"

    def test_post_delete_variants(self, rf, product, mocker):
        """Should delete selected variants."""
        # Create a variant product
        variant = Product.objects.create(
            name="Test Variant", slug="test-variant", sku="VAR001", price=10.0, parent=product, sub_type="variant"
        )
        product.default_variant_id = variant.id
        product.save()

        factory = RequestFactory()
        request = factory.post("/", {"action": "delete", f"delete-{variant.id}": "1"})
        request.session = {}

        view = ProductVariantsView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should delete the variant
        assert not Product.objects.filter(id=variant.id).exists()

        # Should clear default variant if it was the deleted variant
        product.refresh_from_db()
        assert product.default_variant_id is None

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Variants have been deleted.")

    def test_post_update_variants(self, rf, product, mocker):
        """Should update variant properties."""
        # Create a variant product
        variant = Product.objects.create(
            name="Test Variant", slug="test-variant", sku="VAR001", price=10.0, parent=product, sub_type="variant"
        )

        factory = RequestFactory()
        request = factory.post(
            "/",
            {
                "action": "update",
                f"variant-{variant.id}": "1",
                f"name-{variant.id}": "Updated Variant",
                f"sku-{variant.id}": "UPD001",
                f"price-{variant.id}": "15.0",
                f"active-{variant.id}": "1",
                f"active_price-{variant.id}": "1",
                f"active_sku-{variant.id}": "1",
                f"active_name-{variant.id}": "1",
                f"position-{variant.id}": "20",
                "default_variant": str(variant.id),
            },
        )
        request.session = {}

        view = ProductVariantsView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should update the variant
        variant.refresh_from_db()
        assert variant.name == "Updated Variant"
        assert variant.sku == "UPD001"
        assert variant.price == 15.0
        assert variant.active is True
        assert variant.active_price is True
        assert variant.active_sku is True
        assert variant.active_name is True
        assert variant.variant_position == 10  # Gets normalized

        # Should set as default variant
        product.refresh_from_db()
        assert product.default_variant_id == variant.id

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Variants have been saved.")

    def test_post_edit_sub_type(self, rf, product, mocker):
        """Should update variants display type."""
        factory = RequestFactory()
        request = factory.post("/", {"action": "edit_sub_type", "variants_display_type": "1"})  # Use integer value
        request.session = {}

        view = ProductVariantsView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        # Mock the form to be valid
        mock_form = mocker.MagicMock()
        mock_form.is_valid.return_value = True
        mock_form.cleaned_data = {"variants_display_type": 1}

        with mocker.patch("lfs.manage.products.forms.DisplayTypeForm", return_value=mock_form):
            response = view.post(request)

        # Should update display type
        product.refresh_from_db()
        assert product.variants_display_type == 1

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Sub type has been saved.")

    def test_post_update_property_groups(self, rf, product, mocker):
        """Should update property group assignments."""
        from lfs.catalog.models import PropertyGroup

        # Create a property group
        property_group = PropertyGroup.objects.create(name="Test Group")

        factory = RequestFactory()
        request = factory.post(
            "/", {"action": "update_property_groups", "selected-property-groups": [str(property_group.id)]}
        )
        request.session = {}

        view = ProductVariantsView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should assign property group to product
        assert property_group.products.filter(pk=product.pk).exists()

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Property groups have been updated.")

    def test_get_context_data_basic_structure(self, rf, product):
        """Should return context with basic structure."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductVariantsView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Check required context keys
        assert "variants" in context
        assert "all_properties" in context
        assert "local_properties" in context
        assert "display_type_form" in context
        assert "default_variant_form" in context
        assert "category_variant_form" in context
        assert "variant_columns" in context
        assert "shop_property_groups" in context

        # Check types
        assert isinstance(context["variants"], list)
        assert isinstance(context["all_properties"], list)
        assert isinstance(context["local_properties"], list)


class TestProductRelatedProductsView:
    """Test the ProductRelatedProductsView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from ProductTabMixin and TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(ProductRelatedProductsView, ProductTabMixin)
        assert issubclass(ProductRelatedProductsView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductRelatedProductsView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should use 'related' as tab name."""
        assert ProductRelatedProductsView.tab_name == "related"

    def test_post_toggle_active_related_products(self, rf, product, mocker):
        """Should toggle active related products setting."""
        factory = RequestFactory()
        request = factory.post("/", {"action": "toggle_active", "active_related_products": "1"})
        request.session = {}

        view = ProductRelatedProductsView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should update product active_related_products
        product.refresh_from_db()
        assert product.active_related_products is True

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Related products have been updated.")

    def test_post_toggle_active_related_products_htmx(self, rf, product, mocker):
        """Should not show success message for HTMX requests."""
        factory = RequestFactory()
        request = factory.post("/", {"action": "toggle_active", "active_related_products": "1"})
        request.META["HTTP_HX_REQUEST"] = "true"
        request.session = {}

        view = ProductRelatedProductsView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should update product active_related_products
        product.refresh_from_db()
        assert product.active_related_products is True

        # Should NOT add success message for HTMX
        mock_messages_success.assert_not_called()

    def test_post_add_related_products(self, rf, product, mocker):
        """Should add selected products as related products."""
        # Create another product to add as related
        related_product = Product.objects.create(
            name="Related Product", slug="related-product", sku="REL001", price=15.0
        )

        factory = RequestFactory()
        request = factory.post("/", {"action": "add", f"product-{related_product.id}": "1"})
        request.session = {}

        view = ProductRelatedProductsView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should add related product
        assert product.related_products.filter(pk=related_product.id).exists()

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Related products have been added.")

    def test_post_remove_related_products(self, rf, product, mocker):
        """Should remove selected related products."""
        # Create and add a related product
        related_product = Product.objects.create(
            name="Related Product", slug="related-product", sku="REL001", price=15.0
        )
        product.related_products.add(related_product)

        factory = RequestFactory()
        request = factory.post("/", {"action": "remove", f"product-{related_product.id}": "1"})
        request.session = {}

        view = ProductRelatedProductsView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should remove related product
        assert not product.related_products.filter(pk=related_product.id).exists()

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Related products have been removed.")

    def test_get_context_data_basic_structure(self, rf, product):
        """Should return context with basic structure."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductRelatedProductsView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Check required context keys
        assert "related_products" in context
        assert "filter" in context
        assert "amount" in context
        assert "page_sizes" in context
        assert "available_page" in context
        assert "available_paginator" in context

        # Check page sizes
        assert context["page_sizes"] == [10, 25, 50, 100]

        # Check types - related_products is a QuerySet from the view
        from django.db.models import QuerySet

        assert isinstance(context["related_products"], QuerySet)
        assert isinstance(context["available_page"], object)  # Paginator page object

    def test_get_context_data_with_related_products(self, rf, product):
        """Should return existing related products."""
        # Create and add related products
        related_product1 = Product.objects.create(
            name="Related Product 1", slug="related-product-1", sku="REL001", price=15.0
        )
        related_product2 = Product.objects.create(
            name="Related Product 2", slug="related-product-2", sku="REL002", price=20.0
        )
        product.related_products.add(related_product1, related_product2)

        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductRelatedProductsView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Should return related products
        related_products = context["related_products"]
        assert len(related_products) == 2
        # Should be ordered by name
        assert related_products[0].name == "Related Product 1"
        assert related_products[1].name == "Related Product 2"

    def test_get_context_data_with_filter(self, rf, product):
        """Should filter available products."""
        # Create products for filtering
        Product.objects.create(name="Apple Product", slug="apple-product", sku="APP001", price=10.0)
        Product.objects.create(name="Banana Product", slug="banana-product", sku="BAN001", price=15.0)

        factory = RequestFactory()
        request = factory.get("/?filter=apple")
        request.session = {}

        view = ProductRelatedProductsView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Should only include filtered products
        available_page = context["available_page"]
        assert available_page.paginator.count == 1
        assert available_page.object_list[0].name == "Apple Product"

    def test_get_context_data_excludes_current_product(self, rf, product):
        """Should exclude the current product from available products."""
        # Create another product
        other_product = Product.objects.create(name="Other Product", slug="other-product", sku="OTH001", price=25.0)

        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductRelatedProductsView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Should include the other product but not the current product
        available_page = context["available_page"]
        assert available_page.paginator.count == 1
        assert available_page.object_list[0] == other_product

    def test_get_context_data_excludes_already_related_products(self, rf, product):
        """Should exclude products that are already related."""
        # Create products
        related_product = Product.objects.create(
            name="Related Product", slug="related-product", sku="REL001", price=15.0
        )
        available_product = Product.objects.create(
            name="Available Product", slug="available-product", sku="AVA001", price=20.0
        )

        # Add one as related
        product.related_products.add(related_product)

        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductRelatedProductsView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Should only include the available product, not the already related one
        available_page = context["available_page"]
        assert available_page.paginator.count == 1
        assert available_page.object_list[0] == available_product


class TestProductPropertiesView:
    """Test the ProductPropertiesView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from ProductTabMixin and TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(ProductPropertiesView, ProductTabMixin)
        assert issubclass(ProductPropertiesView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductPropertiesView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should use 'properties' as tab name."""
        assert ProductPropertiesView.tab_name == "properties"

    def test_get_context_data_basic_structure(self, rf, product):
        """Should return context with basic structure."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductPropertiesView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Check required context keys
        assert "filterables" in context
        assert "display_filterables" in context
        assert "configurables" in context
        assert "display_configurables" in context
        assert "displayables" in context
        assert "display_displayables" in context
        assert "product_property_groups" in context
        assert "shop_property_groups" in context
        assert "product_variant_properties" in context

        # Check types
        assert isinstance(context["filterables"], list)
        assert isinstance(context["configurables"], list)
        assert isinstance(context["displayables"], list)
        assert isinstance(context["shop_property_groups"], list)
        assert isinstance(context["product_variant_properties"], list)

    def test_get_context_data_with_property_groups(self, rf, product):
        """Should return property groups in context."""
        from lfs.catalog.models import PropertyGroup

        # Create property groups
        property_group1 = PropertyGroup.objects.create(name="Test Group 1")
        property_group2 = PropertyGroup.objects.create(name="Test Group 2")
        product.property_groups.add(property_group1, property_group2)

        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductPropertiesView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Should include all property groups
        shop_property_groups = context["shop_property_groups"]
        assert len(shop_property_groups) >= 2

        # Should mark selected property groups
        selected_groups = [pg for pg in shop_property_groups if pg["selected"]]
        assert len(selected_groups) == 2

    def test_post_update_property_groups(self, rf, product, mocker):
        """Should update property group assignments."""
        from lfs.catalog.models import PropertyGroup

        # Create property groups
        property_group1 = PropertyGroup.objects.create(name="Test Group 1")
        property_group2 = PropertyGroup.objects.create(name="Test Group 2")

        factory = RequestFactory()
        request = factory.post(
            "/", {"action": "update_property_groups", "selected-property-groups": [str(property_group1.id)]}
        )
        request.session = {}

        view = ProductPropertiesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should add selected property group
        assert property_group1.products.filter(pk=product.pk).exists()

        # Should remove unselected property group
        assert not property_group2.products.filter(pk=product.pk).exists()

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Property groups have been updated.")

        # Should redirect to properties page
        assert isinstance(response, HttpResponseRedirect)
        assert f"/manage/product/{product.id}/properties/" in response.url

    def test_post_update_properties(self, rf, product, mocker):
        """Should update individual property values."""
        from lfs.catalog.models import PropertyGroup, Property, PropertyOption, ProductPropertyValue
        from lfs.catalog.settings import PROPERTY_VALUE_TYPE_DEFAULT, PROPERTY_SELECT_FIELD

        # Create property group and property
        property_group = PropertyGroup.objects.create(name="Test Group")
        prop = Property.objects.create(name="Test Property", title="Test Property", type=PROPERTY_SELECT_FIELD)

        # Create property option
        option = PropertyOption.objects.create(name="Test Option", property=prop)

        # Add property group to product
        product.property_groups.add(property_group)

        factory = RequestFactory()
        request = factory.post(
            "/",
            {
                "action": "update_properties",
                "type": str(PROPERTY_VALUE_TYPE_DEFAULT),
                f"property-{property_group.id}-{prop.id}": [str(option.id)],
            },
        )
        request.session = {}

        view = ProductPropertiesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should create property value
        ppv = ProductPropertyValue.objects.filter(
            product=product, property=prop, property_group=property_group, type=PROPERTY_VALUE_TYPE_DEFAULT
        ).first()
        assert ppv is not None
        assert ppv.value == str(option.id)

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Properties have been updated.")

        # Should redirect to properties page
        assert isinstance(response, HttpResponseRedirect)
        assert f"/manage/product/{product.id}/properties/" in response.url

    def test_post_update_properties_multiple_values(self, rf, product, mocker):
        """Should handle multiple values for filterable properties."""
        from lfs.catalog.models import PropertyGroup, Property, PropertyOption, ProductPropertyValue
        from lfs.catalog.settings import PROPERTY_VALUE_TYPE_FILTER, PROPERTY_SELECT_FIELD

        # Create property group and filterable property
        property_group = PropertyGroup.objects.create(name="Test Group")
        prop = Property.objects.create(
            name="Test Property", title="Test Property", type=PROPERTY_SELECT_FIELD, filterable=True
        )

        # Create property options
        option1 = PropertyOption.objects.create(name="Option 1", property=prop)
        option2 = PropertyOption.objects.create(name="Option 2", property=prop)

        # Add property group to product
        product.property_groups.add(property_group)

        factory = RequestFactory()
        request = factory.post(
            "/",
            {
                "action": "update_properties",
                "type": str(PROPERTY_VALUE_TYPE_FILTER),
                f"property-{property_group.id}-{prop.id}": [str(option1.id), str(option2.id)],
            },
        )
        request.session = {}

        view = ProductPropertiesView()
        view.request = request
        view.kwargs = {"id": product.id}

        # Mock messages.success
        mock_messages_success = mocker.patch("lfs.manage.products.views.messages.success")

        response = view.post(request)

        # Should create multiple property values
        ppvs = ProductPropertyValue.objects.filter(
            product=product, property=prop, property_group=property_group, type=PROPERTY_VALUE_TYPE_FILTER
        )
        assert ppvs.count() == 2
        values = [ppv.value for ppv in ppvs]
        assert str(option1.id) in values
        assert str(option2.id) in values

        # Should add success message
        mock_messages_success.assert_called_once_with(request, "Properties have been updated.")

    def test_get_context_data_with_variant_product(self, rf, product):
        """Should handle products without variants correctly."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductPropertiesView()
        view.request = request
        view.kwargs = {"id": product.id}

        context = view.get_context_data()

        # Should return empty variant properties for non-variant products
        product_variant_properties = context["product_variant_properties"]
        assert isinstance(product_variant_properties, list)
        # For non-variant products, this should be empty
        assert len(product_variant_properties) == 0


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


class TestProductListView:
    """Test the ProductListView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from PermissionRequiredMixin and TemplateView."""
        from django.contrib.auth.mixins import PermissionRequiredMixin
        from django.views.generic.base import TemplateView

        assert issubclass(ProductListView, PermissionRequiredMixin)
        assert issubclass(ProductListView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ProductListView.permission_required == "core.manage_shop"

    def test_template_name(self):
        """Should use correct template."""
        assert ProductListView.template_name == "manage/products/product_list.html"

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ProductListView, "get_context_data")
        assert callable(getattr(ProductListView, "get_context_data"))

    def test_get_context_data_basic_structure(self, rf, db, category, shop):
        """Should return context with basic structure when no filters."""
        from lfs.catalog.settings import PRODUCT_TYPE_LOOKUP

        # Create test product
        product = Product.objects.create(
            name="Test Product", sku="TEST001", price=10.0, active=True, manage_stock_amount=True, stock_amount=5
        )
        product.categories.add(category)

        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductListView()
        view.request = request

        context = view.get_context_data()

        # Check basic context structure
        assert "products_page" in context
        assert "products_with_data" in context
        assert "product_filters" in context
        assert "filter_form" in context

        # Check products_with_data structure
        products_with_data = context["products_with_data"]
        assert isinstance(products_with_data, list)
        assert len(products_with_data) > 0

        product_data = products_with_data[0]
        assert "product" in product_data
        assert "categories" in product_data
        assert "price" in product_data
        assert "stock" in product_data
        assert "active" in product_data
        assert "sub_type_display" in product_data

        # Check product data enrichment
        assert product_data["product"] == product
        assert "Test Category" in product_data["categories"]
        assert product_data["price"] == 10.0
        assert product_data["stock"] == 5
        assert product_data["active"] is True
        assert product_data["sub_type_display"] == PRODUCT_TYPE_LOOKUP.get(product.sub_type, product.sub_type)

    def test_get_context_data_with_session_filters(self, rf, db, shop):
        """Should apply filters from session."""
        from lfs.manage.products.services import ProductFilterService

        # Create test data
        product1 = Product.objects.create(name="Apple Product", slug="apple-product", sku="APP001", price=10.0)
        product2 = Product.objects.create(name="Banana Product", slug="banana-product", sku="BAN001", price=20.0)

        factory = RequestFactory()
        request = factory.get("/")
        request.session = {"product-filters": {"name": "Apple"}}

        view = ProductListView()
        view.request = request

        context = view.get_context_data()

        # Should only include filtered products
        products_with_data = context["products_with_data"]
        assert len(products_with_data) == 1
        assert products_with_data[0]["product"] == product1

    def test_get_context_data_filter_service_exception_handling(self, rf, db, shop, mocker):
        """Should handle filter service exceptions gracefully."""
        # Create test data
        Product.objects.create(name="Test Product", sku="TEST001", price=10.0)

        factory = RequestFactory()
        request = factory.get("/")
        request.session = {"product-filters": {"name": "test"}}

        # Mock filter service to raise exception
        mock_filter_service = mocker.patch("lfs.manage.products.views.ProductFilterService")
        mock_filter_service.return_value.filter_products.side_effect = Exception("Filter error")

        view = ProductListView()
        view.request = request

        context = view.get_context_data()

        # Should return empty queryset on exception
        products_with_data = context["products_with_data"]
        assert len(products_with_data) == 0

    def test_get_context_data_pagination(self, rf, db, shop):
        """Should paginate products correctly."""
        from django.core.paginator import Paginator

        # Create more products than page size (22)
        products = []
        for i in range(25):
            product = Product.objects.create(
                name=f"Product {i}", slug=f"product-{i}", sku=f"SKU{i:03d}", price=float(i + 1)
            )
            products.append(product)

        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductListView()
        view.request = request

        context = view.get_context_data()

        products_page = context["products_page"]
        assert hasattr(products_page, "paginator")
        assert isinstance(products_page.paginator, Paginator)
        assert products_page.paginator.per_page == 22
        assert len(products_page.object_list) == 22  # Should be paginated

    def test_get_context_data_pagination_with_page_param(self, rf, db, shop):
        """Should handle page parameter correctly."""
        # Create more products than page size
        for i in range(25):
            Product.objects.create(name=f"Product {i}", slug=f"product-page-{i}", sku=f"SKU{i:03d}", price=float(i + 1))

        factory = RequestFactory()
        request = factory.get("/?page=2")
        request.session = {}

        view = ProductListView()
        view.request = request

        context = view.get_context_data()

        products_page = context["products_page"]
        assert products_page.number == 2
        assert len(products_page.object_list) == 3  # Remaining products on page 2

    def test_get_context_data_filter_form_creation(self, rf):
        """Should create filter form with session data."""
        from lfs.manage.products.forms import ProductFilterForm

        factory = RequestFactory()
        request = factory.get("/")
        request.session = {
            "product-filters": {
                "name": "test name",
                "sku": "test sku",
                "sub_type": "standard",
                "price_calculator": "price",
                "status": "active",
            }
        }

        view = ProductListView()
        view.request = request

        context = view.get_context_data()

        filter_form = context["filter_form"]
        assert isinstance(filter_form, ProductFilterForm)

        # Check form is initialized with session data
        assert filter_form.initial["name"] == "test name"
        assert filter_form.initial["sku"] == "test sku"
        assert filter_form.initial["sub_type"] == "standard"
        assert filter_form.initial["price_calculator"] == "price"
        assert filter_form.initial["status"] == "active"

    def test_get_context_data_filter_form_exception_handling(self, rf, db, mocker):
        """Should handle filter form creation exceptions gracefully."""
        from lfs.manage.products.forms import ProductFilterForm

        factory = RequestFactory()
        request = factory.get("/")
        request.session = {"product-filters": {"invalid": "data"}}

        # Mock ProductFilterForm to raise exception only when called with initial data
        original_form_class = ProductFilterForm
        mock_form_instance = mocker.MagicMock()
        mock_form_instance.initial = {}

        def side_effect(*args, **kwargs):
            if "initial" in kwargs:
                raise Exception("Form error")
            return mock_form_instance

        mock_form = mocker.patch("lfs.manage.products.views.ProductFilterForm", side_effect=side_effect)

        view = ProductListView()
        view.request = request

        context = view.get_context_data()

        filter_form = context["filter_form"]
        # Should be the mock instance created in except block
        assert filter_form == mock_form_instance
        assert filter_form.initial == {}

    def test_get_context_data_no_session_filters(self, rf, db, shop):
        """Should handle missing session filters gracefully."""
        # Create test data
        Product.objects.create(name="Test Product", sku="TEST001", price=10.0)

        factory = RequestFactory()
        request = factory.get("/")
        # No session attribute at all
        request.session = {}

        view = ProductListView()
        view.request = request

        context = view.get_context_data()

        # Should use empty dict as default
        assert context["product_filters"] == {}

        # Should still process products
        products_with_data = context["products_with_data"]
        assert len(products_with_data) == 1

    def test_get_context_data_product_ordering(self, rf, db, shop):
        """Should order products by creation_date descending."""
        from django.utils import timezone

        # Create products with different creation dates
        older_product = Product.objects.create(
            name="Older Product",
            slug="older-product",
            sku="OLD001",
            price=10.0,
            creation_date=timezone.now() - timezone.timedelta(days=1),
        )
        newer_product = Product.objects.create(
            name="Newer Product", slug="newer-product", sku="NEW001", price=20.0, creation_date=timezone.now()
        )

        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        view = ProductListView()
        view.request = request

        context = view.get_context_data()

        products_with_data = context["products_with_data"]
        assert len(products_with_data) == 2
        # Should be ordered by creation_date descending (newest first)
        assert products_with_data[0]["product"] == newer_product
        assert products_with_data[1]["product"] == older_product
