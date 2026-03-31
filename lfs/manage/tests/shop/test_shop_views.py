from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.core.models import Shop
from lfs.manage.shop.views import (
    ShopTabMixin,
    ShopDataView,
    ShopDefaultValuesView,
    ShopOrderNumbersView,
    ShopSEOTabView,
    ShopPortletsView,
    ShopCarouselView,
)

User = get_user_model()


class TestShopTabMixin:
    """Test the ShopTabMixin functionality."""

    def test_mixin_has_template_name(self):
        """Should have correct template name."""
        assert ShopTabMixin.template_name == "manage/shop/shop.html"

    def test_mixin_has_tab_name_attribute(self):
        """Should have tab_name attribute."""
        assert hasattr(ShopTabMixin, "tab_name")

    def test_get_shop_method_exists(self):
        """Should have get_shop method."""
        assert hasattr(ShopTabMixin, "get_shop")
        assert callable(getattr(ShopTabMixin, "get_shop"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ShopTabMixin, "get_context_data")
        assert callable(getattr(ShopTabMixin, "get_context_data"))

    def test_get_tabs_method_exists(self):
        """Should have _get_tabs method."""
        assert hasattr(ShopTabMixin, "_get_tabs")
        assert callable(getattr(ShopTabMixin, "_get_tabs"))

    def test_get_shop_returns_default_shop(self, shop):
        """Should return default shop instance."""
        mixin = ShopTabMixin()
        result = mixin.get_shop()
        assert isinstance(result, Shop)
        assert result.name == "Test Shop"

    def test_get_tabs_returns_correct_tabs(self):
        """Should return correct tab navigation."""
        mixin = ShopTabMixin()
        tabs = mixin._get_tabs(shop=None)

        assert isinstance(tabs, list)
        assert len(tabs) == 6

        tab_names = [tab[0] for tab in tabs]
        expected_tabs = ["data", "default_values", "order_numbers", "seo", "portlets", "carousel"]
        assert tab_names == expected_tabs

    def test_get_context_data_includes_shop_and_tabs(self, shop):
        """Should include shop and tabs in context."""
        from django.views.generic import TemplateView

        class TestView(ShopTabMixin, TemplateView):
            pass

        mixin = TestView()
        mixin.tab_name = "data"
        mixin.object = shop

        context = mixin.get_context_data()

        assert "shop" in context
        assert "active_tab" in context
        assert "tabs" in context
        assert context["shop"].id == shop.id
        assert context["active_tab"] == "data"
        assert isinstance(context["tabs"], list)


class TestShopDataView:
    """Test the ShopDataView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from correct mixins and views."""
        from django.views.generic import UpdateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShopDataView, PermissionRequiredMixin)
        assert issubclass(ShopDataView, ShopTabMixin)
        assert issubclass(ShopDataView, UpdateView)

    def test_model_attribute(self):
        """Should use Shop model."""
        assert ShopDataView.model == Shop

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShopDataView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should have correct tab name."""
        assert ShopDataView.tab_name == "data"

    def test_form_class_attribute(self):
        """Should have form_class attribute."""
        from lfs.manage.shop.forms import ShopDataForm

        assert ShopDataView.form_class == ShopDataForm

    def test_get_object_method_exists(self):
        """Should have get_object method."""
        assert hasattr(ShopDataView, "get_object")
        assert callable(getattr(ShopDataView, "get_object"))

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(ShopDataView, "get_success_url")
        assert callable(getattr(ShopDataView, "get_success_url"))

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(ShopDataView, "form_valid")
        assert callable(getattr(ShopDataView, "form_valid"))

    def test_get_object_returns_shop(self, shop):
        """Should return shop instance."""
        view = ShopDataView()
        result = view.get_object()
        assert isinstance(result, Shop)

    def test_get_success_url_returns_data_url(self):
        """Should return shop data URL."""
        view = ShopDataView()
        url = view.get_success_url()
        assert url == reverse("lfs_manage_shop_data")


class TestShopDefaultValuesView:
    """Test the ShopDefaultValuesView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from correct mixins and views."""
        from django.views.generic import UpdateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShopDefaultValuesView, PermissionRequiredMixin)
        assert issubclass(ShopDefaultValuesView, ShopTabMixin)
        assert issubclass(ShopDefaultValuesView, UpdateView)

    def test_model_attribute(self):
        """Should use Shop model."""
        assert ShopDefaultValuesView.model == Shop

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShopDefaultValuesView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should have correct tab name."""
        assert ShopDefaultValuesView.tab_name == "default_values"

    def test_form_class_attribute(self):
        """Should have form_class attribute."""
        from lfs.manage.shop.forms import ShopDefaultValuesForm

        assert ShopDefaultValuesView.form_class == ShopDefaultValuesForm

    def test_get_object_method_exists(self):
        """Should have get_object method."""
        assert hasattr(ShopDefaultValuesView, "get_object")
        assert callable(getattr(ShopDefaultValuesView, "get_object"))

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(ShopDefaultValuesView, "get_success_url")
        assert callable(getattr(ShopDefaultValuesView, "get_success_url"))

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(ShopDefaultValuesView, "form_valid")
        assert callable(getattr(ShopDefaultValuesView, "form_valid"))

    def test_get_object_returns_shop(self, shop):
        """Should return shop instance."""
        view = ShopDefaultValuesView()
        result = view.get_object()
        assert isinstance(result, Shop)

    def test_get_success_url_returns_default_values_url(self):
        """Should return shop default values URL."""
        view = ShopDefaultValuesView()
        url = view.get_success_url()
        assert url == reverse("lfs_manage_shop_default_values")


