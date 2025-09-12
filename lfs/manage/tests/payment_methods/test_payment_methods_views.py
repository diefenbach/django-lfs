"""
Comprehensive unit tests for payment method views.

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

import pytest
from decimal import Decimal
from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.http import Http404
from django.urls import reverse

from lfs.payment.models import PaymentMethod, PaymentMethodPrice
from lfs.customer.models import Customer
from lfs.manage.payment_methods.views import (
    ManagePaymentsView,
    NoPaymentMethodsView,
    PaymentMethodTabMixin,
    PaymentMethodDataView,
    PaymentMethodCriteriaView,
    PaymentMethodPricesView,
    PaymentMethodCreateView,
    PaymentMethodDeleteConfirmView,
    PaymentMethodDeleteView,
    PaymentMethodPriceCriteriaView,
    PaymentMethodPriceCriteriaSaveView,
)

User = get_user_model()


class TestManagePaymentsView:
    """Test ManagePaymentsView functionality."""

    def test_redirects_to_first_payment_method_when_methods_exist(self, rf, admin_user, payment_method):
        """Test that view redirects to first payment method when methods exist."""
        request = rf.get("/")
        request.user = admin_user

        view = ManagePaymentsView()
        view.request = request

        redirect_url = view.get_redirect_url()
        expected_url = reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id})

        assert redirect_url == expected_url

    def test_redirects_to_no_payment_methods_when_none_exist(self, rf, admin_user):
        """Test that view redirects to no payment methods page when none exist."""
        request = rf.get("/")
        request.user = admin_user

        view = ManagePaymentsView()
        view.request = request

        redirect_url = view.get_redirect_url()
        expected_url = reverse("lfs_manage_no_payment_methods")

        assert redirect_url == expected_url

    def test_orders_payment_methods_by_name(self, rf, admin_user):
        """Test that payment methods are ordered by name."""
        # Create payment methods in reverse alphabetical order
        PaymentMethod.objects.create(name="Zebra Payment", active=True, priority=10)
        PaymentMethod.objects.create(name="Alpha Payment", active=True, priority=20)

        request = rf.get("/")
        request.user = admin_user

        view = ManagePaymentsView()
        view.request = request

        redirect_url = view.get_redirect_url()

        # Should redirect to Alpha Payment (first alphabetically)
        alpha_method = PaymentMethod.objects.get(name="Alpha Payment")
        expected_url = reverse("lfs_manage_payment_method", kwargs={"id": alpha_method.id})

        assert redirect_url == expected_url

    def test_requires_manage_shop_permission(self):
        """Test that view requires manage_shop permission."""
        view = ManagePaymentsView()
        assert view.permission_required == "core.manage_shop"


class TestNoPaymentMethodsView:
    """Test NoPaymentMethodsView functionality."""

    def test_uses_correct_template(self):
        """Test that view uses correct template."""
        view = NoPaymentMethodsView()
        assert view.template_name == "manage/payment_methods/no_payment_methods.html"

    def test_requires_manage_shop_permission(self):
        """Test that view requires manage_shop permission."""
        view = NoPaymentMethodsView()
        assert view.permission_required == "core.manage_shop"


class TestPaymentMethodTabMixin:
    """Test PaymentMethodTabMixin functionality."""

    def test_get_payment_method_returns_correct_object(self, rf, payment_method):
        """Test that get_payment_method returns the correct PaymentMethod."""
        request = rf.get("/")

        mixin = PaymentMethodTabMixin()
        mixin.request = request
        mixin.kwargs = {"id": payment_method.id}

        result = mixin.get_payment_method()

        assert result == payment_method

    @pytest.mark.django_db
    def test_get_payment_method_raises_404_for_nonexistent_id(self, rf):
        """Test that get_payment_method raises 404 for nonexistent PaymentMethod."""
        request = rf.get("/")

        mixin = PaymentMethodTabMixin()
        mixin.request = request
        mixin.kwargs = {"id": 999}

        with pytest.raises(Http404):
            mixin.get_payment_method()

    def test_get_payment_methods_queryset_returns_all_by_default(self, rf, multiple_payment_methods):
        """Test that get_payment_methods_queryset returns all payment methods ordered by name."""
        request = rf.get("/")

        mixin = PaymentMethodTabMixin()
        mixin.request = request

        queryset = mixin.get_payment_methods_queryset()
        result_names = list(queryset.values_list("name", flat=True))

        expected_names = ["Payment Method 1", "Payment Method 2", "Payment Method 3"]
        assert result_names == expected_names

    def test_get_payment_methods_queryset_filters_by_search(self, rf, multiple_payment_methods):
        """Test that get_payment_methods_queryset filters by search query."""
        request = rf.get("/?q=Method 2")

        mixin = PaymentMethodTabMixin()
        mixin.request = request

        queryset = mixin.get_payment_methods_queryset()
        result_names = list(queryset.values_list("name", flat=True))

        assert result_names == ["Payment Method 2"]

    def test_get_payment_methods_queryset_handles_empty_search(self, rf, multiple_payment_methods):
        """Test that get_payment_methods_queryset handles empty search query."""
        request = rf.get("/?q=")

        mixin = PaymentMethodTabMixin()
        mixin.request = request

        queryset = mixin.get_payment_methods_queryset()
        result_count = queryset.count()

        assert result_count == 3

    def test_get_context_data_includes_payment_method(self, rf, payment_method):
        """Test that get_context_data includes payment method."""
        request = rf.get("/")

        mixin = PaymentMethodTabMixin()
        mixin.request = request
        mixin.kwargs = {"id": payment_method.id}
        mixin.object = None

        context = mixin.get_tab_context_data()

        assert context["payment_method"] == payment_method

    def test_get_context_data_includes_search_query(self, rf, payment_method):
        """Test that get_context_data includes search query."""
        request = rf.get("/?q=test")

        mixin = PaymentMethodTabMixin()
        mixin.request = request
        mixin.kwargs = {"id": payment_method.id}
        mixin.object = None

        context = mixin.get_tab_context_data()

        assert context["search_query"] == "test"

    def test_get_context_data_includes_active_tab(self, rf, payment_method):
        """Test that get_context_data includes active tab."""
        request = rf.get("/")

        mixin = PaymentMethodTabMixin()
        mixin.request = request
        mixin.kwargs = {"id": payment_method.id}
        mixin.tab_name = "data"
        mixin.object = None

        context = mixin.get_tab_context_data()

        assert context["active_tab"] == "data"

    def test_get_tabs_returns_correct_urls(self, rf, payment_method):
        """Test that _get_tabs returns correct tab URLs."""
        request = rf.get("/")

        mixin = PaymentMethodTabMixin()
        mixin.request = request

        tabs = mixin._get_tabs(payment_method)

        expected_tabs = [
            ("data", reverse("lfs_manage_payment_method", args=[payment_method.pk])),
            ("criteria", reverse("lfs_manage_payment_method_criteria", args=[payment_method.pk])),
            ("prices", reverse("lfs_manage_payment_method_prices", args=[payment_method.pk])),
        ]

        assert tabs == expected_tabs

    def test_get_tabs_includes_search_parameter(self, rf, payment_method):
        """Test that _get_tabs includes search parameter in URLs."""
        request = rf.get("/?q=test")

        mixin = PaymentMethodTabMixin()
        mixin.request = request

        tabs = mixin._get_tabs(payment_method)

        # All URLs should include the search parameter
        for tab_name, url in tabs:
            assert "q=test" in url


class TestPaymentMethodDataView:
    """Test PaymentMethodDataView functionality."""

    def test_uses_correct_model_and_form(self):
        """Test that view uses correct model and form class."""
        view = PaymentMethodDataView()

        assert view.model == PaymentMethod
        assert view.form_class.__name__ == "PaymentMethodForm"

    def test_uses_correct_tab_name(self):
        """Test that view uses correct tab name."""
        view = PaymentMethodDataView()
        assert view.tab_name == "data"

    def test_uses_correct_pk_url_kwarg(self):
        """Test that view uses correct pk_url_kwarg."""
        view = PaymentMethodDataView()
        assert view.pk_url_kwarg == "id"

    def test_requires_manage_shop_permission(self):
        """Test that view requires manage_shop permission."""
        view = PaymentMethodDataView()
        assert view.permission_required == "core.manage_shop"

    def test_get_success_url_returns_data_tab_url(self, rf, payment_method):
        """Test that get_success_url returns URL for data tab."""
        request = rf.post("/")

        view = PaymentMethodDataView()
        view.request = request
        view.object = payment_method

        success_url = view.get_success_url()
        expected_url = reverse("lfs_manage_payment_method", kwargs={"id": payment_method.pk})

        assert success_url == expected_url

    @patch("lfs.manage.payment_methods.views.messages")
    def test_form_valid_shows_success_message(self, mock_messages, rf, payment_method):
        """Test that form_valid shows success message."""
        request = rf.post("/")
        request.user = Mock()

        view = PaymentMethodDataView()
        view.request = request
        view.object = payment_method

        # Mock form
        form = Mock()
        form.save.return_value = payment_method

        # Mock parent form_valid
        with patch("django.views.generic.UpdateView.form_valid") as mock_parent:
            mock_parent.return_value = Mock()
            view.form_valid(form)

        mock_messages.success.assert_called_once()


class TestPaymentMethodCriteriaView:
    """Test PaymentMethodCriteriaView functionality."""

    def test_uses_correct_tab_name(self):
        """Test that view uses correct tab name."""
        view = PaymentMethodCriteriaView()
        assert view.tab_name == "criteria"

    def test_requires_manage_shop_permission(self):
        """Test that view requires manage_shop permission."""
        view = PaymentMethodCriteriaView()
        assert view.permission_required == "core.manage_shop"

    def test_get_success_url_returns_criteria_tab_url(self, rf):
        """Test that get_success_url returns URL for criteria tab."""
        request = rf.get("/")

        view = PaymentMethodCriteriaView()
        view.request = request
        view.kwargs = {"id": 1}

        success_url = view.get_success_url()
        expected_url = reverse("lfs_manage_payment_method_criteria", kwargs={"id": 1})

        assert success_url == expected_url

    @patch("lfs.manage.payment_methods.views.messages")
    def test_post_saves_criteria_and_shows_message(self, mock_messages, rf, payment_method):
        """Test that POST saves criteria and shows success message."""
        request = rf.post("/")
        request.user = Mock()

        view = PaymentMethodCriteriaView()
        view.request = request
        view.kwargs = {"id": payment_method.id}

        # Mock payment method save_criteria
        with patch.object(PaymentMethod, "save_criteria") as mock_save_criteria:
            response = view.post(request)

        mock_save_criteria.assert_called_once_with(request)
        mock_messages.success.assert_called_once()

    def test_post_returns_redirect_for_regular_request(self, rf, payment_method):
        """Test that POST returns redirect for regular request."""
        request = rf.post("/")
        request.headers = {}
        request.user = Mock()

        view = PaymentMethodCriteriaView()
        view.request = request
        view.kwargs = {"id": payment_method.id}

        with patch.object(PaymentMethod, "save_criteria"):
            with patch("lfs.manage.payment_methods.views.messages"):
                response = view.post(request)

        assert response.status_code == 302

    def test_post_returns_rendered_template_for_htmx_request(self, rf, payment_method):
        """Test that POST returns rendered template for HTMX request."""
        request = rf.post("/")
        request.headers = {"HX-Request": "true"}
        request.user = Mock()

        view = PaymentMethodCriteriaView()
        view.request = request
        view.kwargs = {"id": payment_method.id}

        with patch.object(PaymentMethod, "save_criteria"):
            with patch("lfs.manage.payment_methods.views.messages"):
                with patch("lfs.manage.payment_methods.views.render") as mock_render:
                    view.post(request)

        mock_render.assert_called_once()

    def test_get_context_data_includes_criteria(self, rf, payment_method):
        """Test that get_context_data includes criteria."""
        request = rf.get("/")

        view = PaymentMethodCriteriaView()
        view.request = request
        view.kwargs = {"id": payment_method.id}

        # Mock get_criteria method
        mock_criterion = Mock()
        mock_criterion.render.return_value = "<div>Test Criterion</div>"

        with patch.object(PaymentMethod, "get_criteria", return_value=[mock_criterion]):
            context = view.get_context_data()

        assert "criteria" in context
        assert len(context["criteria"]) == 1


class TestPaymentMethodPricesView:
    """Test PaymentMethodPricesView functionality."""

    def test_uses_correct_tab_name(self):
        """Test that view uses correct tab name."""
        view = PaymentMethodPricesView()
        assert view.tab_name == "prices"

    def test_requires_manage_shop_permission(self):
        """Test that view requires manage_shop permission."""
        view = PaymentMethodPricesView()
        assert view.permission_required == "core.manage_shop"

    def test_get_success_url_returns_prices_tab_url(self, rf):
        """Test that get_success_url returns URL for prices tab."""
        request = rf.get("/")

        view = PaymentMethodPricesView()
        view.request = request
        view.kwargs = {"id": 1}

        success_url = view.get_success_url()
        expected_url = reverse("lfs_manage_payment_method_prices", kwargs={"id": 1})

        assert success_url == expected_url

    def test_post_handles_add_price_action(self, rf, payment_method):
        """Test that POST handles add_price action."""
        request = rf.post("/", {"add_price": "true", "price": "15.00"})
        request.user = Mock()

        view = PaymentMethodPricesView()
        view.request = request
        view.kwargs = {"id": payment_method.id}

        with patch("lfs.manage.payment_methods.views.messages"):
            response = view.post(request)

        # Verify price was created
        assert payment_method.prices.filter(price=Decimal("15.00")).exists()
        assert response.status_code == 302

    def test_post_handles_update_prices_action(self, rf, payment_method_with_prices):
        """Test that POST handles update prices action."""
        price = payment_method_with_prices.prices.first()
        request = rf.post("/", {"action": "update", f"price-{price.id}": "25.00", f"priority-{price.id}": "15"})
        request.user = Mock()

        view = PaymentMethodPricesView()
        view.request = request
        view.kwargs = {"id": payment_method_with_prices.id}

        with patch("lfs.manage.payment_methods.views.messages"):
            response = view.post(request)

        # Verify price was updated
        price.refresh_from_db()
        assert price.price == Decimal("25.00")
        assert response.status_code == 302

    def test_post_handles_delete_prices_action(self, rf, payment_method_with_prices):
        """Test that POST handles delete prices action."""
        price = payment_method_with_prices.prices.first()
        price_id = price.id

        request = rf.post("/", {"action": "delete", f"delete-{price_id}": "true"})
        request.user = Mock()

        view = PaymentMethodPricesView()
        view.request = request
        view.kwargs = {"id": payment_method_with_prices.id}

        with patch("lfs.manage.payment_methods.views.messages"):
            response = view.post(request)

        # Verify price was deleted
        assert not PaymentMethodPrice.objects.filter(id=price_id).exists()
        assert response.status_code == 302

    def test_handle_add_price_with_invalid_price(self, rf, payment_method):
        """Test that _handle_add_price handles invalid price gracefully."""
        request = rf.post("/", {"add_price": "true", "price": "invalid"})
        request.user = Mock()

        view = PaymentMethodPricesView()
        view.request = request
        view.kwargs = {"id": payment_method.id}

        with patch("lfs.manage.payment_methods.views.messages"):
            response = view.post(request)

        # Verify price was created with 0.0
        assert payment_method.prices.filter(price=Decimal("0.0")).exists()

    def test_update_price_positions_sets_correct_priorities(self, rf, payment_method_with_prices):
        """Test that _update_price_positions sets correct priorities."""
        view = PaymentMethodPricesView()
        view._update_price_positions(payment_method_with_prices)

        prices = payment_method_with_prices.prices.all()
        priorities = [price.priority for price in prices]

        assert priorities == [10, 20]

    def test_get_context_data_includes_prices(self, rf, payment_method_with_prices):
        """Test that get_context_data includes prices."""
        request = rf.get("/")

        view = PaymentMethodPricesView()
        view.request = request
        view.kwargs = {"id": payment_method_with_prices.id}

        context = view.get_context_data()

        assert "prices" in context
        assert context["prices"].count() == 2


class TestPaymentMethodCreateView:
    """Test PaymentMethodCreateView functionality."""

    def test_uses_correct_model_and_form(self):
        """Test that view uses correct model and form class."""
        view = PaymentMethodCreateView()

        assert view.model == PaymentMethod
        assert view.form_class.__name__ == "PaymentMethodAddForm"

    def test_uses_correct_template(self):
        """Test that view uses correct template."""
        view = PaymentMethodCreateView()
        assert view.template_name == "manage/payment_methods/add_payment_method.html"

    def test_requires_manage_shop_permission(self):
        """Test that view requires manage_shop permission."""
        view = PaymentMethodCreateView()
        assert view.permission_required == "core.manage_shop"

    @patch("lfs.manage.payment_methods.views.messages")
    def test_form_valid_creates_payment_method_and_redirects(self, mock_messages, rf):
        """Test that form_valid creates payment method and redirects."""
        request = rf.post("/", {"name": "New Payment Method"})
        request.user = Mock()

        view = PaymentMethodCreateView()
        view.request = request

        # Mock form
        form = Mock()
        new_payment_method = PaymentMethod(id=1, name="New Payment Method")
        form.save.return_value = new_payment_method

        response = view.form_valid(form)

        mock_messages.success.assert_called_once()
        assert response.status_code == 302

    def test_get_success_url_returns_payment_method_url(self, rf):
        """Test that get_success_url returns URL for the created payment method."""
        request = rf.post("/")

        view = PaymentMethodCreateView()
        view.request = request
        view.object = Mock(id=1)

        success_url = view.get_success_url()
        expected_url = reverse("lfs_manage_payment_method", kwargs={"id": 1})

        assert success_url == expected_url


class TestPaymentMethodDeleteConfirmView:
    """Test PaymentMethodDeleteConfirmView functionality."""

    def test_uses_correct_template(self):
        """Test that view uses correct template."""
        view = PaymentMethodDeleteConfirmView()
        assert view.template_name == "manage/payment_methods/delete_payment_method.html"

    def test_requires_manage_shop_permission(self):
        """Test that view requires manage_shop permission."""
        view = PaymentMethodDeleteConfirmView()
        assert view.permission_required == "core.manage_shop"

    def test_get_context_data_includes_payment_method(self, rf, payment_method):
        """Test that get_context_data includes payment method."""
        request = rf.get("/")

        view = PaymentMethodDeleteConfirmView()
        view.request = request
        view.kwargs = {"id": payment_method.id}

        context = view.get_context_data()

        assert context["payment_method"] == payment_method


class TestPaymentMethodDeleteView:
    """Test PaymentMethodDeleteView functionality."""

    def test_uses_correct_model(self):
        """Test that view uses correct model."""
        view = PaymentMethodDeleteView()
        assert view.model == PaymentMethod

    def test_uses_correct_pk_url_kwarg(self):
        """Test that view uses correct pk_url_kwarg."""
        view = PaymentMethodDeleteView()
        assert view.pk_url_kwarg == "id"

    def test_requires_manage_shop_permission(self):
        """Test that view requires manage_shop permission."""
        view = PaymentMethodDeleteView()
        assert view.permission_required == "core.manage_shop"

    def test_get_success_url_returns_payment_methods_list(self, rf):
        """Test that get_success_url returns payment methods list URL."""
        request = rf.delete("/")

        view = PaymentMethodDeleteView()
        view.request = request

        success_url = view.get_success_url()
        expected_url = reverse("lfs_manage_payment_methods")

        assert success_url == expected_url

    @patch("lfs.payment.utils.get_default_payment_method")
    def test_delete_updates_customer_payment_methods(self, mock_get_default, rf, payment_method, admin_user):
        """Test that delete updates customers using the deleted payment method."""
        # Create customer using the payment method
        customer = Customer.objects.create(user=admin_user, selected_payment_method=payment_method)

        # Mock default payment method
        default_method = PaymentMethod.objects.create(name="Default", active=True, priority=1)
        mock_get_default.return_value = default_method

        request = rf.delete("/")
        request.user = admin_user

        view = PaymentMethodDeleteView()
        view.request = request
        view.kwargs = {"id": payment_method.id}

        view.delete(request)

        # Verify customer payment method was updated
        customer.refresh_from_db()
        assert customer.selected_payment_method == default_method


class TestPaymentMethodPriceCriteriaView:
    """Test PaymentMethodPriceCriteriaView functionality."""

    def test_uses_correct_template(self):
        """Test that view uses correct template."""
        view = PaymentMethodPriceCriteriaView()
        assert view.template_name == "manage/payment_methods/payment_price_criteria.html"

    def test_requires_manage_shop_permission(self):
        """Test that view requires manage_shop permission."""
        view = PaymentMethodPriceCriteriaView()
        assert view.permission_required == "core.manage_shop"

    def test_get_payment_price_returns_correct_object(self, rf, payment_method_price):
        """Test that get_payment_price returns correct PaymentMethodPrice."""
        request = rf.get("/")

        view = PaymentMethodPriceCriteriaView()
        view.request = request
        view.kwargs = {"price_id": payment_method_price.id}

        result = view.get_payment_price()

        assert result == payment_method_price

    @pytest.mark.django_db
    def test_get_payment_price_raises_404_for_nonexistent_id(self, rf):
        """Test that get_payment_price raises 404 for nonexistent price."""
        request = rf.get("/")

        view = PaymentMethodPriceCriteriaView()
        view.request = request
        view.kwargs = {"price_id": 999}

        with pytest.raises(Http404):
            view.get_payment_price()

    def test_get_context_data_includes_payment_price_and_criteria(self, rf, payment_method_price):
        """Test that get_context_data includes payment price and criteria."""
        request = rf.get("/")

        view = PaymentMethodPriceCriteriaView()
        view.request = request
        view.kwargs = {"price_id": payment_method_price.id}

        # Mock get_criteria method
        mock_criterion = Mock()
        mock_criterion.render.return_value = "<div>Test Criterion</div>"

        with patch.object(PaymentMethodPrice, "get_criteria", return_value=[mock_criterion]):
            context = view.get_context_data()

        assert context["payment_price"] == payment_method_price
        assert "criteria" in context
        assert len(context["criteria"]) == 1

    def test_get_returns_modal_template_for_htmx_request(self, rf, payment_method_price):
        """Test that GET returns modal template for HTMX request."""
        request = rf.get("/")
        request.headers = {"HX-Request": "true"}

        view = PaymentMethodPriceCriteriaView()
        view.request = request
        view.kwargs = {"price_id": payment_method_price.id}

        with patch("lfs.manage.payment_methods.views.render") as mock_render:
            with patch.object(PaymentMethodPrice, "get_criteria", return_value=[]):
                view.get(request)

        mock_render.assert_called_once()
        args = mock_render.call_args[0]
        assert "payment_price_criteria_modal.html" in args[1]

    def test_get_returns_regular_template_for_regular_request(self, rf, payment_method_price):
        """Test that GET returns regular template for regular request."""
        request = rf.get("/")
        request.headers = {}

        view = PaymentMethodPriceCriteriaView()
        view.request = request
        view.kwargs = {"price_id": payment_method_price.id}

        with patch.object(PaymentMethodPrice, "get_criteria", return_value=[]):
            with patch("django.views.generic.TemplateView.get") as mock_super_get:
                view.get(request)

        mock_super_get.assert_called_once()


class TestPaymentMethodPriceCriteriaSaveView:
    """Test PaymentMethodPriceCriteriaSaveView functionality."""

    def test_requires_manage_shop_permission(self):
        """Test that view requires manage_shop permission."""
        view = PaymentMethodPriceCriteriaSaveView()
        assert view.permission_required == "core.manage_shop"

    @patch("lfs.manage.payment_methods.views.messages")
    def test_post_saves_criteria_and_shows_message(self, mock_messages, rf, payment_method_price):
        """Test that POST saves criteria and shows success message."""
        request = rf.post("/")
        request.user = Mock()

        view = PaymentMethodPriceCriteriaSaveView()
        view.request = request
        view.kwargs = {"price_id": payment_method_price.id}

        # Mock payment price save_criteria
        with patch.object(PaymentMethodPrice, "save_criteria") as mock_save_criteria:
            response = view.post(request)

        mock_save_criteria.assert_called_once_with(request)
        mock_messages.success.assert_called_once()

    def test_post_returns_htmx_redirect_for_htmx_request(self, rf, payment_method_price):
        """Test that POST returns HTMX redirect for HTMX request."""
        request = rf.post("/")
        request.headers = {"HX-Request": "true"}
        request.user = Mock()

        view = PaymentMethodPriceCriteriaSaveView()
        view.request = request
        view.kwargs = {"price_id": payment_method_price.id}

        with patch.object(PaymentMethodPrice, "save_criteria"):
            with patch("lfs.manage.payment_methods.views.messages"):
                response = view.post(request)

        assert "HX-Redirect" in response
        expected_url = reverse(
            "lfs_manage_payment_method_prices", kwargs={"id": payment_method_price.payment_method.id}
        )
        assert expected_url in response["HX-Redirect"]

    def test_post_returns_regular_redirect_for_regular_request(self, rf, payment_method_price):
        """Test that POST returns regular redirect for regular request."""
        request = rf.post("/")
        request.headers = {}
        request.user = Mock()

        view = PaymentMethodPriceCriteriaSaveView()
        view.request = request
        view.kwargs = {"price_id": payment_method_price.id}

        with patch.object(PaymentMethodPrice, "save_criteria"):
            with patch("lfs.manage.payment_methods.views.messages"):
                response = view.post(request)

        assert response.status_code == 302

    def test_get_criteria_returns_rendered_criteria(self, rf, payment_method_price):
        """Test that _get_criteria returns rendered criteria HTML."""
        request = rf.post("/")

        view = PaymentMethodPriceCriteriaSaveView()
        view.request = request

        # Mock criterion objects
        mock_criterion = Mock()
        mock_criterion.render.return_value = "<div>Test Criterion</div>"

        with patch.object(PaymentMethodPrice, "get_criteria", return_value=[mock_criterion]):
            criteria = view._get_criteria(payment_method_price)

        assert len(criteria) == 1
        assert criteria[0] == "<div>Test Criterion</div>"
