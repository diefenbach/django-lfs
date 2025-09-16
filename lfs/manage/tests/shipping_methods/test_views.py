from django.http import HttpResponseRedirect

from lfs.shipping.models import ShippingMethod, ShippingMethodPrice
from lfs.manage.shipping_methods.views import (
    ManageShippingView,
    NoShippingMethodsView,
    ShippingMethodDataView,
    ShippingMethodCriteriaView,
    ShippingMethodPricesView,
    ShippingMethodCreateView,
    ShippingMethodDeleteConfirmView,
    ShippingMethodDeleteView,
    ShippingMethodPriceCriteriaView,
    ShippingMethodPriceCriteriaSaveView,
    ShippingMethodTabMixin,
)


class TestManageShippingView:
    """Test the ManageShippingView dispatcher."""

    def test_view_inheritance(self):
        """Should inherit from Django RedirectView."""
        from django.views.generic import RedirectView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ManageShippingView, RedirectView)
        assert issubclass(ManageShippingView, PermissionRequiredMixin)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManageShippingView.permission_required == "core.manage_shop"

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


class TestNoShippingMethodsView:
    """Test the NoShippingMethodsView template view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(NoShippingMethodsView, TemplateView)
        assert issubclass(NoShippingMethodsView, PermissionRequiredMixin)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert NoShippingMethodsView.permission_required == "core.manage_shop"

    def test_template_name(self):
        """Should use correct template."""
        assert NoShippingMethodsView.template_name == "manage/shipping_methods/no_shipping_methods.html"


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

    def test_get_shipping_method_method_exists(self):
        """Should have get_shipping_method method."""
        assert hasattr(ShippingMethodTabMixin, "get_shipping_method")
        assert callable(getattr(ShippingMethodTabMixin, "get_shipping_method"))

    def test_get_shipping_methods_queryset_method_exists(self):
        """Should have get_shipping_methods_queryset method."""
        assert hasattr(ShippingMethodTabMixin, "get_shipping_methods_queryset")
        assert callable(getattr(ShippingMethodTabMixin, "get_shipping_methods_queryset"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ShippingMethodTabMixin, "get_context_data")
        assert callable(getattr(ShippingMethodTabMixin, "get_context_data"))

    def test_get_tabs_method_exists(self):
        """Should have _get_tabs method."""
        assert hasattr(ShippingMethodTabMixin, "_get_tabs")
        assert callable(getattr(ShippingMethodTabMixin, "_get_tabs"))


class TestShippingMethodDataView:
    """Test the ShippingMethodDataView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django UpdateView."""
        from django.views.generic.edit import UpdateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShippingMethodDataView, UpdateView)
        assert issubclass(ShippingMethodDataView, PermissionRequiredMixin)
        assert issubclass(ShippingMethodDataView, ShippingMethodTabMixin)

    def test_model_attribute(self):
        """Should use ShippingMethod model."""
        assert ShippingMethodDataView.model == ShippingMethod

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShippingMethodDataView.permission_required == "core.manage_shop"

    def test_form_class(self):
        """Should use ShippingMethodForm."""
        from lfs.manage.shipping_methods.forms import ShippingMethodForm

        assert ShippingMethodDataView.form_class == ShippingMethodForm

    def test_tab_name(self):
        """Should have correct tab name."""
        assert ShippingMethodDataView.tab_name == "data"

    def test_pk_url_kwarg(self):
        """Should use correct URL kwarg."""
        assert ShippingMethodDataView.pk_url_kwarg == "id"

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(ShippingMethodDataView, "get_success_url")
        assert callable(getattr(ShippingMethodDataView, "get_success_url"))

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(ShippingMethodDataView, "form_valid")
        assert callable(getattr(ShippingMethodDataView, "form_valid"))


class TestShippingMethodCriteriaView:
    """Test the ShippingMethodCriteriaView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShippingMethodCriteriaView, TemplateView)
        assert issubclass(ShippingMethodCriteriaView, PermissionRequiredMixin)
        assert issubclass(ShippingMethodCriteriaView, ShippingMethodTabMixin)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShippingMethodCriteriaView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should have correct tab name."""
        assert ShippingMethodCriteriaView.tab_name == "criteria"

    def test_template_name(self):
        """Should use correct template."""
        assert ShippingMethodCriteriaView.template_name == "manage/shipping_methods/shipping_method.html"

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(ShippingMethodCriteriaView, "get_success_url")
        assert callable(getattr(ShippingMethodCriteriaView, "get_success_url"))

    def test_post_method_exists(self):
        """Should have post method."""
        assert hasattr(ShippingMethodCriteriaView, "post")
        assert callable(getattr(ShippingMethodCriteriaView, "post"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ShippingMethodCriteriaView, "get_context_data")
        assert callable(getattr(ShippingMethodCriteriaView, "get_context_data"))


class TestShippingMethodPricesView:
    """Test the ShippingMethodPricesView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShippingMethodPricesView, TemplateView)
        assert issubclass(ShippingMethodPricesView, PermissionRequiredMixin)
        assert issubclass(ShippingMethodPricesView, ShippingMethodTabMixin)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShippingMethodPricesView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should have correct tab name."""
        assert ShippingMethodPricesView.tab_name == "prices"

    def test_template_name(self):
        """Should use correct template."""
        assert ShippingMethodPricesView.template_name == "manage/shipping_methods/shipping_method.html"

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(ShippingMethodPricesView, "get_success_url")
        assert callable(getattr(ShippingMethodPricesView, "get_success_url"))

    def test_post_method_exists(self):
        """Should have post method."""
        assert hasattr(ShippingMethodPricesView, "post")
        assert callable(getattr(ShippingMethodPricesView, "post"))

    def test_handle_add_price_method_exists(self):
        """Should have _handle_add_price method."""
        assert hasattr(ShippingMethodPricesView, "_handle_add_price")
        assert callable(getattr(ShippingMethodPricesView, "_handle_add_price"))

    def test_handle_update_prices_method_exists(self):
        """Should have _handle_update_prices method."""
        assert hasattr(ShippingMethodPricesView, "_handle_update_prices")
        assert callable(getattr(ShippingMethodPricesView, "_handle_update_prices"))

    def test_update_price_positions_method_exists(self):
        """Should have _update_price_positions method."""
        assert hasattr(ShippingMethodPricesView, "_update_price_positions")
        assert callable(getattr(ShippingMethodPricesView, "_update_price_positions"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ShippingMethodPricesView, "get_context_data")
        assert callable(getattr(ShippingMethodPricesView, "get_context_data"))


class TestShippingMethodCreateView:
    """Test the ShippingMethodCreateView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django CreateView."""
        from django.views.generic.edit import CreateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShippingMethodCreateView, CreateView)
        assert issubclass(ShippingMethodCreateView, PermissionRequiredMixin)

    def test_model_attribute(self):
        """Should use ShippingMethod model."""
        assert ShippingMethodCreateView.model == ShippingMethod

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShippingMethodCreateView.permission_required == "core.manage_shop"

    def test_form_class(self):
        """Should use ShippingMethodAddForm."""
        from lfs.manage.shipping_methods.forms import ShippingMethodAddForm

        assert ShippingMethodCreateView.form_class == ShippingMethodAddForm

    def test_template_name(self):
        """Should use correct template."""
        assert ShippingMethodCreateView.template_name == "manage/shipping_methods/add_shipping_method.html"

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(ShippingMethodCreateView, "form_valid")
        assert callable(getattr(ShippingMethodCreateView, "form_valid"))

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(ShippingMethodCreateView, "get_success_url")
        assert callable(getattr(ShippingMethodCreateView, "get_success_url"))


class TestShippingMethodDeleteConfirmView:
    """Test the ShippingMethodDeleteConfirmView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShippingMethodDeleteConfirmView, TemplateView)
        assert issubclass(ShippingMethodDeleteConfirmView, PermissionRequiredMixin)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShippingMethodDeleteConfirmView.permission_required == "core.manage_shop"

    def test_template_name(self):
        """Should use correct template."""
        assert ShippingMethodDeleteConfirmView.template_name == "manage/shipping_methods/delete_shipping_method.html"

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ShippingMethodDeleteConfirmView, "get_context_data")
        assert callable(getattr(ShippingMethodDeleteConfirmView, "get_context_data"))


