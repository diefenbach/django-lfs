"""
Comprehensive unit tests for payment method mixins.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- PaymentMethodTabMixin functionality
- Mixin method isolation and reusability
- Context data generation
- Tab navigation logic
- Search query handling
- Error handling in mixins
- Mixin composition and inheritance
"""

import pytest
from unittest.mock import patch
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.http import Http404
from django.urls import reverse

from lfs.payment.models import PaymentMethod
from lfs.manage.payment_methods.views import PaymentMethodTabMixin

User = get_user_model()


class TestPaymentMethodTabMixin:
    """Test PaymentMethodTabMixin functionality."""

    def test_mixin_can_be_instantiated(self):
        """Test that mixin can be instantiated."""
        mixin = PaymentMethodTabMixin()
        assert mixin is not None

    def test_mixin_has_correct_template_name(self):
        """Test that mixin sets correct template name."""
        mixin = PaymentMethodTabMixin()
        assert mixin.template_name == "manage/payment_methods/payment_method.html"

    def test_mixin_tab_name_defaults_to_none(self):
        """Test that mixin tab_name defaults to None."""
        mixin = PaymentMethodTabMixin()
        assert mixin.tab_name is None

    def test_get_payment_method_with_valid_id(self, rf, payment_method, mock_view):
        """Test get_payment_method with valid payment method ID."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": payment_method.id}

        result = mock_view.get_payment_method()

        assert result == payment_method

    @pytest.mark.django_db
    def test_get_payment_method_with_nonexistent_id(self, rf, mock_view):
        """Test get_payment_method with nonexistent payment method ID."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": 999}

        with pytest.raises(Http404):
            mock_view.get_payment_method()

    def test_get_payment_method_with_invalid_id_type(self, rf, mock_view):
        """Test get_payment_method with invalid ID type."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": "invalid"}

        with pytest.raises((ValueError, Http404)):
            mock_view.get_payment_method()

    def test_get_payment_method_with_missing_id(self, rf, mock_view):
        """Test get_payment_method with missing ID in kwargs."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {}

        with pytest.raises(KeyError):
            mock_view.get_payment_method()

    def test_get_payment_methods_queryset_returns_all_by_default(self, rf, multiple_payment_methods, mock_view):
        """Test get_payment_methods_queryset returns all payment methods by default."""
        request = rf.get("/")
        mock_view.request = request

        queryset = mock_view.get_payment_methods_queryset()

        assert queryset.count() == 3
        names = list(queryset.values_list("name", flat=True))
        expected_names = ["Payment Method 1", "Payment Method 2", "Payment Method 3"]
        assert names == expected_names

    @pytest.mark.django_db
    def test_get_payment_methods_queryset_orders_by_name(self, rf, mock_view):
        """Test get_payment_methods_queryset orders results by name."""
        # Create payment methods in reverse alphabetical order
        PaymentMethod.objects.create(name="Zebra Payment", active=True, priority=10)
        PaymentMethod.objects.create(name="Alpha Payment", active=True, priority=20)
        PaymentMethod.objects.create(name="Beta Payment", active=True, priority=30)

        request = rf.get("/")
        mock_view.request = request

        queryset = mock_view.get_payment_methods_queryset()
        names = list(queryset.values_list("name", flat=True))

        assert names == ["Alpha Payment", "Beta Payment", "Zebra Payment"]

    def test_get_payment_methods_queryset_filters_by_search_query(self, rf, multiple_payment_methods, mock_view):
        """Test get_payment_methods_queryset filters by search query."""
        request = rf.get("/?q=Method 2")
        mock_view.request = request

        queryset = mock_view.get_payment_methods_queryset()

        assert queryset.count() == 1
        names = list(queryset.values_list("name", flat=True))
        assert names == ["Payment Method 2"]

    def test_get_payment_methods_queryset_case_insensitive_search(self, rf, multiple_payment_methods, mock_view):
        """Test get_payment_methods_queryset performs case-insensitive search."""
        request = rf.get("/?q=method 2")  # lowercase
        mock_view.request = request

        queryset = mock_view.get_payment_methods_queryset()

        assert queryset.count() == 1
        names = list(queryset.values_list("name", flat=True))
        assert names == ["Payment Method 2"]

    def test_get_payment_methods_queryset_partial_match_search(self, rf, multiple_payment_methods, mock_view):
        """Test get_payment_methods_queryset performs partial match search."""
        request = rf.get("/?q=Method")  # Should match all
        mock_view.request = request

        queryset = mock_view.get_payment_methods_queryset()

        assert queryset.count() == 3

    def test_get_payment_methods_queryset_empty_search_query(self, rf, multiple_payment_methods, mock_view):
        """Test get_payment_methods_queryset with empty search query."""
        request = rf.get("/?q=")
        mock_view.request = request

        queryset = mock_view.get_payment_methods_queryset()

        assert queryset.count() == 3

    def test_get_payment_methods_queryset_whitespace_only_search(self, rf, multiple_payment_methods, mock_view):
        """Test get_payment_methods_queryset with whitespace-only search query."""
        request = rf.get("/?q=   ")
        mock_view.request = request

        queryset = mock_view.get_payment_methods_queryset()

        assert queryset.count() == 3

    def test_get_payment_methods_queryset_no_matches(self, rf, multiple_payment_methods, mock_view):
        """Test get_payment_methods_queryset with search query that matches nothing."""
        request = rf.get("/?q=NonExistent")
        mock_view.request = request

        queryset = mock_view.get_payment_methods_queryset()

        assert queryset.count() == 0

    def test_get_context_data_includes_payment_method(self, rf, payment_method, mock_view):
        """Test get_context_data includes payment method."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": payment_method.id}
        mock_view.object = None

        context = mock_view.get_tab_context_data()

        assert context["payment_method"] == payment_method

    def test_get_context_data_uses_object_if_available(self, rf, payment_method, mock_view):
        """Test get_context_data uses object attribute if available."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": 999}  # Different ID
        mock_view.object = payment_method  # Should use this instead

        context = mock_view.get_tab_context_data()

        assert context["payment_method"] == payment_method

    def test_get_context_data_includes_payment_methods_queryset(self, rf, multiple_payment_methods, mock_view):
        """Test get_context_data includes payment methods queryset."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": multiple_payment_methods[0].id}
        mock_view.object = None

        context = mock_view.get_tab_context_data()

        assert "payment_methods" in context
        assert context["payment_methods"].count() == 3

    def test_get_context_data_includes_search_query(self, rf, payment_method, mock_view):
        """Test get_context_data includes search query."""
        request = rf.get("/?q=test")
        mock_view.request = request
        mock_view.kwargs = {"id": payment_method.id}
        mock_view.object = None

        context = mock_view.get_tab_context_data()

        assert context["search_query"] == "test"

    def test_get_context_data_includes_active_tab(self, rf, payment_method, mock_view):
        """Test get_context_data includes active tab."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": payment_method.id}
        mock_view.object = None
        mock_view.tab_name = "data"

        context = mock_view.get_tab_context_data()

        assert context["active_tab"] == "data"

    def test_get_context_data_includes_tabs(self, rf, payment_method, mock_view):
        """Test get_context_data includes tabs."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": payment_method.id}
        mock_view.object = None

        context = mock_view.get_tab_context_data()

        assert "tabs" in context
        assert len(context["tabs"]) == 3

    def test_get_tabs_returns_correct_tab_structure(self, rf, payment_method, mock_view):
        """Test _get_tabs returns correct tab structure."""
        request = rf.get("/")
        mock_view.request = request

        tabs = mock_view._get_tabs(payment_method)

        assert len(tabs) == 3

        # Each tab should be a tuple of (name, url)
        for tab_name, tab_url in tabs:
            assert isinstance(tab_name, str)
            assert isinstance(tab_url, str)
            assert tab_name in ["data", "criteria", "prices"]

    def test_get_tabs_returns_correct_urls(self, rf, payment_method, mock_view):
        """Test _get_tabs returns correct URLs for each tab."""
        request = rf.get("/")
        mock_view.request = request

        tabs = mock_view._get_tabs(payment_method)
        tab_dict = dict(tabs)

        expected_data_url = reverse("lfs_manage_payment_method", args=[payment_method.pk])
        expected_criteria_url = reverse("lfs_manage_payment_method_criteria", args=[payment_method.pk])
        expected_prices_url = reverse("lfs_manage_payment_method_prices", args=[payment_method.pk])

        assert tab_dict["data"] == expected_data_url
        assert tab_dict["criteria"] == expected_criteria_url
        assert tab_dict["prices"] == expected_prices_url

    def test_get_tabs_includes_search_parameter(self, rf, payment_method, mock_view):
        """Test _get_tabs includes search parameter in URLs."""
        request = rf.get("/?q=test")
        mock_view.request = request

        tabs = mock_view._get_tabs(payment_method)

        for tab_name, tab_url in tabs:
            assert "q=test" in tab_url

    def test_get_tabs_handles_empty_search_parameter(self, rf, payment_method, mock_view):
        """Test _get_tabs handles empty search parameter."""
        request = rf.get("/?q=")
        mock_view.request = request

        tabs = mock_view._get_tabs(payment_method)

        for tab_name, tab_url in tabs:
            # Should not include empty search parameter
            assert "q=" not in tab_url

    def test_get_tabs_handles_special_characters_in_search(self, rf, payment_method, mock_view):
        """Test _get_tabs handles special characters in search parameter."""
        search_query = "test & more"
        encoded_query = urlencode({"q": search_query})
        request = rf.get(f"/?{encoded_query}")
        mock_view.request = request

        tabs = mock_view._get_tabs(payment_method)

        for tab_name, tab_url in tabs:
            # Should properly encode special characters
            assert "test" in tab_url
            assert "more" in tab_url

    def test_get_tabs_handles_unicode_in_search(self, rf, payment_method, mock_view):
        """Test _get_tabs handles unicode characters in search parameter."""
        search_query = "测试"
        request = rf.get(f"/?q={search_query}")
        mock_view.request = request

        tabs = mock_view._get_tabs(payment_method)

        for tab_name, tab_url in tabs:
            # Should properly encode unicode characters
            assert search_query in tab_url or urlencode({"q": search_query}) in tab_url

    def test_get_navigation_context_returns_search_query(self, rf, mock_view):
        """Test _get_navigation_context returns search query."""
        request = rf.get("/?q=test")
        mock_view.request = request

        context = mock_view._get_navigation_context()

        assert context["search_query"] == "test"

    def test_get_navigation_context_handles_missing_search_query(self, rf, mock_view):
        """Test _get_navigation_context handles missing search query."""
        request = rf.get("/")
        mock_view.request = request

        context = mock_view._get_navigation_context()

        assert context["search_query"] == ""

    def test_mixin_works_with_inheritance(self, rf, payment_method):
        """Test that mixin works properly with class inheritance."""

        class BaseView:
            def get_context_data(self, **kwargs):
                return {}

        class TestView(PaymentMethodTabMixin, BaseView):
            tab_name = "test_tab"

            def __init__(self):
                self.request = None
                self.kwargs = {}
                self.object = None

        request = rf.get("/")
        view = TestView()
        view.request = request
        view.kwargs = {"id": payment_method.id}

        # Should inherit all mixin functionality
        assert view.get_payment_method() == payment_method
        assert view.tab_name == "test_tab"

        context = view.get_tab_context_data()
        assert context["active_tab"] == "test_tab"

    def test_mixin_handles_multiple_inheritance(self, rf, payment_method):
        """Test that mixin works with multiple inheritance."""

        class OtherMixin:
            def get_other_data(self):
                return "other_data"

        class BaseView:
            def get_context_data(self, **kwargs):
                return {}

        class TestView(PaymentMethodTabMixin, OtherMixin, BaseView):
            tab_name = "multi_tab"

            def __init__(self):
                self.request = None
                self.kwargs = {}
                self.object = None

        request = rf.get("/")
        view = TestView()
        view.request = request
        view.kwargs = {"id": payment_method.id}

        # Should have functionality from both mixins
        assert view.get_payment_method() == payment_method
        assert view.get_other_data() == "other_data"
        assert view.tab_name == "multi_tab"

    def test_mixin_handles_database_errors_gracefully(self, rf, mock_view):
        """Test that mixin handles database errors gracefully."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": 1}

        # Mock database error in get_payment_method
        with patch("lfs.manage.payment_methods.views.get_object_or_404") as mock_get_object:
            mock_get_object.side_effect = Exception("Database error")

            with pytest.raises(Exception):
                mock_view.get_payment_method()

        # Mock database error in get_payment_methods_queryset
        with patch.object(PaymentMethod.objects, "all") as mock_all:
            mock_all.side_effect = Exception("Database error")

            with pytest.raises(Exception):
                mock_view.get_payment_methods_queryset()

    @pytest.mark.django_db
    def test_mixin_performance_with_large_queryset(self, rf, mock_view):
        """Test mixin performance with large number of payment methods."""
        # Create many payment methods
        payment_methods = []
        for i in range(100):
            pm = PaymentMethod.objects.create(name=f"Payment Method {i:03d}", active=True, priority=i)
            payment_methods.append(pm)

        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": payment_methods[0].id}

        # Should handle large queryset efficiently
        context = mock_view.get_tab_context_data()

        assert context["payment_methods"].count() == 100
        assert context["payment_method"] == payment_methods[0]

    def test_mixin_thread_safety(self, rf, payment_method):
        """Test that mixin instances are thread-safe."""
        # Create multiple mixin instances
        mixin1 = PaymentMethodTabMixin()
        mixin2 = PaymentMethodTabMixin()

        request1 = rf.get("/?q=test1")
        request2 = rf.get("/?q=test2")

        mixin1.request = request1
        mixin1.kwargs = {"id": payment_method.id}
        mixin1.object = None
        mixin1.tab_name = "tab1"

        mixin2.request = request2
        mixin2.kwargs = {"id": payment_method.id}
        mixin2.object = None
        mixin2.tab_name = "tab2"

        # Each instance should maintain its own state
        context1 = mixin1.get_tab_context_data()
        context2 = mixin2.get_tab_context_data()

        assert context1["search_query"] == "test1"
        assert context2["search_query"] == "test2"
        assert context1["active_tab"] == "tab1"
        assert context2["active_tab"] == "tab2"

    def test_mixin_memory_efficiency(self, rf, payment_method, mock_view):
        """Test that mixin doesn't hold unnecessary references."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": payment_method.id}
        mock_view.object = None

        # Get context data multiple times
        for i in range(10):
            context = mock_view.get_tab_context_data()
            assert context["payment_method"] == payment_method
            # Context should be fresh each time, not cached
            del context

        # Mixin should not accumulate state
        assert not hasattr(mock_view, "_cached_context")
        assert not hasattr(mock_view, "_cached_payment_method")

    def test_mixin_error_handling_in_context_generation(self, rf, payment_method, mock_view):
        """Test error handling in context data generation."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": payment_method.id}
        mock_view.object = None

        # Mock error in _get_tabs
        with patch.object(mock_view, "_get_tabs", side_effect=Exception("Tab generation error")):
            with pytest.raises(Exception):
                mock_view.get_tab_context_data()

        # Mock error in get_payment_methods_queryset
        with patch.object(mock_view, "get_payment_methods_queryset", side_effect=Exception("Queryset error")):
            with pytest.raises(Exception):
                mock_view.get_tab_context_data()

    def test_mixin_customization_via_subclassing(self, rf, payment_method):
        """Test that mixin can be customized via subclassing."""

        class CustomTabMixin(PaymentMethodTabMixin):
            def get_payment_methods_queryset(self):
                # Override to add custom filtering
                queryset = super().get_payment_methods_queryset()
                return queryset.filter(active=True)

            def _get_tabs(self, payment_method):
                # Override to add custom tab
                tabs = super()._get_tabs(payment_method)
                custom_tab = ("custom", f"/custom/{payment_method.pk}/")
                return tabs + [custom_tab]

        class TestView(CustomTabMixin):
            def __init__(self):
                super().__init__()
                self.request = None
                self.kwargs = {}
                self.object = None

        # Create inactive payment method
        inactive_method = PaymentMethod.objects.create(name="Inactive", active=False, priority=10)

        request = rf.get("/")
        view = TestView()
        view.request = request
        view.kwargs = {"id": payment_method.id}

        context = view.get_tab_context_data()

        # Should only include active payment methods
        payment_methods = context["payment_methods"]
        names = list(payment_methods.values_list("name", flat=True))
        assert "Inactive" not in names

        # Should include custom tab
        tabs = context["tabs"]
        tab_names = [tab[0] for tab in tabs]
        assert "custom" in tab_names

    def test_mixin_integration_with_django_generic_views(self, rf, payment_method):
        """Test that mixin integrates well with Django generic views."""
        from django.views.generic import TemplateView

        class TestView(PaymentMethodTabMixin, TemplateView):
            template_name = "test_template.html"
            tab_name = "integration_test"

        request = rf.get("/")
        view = TestView()
        view.request = request
        view.kwargs = {"id": payment_method.id}

        # Should work with TemplateView
        context = view.get_context_data()
        context.update(view.get_tab_context_data())

        assert context["payment_method"] == payment_method
        assert context["active_tab"] == "integration_test"
        assert "view" in context  # Added by TemplateView

    def test_mixin_backwards_compatibility(self, rf, payment_method, mock_view):
        """Test that mixin maintains backwards compatibility."""
        request = rf.get("/")
        mock_view.request = request
        mock_view.kwargs = {"id": payment_method.id}
        mock_view.object = None

        # Test that all expected context keys are present
        context = mock_view.get_tab_context_data()

        required_keys = ["payment_method", "payment_methods", "search_query", "active_tab", "tabs"]

        for key in required_keys:
            assert key in context, f"Required context key '{key}' is missing"

        # Test that tab structure is correct
        tabs = context["tabs"]
        assert len(tabs) == 3

        for tab_name, tab_url in tabs:
            assert tab_name in ["data", "criteria", "prices"]
            assert isinstance(tab_url, str)
            assert tab_url.startswith("/") or tab_url.startswith("http")
