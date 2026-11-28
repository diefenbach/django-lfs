from unittest.mock import Mock, patch

from django.apps import apps
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

        tab_names = [tab[0] for tab in tabs]
        expected_tabs = ["data", "default_values", "order_numbers", "seo", "portlets"]
        if apps.is_installed("lfs_carousel"):
            expected_tabs.append("carousel")
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