class TestShippingMethodDeleteView:
    """Test the ShippingMethodDeleteView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django DeleteView."""
        from django.views.generic.edit import DeleteView
        from django.contrib.auth.mixins import PermissionRequiredMixin
        from django.contrib.messages.views import SuccessMessageMixin
        from lfs.manage.mixins import DirectDeleteMixin

        assert issubclass(ShippingMethodDeleteView, DeleteView)
        assert issubclass(ShippingMethodDeleteView, PermissionRequiredMixin)
        assert issubclass(ShippingMethodDeleteView, SuccessMessageMixin)
        assert issubclass(ShippingMethodDeleteView, DirectDeleteMixin)

    def test_model_attribute(self):
        """Should use ShippingMethod model."""
        assert ShippingMethodDeleteView.model == ShippingMethod

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShippingMethodDeleteView.permission_required == "core.manage_shop"

    def test_pk_url_kwarg(self):
        """Should use correct URL kwarg."""
        assert ShippingMethodDeleteView.pk_url_kwarg == "id"

    def test_success_message(self):
        """Should have success message."""
        assert ShippingMethodDeleteView.success_message == "Shipping method has been deleted."

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(ShippingMethodDeleteView, "get_success_url")
        assert callable(getattr(ShippingMethodDeleteView, "get_success_url"))

    def test_delete_method_exists(self):
        """Should have delete method."""
        assert hasattr(ShippingMethodDeleteView, "delete")
        assert callable(getattr(ShippingMethodDeleteView, "delete"))