class TestShopOrderNumbersView:
    """Test the ShopOrderNumbersView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from correct mixins and views."""
        from django.views.generic import TemplateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShopOrderNumbersView, PermissionRequiredMixin)
        assert issubclass(ShopOrderNumbersView, ShopTabMixin)
        assert issubclass(ShopOrderNumbersView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShopOrderNumbersView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should have correct tab name."""
        assert ShopOrderNumbersView.tab_name == "order_numbers"

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ShopOrderNumbersView, "get_context_data")
        assert callable(getattr(ShopOrderNumbersView, "get_context_data"))

    def test_post_method_exists(self):
        """Should have post method."""
        assert hasattr(ShopOrderNumbersView, "post")
        assert callable(getattr(ShopOrderNumbersView, "post"))

    @patch("lfs.manage.shop.views.import_symbol")
    def test_get_context_data_includes_order_numbers_form(self, mock_import_symbol, shop):
        """Should include order numbers form in context."""
        mock_ong = Mock()
        mock_order_number = Mock()
        mock_order_number.id = "order_number"
        mock_order_number.get_form.return_value = Mock()
        mock_ong.objects.get.return_value = mock_order_number
        mock_import_symbol.return_value = mock_ong

        view = ShopOrderNumbersView()
        context = view.get_context_data()

        assert "order_numbers_form" in context
        assert "shop" in context
        # The view returns the default shop, not necessarily the shop fixture
        assert isinstance(context["shop"], Shop)

    @patch("lfs.manage.shop.views.import_symbol")
    def test_get_context_data_creates_order_number_if_not_exists(self, mock_import_symbol, shop):
        """Should create order number if it doesn't exist."""
        from django.core.exceptions import ObjectDoesNotExist

        mock_ong = Mock()
        mock_order_number = Mock()
        mock_order_number.id = "order_number"
        mock_order_number.get_form.return_value = Mock()
        mock_ong.objects.get.side_effect = ObjectDoesNotExist()
        mock_ong.objects.create.return_value = mock_order_number
        mock_ong.DoesNotExist = ObjectDoesNotExist
        mock_import_symbol.return_value = mock_ong

        view = ShopOrderNumbersView()
        context = view.get_context_data()

        assert "order_numbers_form" in context
        mock_ong.objects.create.assert_called_once_with(id="order_number")


class TestShopSEOTabView:
    """Test the ShopSEOTabView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from correct mixins and views."""
        from django.views.generic import UpdateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShopSEOTabView, PermissionRequiredMixin)
        assert issubclass(ShopSEOTabView, ShopTabMixin)
        assert issubclass(ShopSEOTabView, UpdateView)

    def test_model_attribute(self):
        """Should use Shop model."""
        assert ShopSEOTabView.model == Shop

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShopSEOTabView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should have correct tab name."""
        assert ShopSEOTabView.tab_name == "seo"

    def test_fields_attribute(self):
        """Should define correct fields."""
        expected_fields = ["meta_title", "meta_description", "meta_keywords"]
        assert ShopSEOTabView.fields == expected_fields

    def test_get_object_method_exists(self):
        """Should have get_object method."""
        assert hasattr(ShopSEOTabView, "get_object")
        assert callable(getattr(ShopSEOTabView, "get_object"))

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(ShopSEOTabView, "get_success_url")
        assert callable(getattr(ShopSEOTabView, "get_success_url"))

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(ShopSEOTabView, "form_valid")
        assert callable(getattr(ShopSEOTabView, "form_valid"))

    def test_get_object_returns_shop(self, shop):
        """Should return shop instance."""
        view = ShopSEOTabView()
        result = view.get_object()
        assert isinstance(result, Shop)

    def test_get_success_url_returns_seo_url(self):
        """Should return shop SEO URL."""
        view = ShopSEOTabView()
        url = view.get_success_url()
        assert url == reverse("lfs_manage_shop_seo")


class TestShopPortletsView:
    """Test the ShopPortletsView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from correct mixins and views."""
        from django.views.generic import TemplateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShopPortletsView, PermissionRequiredMixin)
        assert issubclass(ShopPortletsView, ShopTabMixin)
        assert issubclass(ShopPortletsView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShopPortletsView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should have correct tab name."""
        assert ShopPortletsView.tab_name == "portlets"

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ShopPortletsView, "get_context_data")
        assert callable(getattr(ShopPortletsView, "get_context_data"))

    @patch("lfs.manage.shop.views.PortletsInlineView")
    def test_get_context_data_includes_portlets(self, mock_portlets_view, shop):
        """Should include portlets in context."""
        mock_instance = Mock()
        mock_instance.get.return_value = {"portlets": []}
        mock_portlets_view.return_value = mock_instance

        view = ShopPortletsView()
        view.request = Mock()
        context = view.get_context_data()

        assert "portlets" in context
        assert "shop" in context
        # The view returns the default shop, not necessarily the shop fixture
        assert isinstance(context["shop"], Shop)


