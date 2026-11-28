from django.http import HttpResponseRedirect

from lfs.shipping.models import ShippingMethod, ShippingMethodPrice
from lfs.manage.shipping_methods.views import (
    ManageShippingView,
    ShippingMethodPricesView,
    ShippingMethodTabMixin,
)


class TestManageShippingView:
    """Test the ManageShippingView dispatcher."""


    def test_redirects_to_first_shipping_method_when_methods_exist(self, shipping_method, mock_request, monkeypatch):
        """Should redirect to first shipping method when methods exist."""

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_manage_shipping_method" and kwargs and kwargs.get("id") == shipping_method.id:
                return f"/manage/shipping-method/{shipping_method.id}/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.shipping_methods.views.reverse", mock_reverse)

        view = ManageShippingView()
        response = view.get_redirect_url()

        assert f"/manage/shipping-method/{shipping_method.id}/" in response

    def test_redirects_to_no_shipping_methods_when_none_exist(self, mock_request, monkeypatch):
        """Should redirect to no shipping methods view when no methods exist."""
        # Delete all shipping methods
        ShippingMethod.objects.all().delete()

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_manage_no_shipping_methods":
                return "/manage/shipping-methods/no/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.shipping_methods.views.reverse", mock_reverse)

        view = ManageShippingView()
        response = view.get_redirect_url()

        assert response == "/manage/shipping-methods/no/"



class TestShippingMethodTabMixin:
    """Test the ShippingMethodTabMixin functionality."""

    def test_mixin_has_template_name(self):
        """Should have template_name attribute."""
        assert hasattr(ShippingMethodTabMixin, "template_name")
        assert ShippingMethodTabMixin.template_name == "manage/shipping_methods/shipping_method.html"

    def test_mixin_has_tab_name(self):
        """Should have tab_name attribute."""
        assert hasattr(ShippingMethodTabMixin, "tab_name")
        assert ShippingMethodTabMixin.tab_name is None













class TestShippingMethodPriceOperations:
    """Test shipping method price operations functionality."""

    def test_add_price_with_valid_data(self, shipping_method, mock_request):
        """Should add price with valid data."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        # Add message storage to request
        setattr(mock_request, "_messages", FallbackStorage(mock_request))

        mock_request.POST = {"add_price": "1", "price": "15.99"}

        view = ShippingMethodPricesView()
        view.kwargs = {"id": shipping_method.id}
        view.request = mock_request

        response = view._handle_add_price(mock_request)

        assert isinstance(response, HttpResponseRedirect)
        assert ShippingMethodPrice.objects.filter(shipping_method=shipping_method, price=15.99).exists()

    def test_add_price_with_negative_value(self, shipping_method, mock_request):
        """Should reject negative price values."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        # Add message storage to request
        setattr(mock_request, "_messages", FallbackStorage(mock_request))

        mock_request.POST = {"add_price": "1", "price": "-5.99"}

        view = ShippingMethodPricesView()
        view.kwargs = {"id": shipping_method.id}
        view.request = mock_request

        response = view._handle_add_price(mock_request)

        assert isinstance(response, HttpResponseRedirect)
        assert not ShippingMethodPrice.objects.filter(shipping_method=shipping_method, price=-5.99).exists()

    def test_add_price_with_invalid_value(self, shipping_method, mock_request):
        """Should handle invalid price values gracefully."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        # Add message storage to request
        setattr(mock_request, "_messages", FallbackStorage(mock_request))

        mock_request.POST = {"add_price": "1", "price": "invalid"}

        view = ShippingMethodPricesView()
        view.kwargs = {"id": shipping_method.id}
        view.request = mock_request

        response = view._handle_add_price(mock_request)

        assert isinstance(response, HttpResponseRedirect)
        # Should create price with 0.0 for invalid values
        assert ShippingMethodPrice.objects.filter(shipping_method=shipping_method, price=0.0).exists()

    def test_update_price_positions(self, shipping_method, multiple_shipping_prices):
        """Should update price positions correctly."""
        view = ShippingMethodPricesView()

        # Mess up the positions first
        for i, price in enumerate(multiple_shipping_prices):
            price.priority = 999 - i
            price.save()

        view._update_price_positions(shipping_method)

        # Check that priorities are updated correctly in order
        prices = list(shipping_method.prices.all())
        for i, price in enumerate(prices):
            assert price.priority == (i + 1) * 10

    def test_delete_prices_action(self, shipping_method, multiple_shipping_prices, mock_request):
        """Should delete selected prices."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        # Add message storage to request
        setattr(mock_request, "_messages", FallbackStorage(mock_request))

        price_to_delete = multiple_shipping_prices[0]
        mock_request.POST = {"action": "delete", f"delete-{price_to_delete.id}": "1"}

        view = ShippingMethodPricesView()
        view.kwargs = {"id": shipping_method.id}
        view.request = mock_request

        response = view._handle_update_prices(mock_request)

        assert isinstance(response, HttpResponseRedirect)
        assert not ShippingMethodPrice.objects.filter(id=price_to_delete.id).exists()

    def test_update_prices_action(self, shipping_method, multiple_shipping_prices, mock_request):
        """Should update selected prices."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        # Add message storage to request
        setattr(mock_request, "_messages", FallbackStorage(mock_request))

        price_to_update = multiple_shipping_prices[0]
        new_price = 25.99
        new_priority = 5

        mock_request.POST = {
            "action": "update",
            f"price-{price_to_update.id}": str(new_price),
            f"priority-{price_to_update.id}": str(new_priority),
        }

        view = ShippingMethodPricesView()
        view.kwargs = {"id": shipping_method.id}
        view.request = mock_request

        response = view._handle_update_prices(mock_request)

        assert isinstance(response, HttpResponseRedirect)
        price_to_update.refresh_from_db()
        assert price_to_update.price == new_price
        # Priority gets overwritten by _update_price_positions, so check it's in the expected range
        assert price_to_update.priority in [10, 20, 30]