class TestShippingMethodPriceCriteriaView:
    """Test the ShippingMethodPriceCriteriaView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShippingMethodPriceCriteriaView, TemplateView)
        assert issubclass(ShippingMethodPriceCriteriaView, PermissionRequiredMixin)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShippingMethodPriceCriteriaView.permission_required == "core.manage_shop"

    def test_template_name(self):
        """Should use correct template."""
        assert ShippingMethodPriceCriteriaView.template_name == "manage/shipping_methods/shipping_price_criteria.html"

    def test_get_shipping_price_method_exists(self):
        """Should have get_shipping_price method."""
        assert hasattr(ShippingMethodPriceCriteriaView, "get_shipping_price")
        assert callable(getattr(ShippingMethodPriceCriteriaView, "get_shipping_price"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ShippingMethodPriceCriteriaView, "get_context_data")
        assert callable(getattr(ShippingMethodPriceCriteriaView, "get_context_data"))

    def test_get_method_exists(self):
        """Should have get method."""
        assert hasattr(ShippingMethodPriceCriteriaView, "get")
        assert callable(getattr(ShippingMethodPriceCriteriaView, "get"))


class TestShippingMethodPriceCriteriaSaveView:
    """Test the ShippingMethodPriceCriteriaSaveView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView
        from django.contrib.auth.mixins import PermissionRequiredMixin

        assert issubclass(ShippingMethodPriceCriteriaSaveView, TemplateView)
        assert issubclass(ShippingMethodPriceCriteriaSaveView, PermissionRequiredMixin)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ShippingMethodPriceCriteriaSaveView.permission_required == "core.manage_shop"

    def test_post_method_exists(self):
        """Should have post method."""
        assert hasattr(ShippingMethodPriceCriteriaSaveView, "post")
        assert callable(getattr(ShippingMethodPriceCriteriaSaveView, "post"))

    def test_get_criteria_method_exists(self):
        """Should have _get_criteria method."""
        assert hasattr(ShippingMethodPriceCriteriaSaveView, "_get_criteria")
        assert callable(getattr(ShippingMethodPriceCriteriaSaveView, "_get_criteria"))


class TestShippingMethodPriceOperations:
    """Test shipping method price operations functionality."""

    def test_add_price_with_valid_data(self, shipping_method, mock_request):
        """Should add price with valid data."""
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.contrib.messages import get_messages

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