class TestShopCarouselView:
    """Test the ShopCarouselView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from correct mixins and views."""
        from django.views.generic import TemplateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShopCarouselView, PermissionRequiredMixin)
        assert issubclass(ShopCarouselView, ShopTabMixin)
        assert issubclass(ShopCarouselView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShopCarouselView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should have correct tab name."""
        assert ShopCarouselView.tab_name == "carousel"

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ShopCarouselView, "get_context_data")
        assert callable(getattr(ShopCarouselView, "get_context_data"))

    def test_get_context_data_includes_shop(self, shop):
        """Should include shop in context."""
        view = ShopCarouselView()
        context = view.get_context_data()

        assert "shop" in context
        # The view returns the default shop, not necessarily the shop fixture
        assert isinstance(context["shop"], Shop)


class TestShopViewIntegration:
    """Integration tests for shop views."""

    def test_all_views_require_permission(self):
        """All shop views should require core.manage_shop permission."""
        views = [
            ShopDataView,
            ShopDefaultValuesView,
            ShopOrderNumbersView,
            ShopSEOTabView,
            ShopPortletsView,
            ShopCarouselView,
        ]

        for view in views:
            assert hasattr(view, "permission_required")
            assert view.permission_required == "core.manage_shop"

    def test_all_views_inherit_shop_tab_mixin(self):
        """All shop views should inherit from ShopTabMixin."""
        views = [
            ShopDataView,
            ShopDefaultValuesView,
            ShopOrderNumbersView,
            ShopSEOTabView,
            ShopPortletsView,
            ShopCarouselView,
        ]

        for view in views:
            assert issubclass(view, ShopTabMixin)

    def test_all_views_have_unique_tab_names(self):
        """All shop views should have unique tab names."""
        views = [
            ShopDataView,
            ShopDefaultValuesView,
            ShopOrderNumbersView,
            ShopSEOTabView,
            ShopPortletsView,
            ShopCarouselView,
        ]

        tab_names = [view.tab_name for view in views]
        assert len(tab_names) == len(set(tab_names)), "Tab names should be unique"
