"""
Comprehensive unit tests for order mixins.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- OrderFilterMixin filtering and form handling
- OrderPaginationMixin pagination logic
- OrderDataMixin data calculation methods
- OrderContextMixin context data provision
- Edge cases and error conditions
"""

import pytest
from datetime import date
from unittest.mock import MagicMock

from django.test import RequestFactory

from lfs.order.models import Order
from lfs.manage.orders.mixins import OrderFilterMixin, OrderPaginationMixin, OrderDataMixin, OrderContextMixin
from lfs.manage.orders.forms import OrderFilterForm


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def mock_request(request_factory):
    """Mock request object for testing."""
    request = request_factory.get("/")
    request.session = {}
    return request


@pytest.fixture
def mock_request_with_filters(request_factory):
    """Mock request with session filters."""
    request = request_factory.get("/")
    request.session = {"order-filters": {"name": "John Doe", "state": "1", "start": "2023-01-01", "end": "2023-12-31"}}
    return request


class TestOrderFilterMixin:
    """Test OrderFilterMixin functionality."""

    def test_get_order_filters_empty_session(self, mock_request):
        """Should return empty dict when no session filters exist."""
        mixin = OrderFilterMixin()
        mixin.request = mock_request

        filters = mixin.get_order_filters()

        assert filters == {}

    def test_get_order_filters_with_session_data(self, mock_request_with_filters):
        """Should return session filters when they exist."""
        mixin = OrderFilterMixin()
        mixin.request = mock_request_with_filters

        filters = mixin.get_order_filters()

        expected_filters = {"name": "John Doe", "state": "1", "start": "2023-01-01", "end": "2023-12-31"}
        assert filters == expected_filters

    def test_get_filtered_orders_queryset_no_filters(self, mock_request):
        """Should return all orders when no filters applied."""
        mixin = OrderFilterMixin()
        mixin.request = mock_request

        queryset = mixin.get_filtered_orders_queryset()

        assert queryset.model == Order
        assert "created" in str(queryset.query.order_by)

    def test_get_filtered_orders_queryset_with_filters(self, mock_request_with_filters, multiple_orders):
        """Should apply filters to queryset."""
        mixin = OrderFilterMixin()
        mixin.request = mock_request_with_filters

        queryset = mixin.get_filtered_orders_queryset()

        # Should have applied filters - exact count depends on test data
        assert queryset.exists()

    def test_get_filter_form_initial_no_filters(self, mock_request):
        """Should return empty initial data when no filters."""
        mixin = OrderFilterMixin()
        mixin.request = mock_request

        initial = mixin.get_filter_form_initial()

        expected = {
            "name": "",
            "state": "",
            "start": None,
            "end": None,
        }
        assert initial == expected

    def test_get_filter_form_initial_with_filters(self, mock_request_with_filters):
        """Should parse date strings and return proper initial data."""
        mixin = OrderFilterMixin()
        mixin.request = mock_request_with_filters

        initial = mixin.get_filter_form_initial()

        assert initial["name"] == "John Doe"
        assert initial["state"] == "1"
        assert initial["start"] == date(2023, 1, 1)
        assert initial["end"] == date(2023, 12, 31)


class TestOrderPaginationMixin:
    """Test OrderPaginationMixin functionality."""

    def test_get_paginated_orders_default_page_size(self, mock_request, multiple_orders):
        """Should paginate with default page size of 20."""
        mixin = OrderPaginationMixin()
        mixin.request = mock_request

        page = mixin.get_paginated_orders()

        assert hasattr(page, "object_list")
        assert hasattr(page, "number")
        assert page.paginator.per_page == 20

    def test_get_paginated_orders_custom_page_size(self, mock_request, multiple_orders):
        """Should paginate with custom page size."""
        mixin = OrderPaginationMixin()
        mixin.request = mock_request

        page = mixin.get_paginated_orders(page_size=5)

        assert page.paginator.per_page == 5

    def test_get_paginated_orders_with_page_parameter(self, request_factory, multiple_orders):
        """Should respect page parameter from request."""
        request = request_factory.get("/?page=2")
        request.session = {}

        mixin = OrderPaginationMixin()
        mixin.request = request

        page = mixin.get_paginated_orders(page_size=2)

        assert page.number == 2

    def test_get_paginated_orders_empty_queryset(self, mock_request):
        """Should handle empty queryset gracefully."""
        # Ensure no orders exist
        Order.objects.all().delete()

        mixin = OrderPaginationMixin()
        mixin.request = mock_request

        page = mixin.get_paginated_orders()

        assert page.paginator.count == 0
        assert len(page.object_list) == 0


class TestOrderDataMixin:
    """Test OrderDataMixin functionality."""

    def test_get_order_summary(self, order, order_item):
        """Should delegate to OrderDataService."""
        mixin = OrderDataMixin()

        summary = mixin.get_order_summary(order)

        assert "total" in summary
        assert "item_count" in summary
        assert "products" in summary

    def test_get_orders_with_data(self, multiple_orders):
        """Should delegate to OrderDataService for multiple orders."""
        mixin = OrderDataMixin()

        orders_with_data = mixin.get_orders_with_data(multiple_orders)

        assert len(orders_with_data) == len(multiple_orders)
        for order_data in orders_with_data:
            assert "order" in order_data
            assert "total" in order_data

    def test_get_order_with_data(self, order):
        """Should delegate to OrderDataService for single order."""
        mixin = OrderDataMixin()

        order_with_data = mixin.get_order_with_data(order)

        assert order_with_data is not None
        assert "order" in order_with_data
        assert "total" in order_with_data

    def test_get_order_with_data_none_input(self):
        """Should handle None input gracefully."""
        mixin = OrderDataMixin()

        result = mixin.get_order_with_data(None)
        assert result is None


class TestOrderContextMixin:
    """Test OrderContextMixin functionality."""

    def test_get_order_context_data_no_filters(self, mock_request):
        """Should return context data with empty filters."""
        mixin = OrderContextMixin()
        mixin.request = mock_request

        context = mixin.get_order_context_data()

        assert "order_filters" in context
        assert "filter_form" in context
        assert context["order_filters"] == {}
        assert isinstance(context["filter_form"], OrderFilterForm)

    def test_get_order_context_data_with_filters(self, mock_request_with_filters):
        """Should return context data with populated filters."""
        mixin = OrderContextMixin()
        mixin.request = mock_request_with_filters

        context = mixin.get_order_context_data()

        assert "order_filters" in context
        assert "filter_form" in context
        assert context["order_filters"]["name"] == "John Doe"
        assert isinstance(context["filter_form"], OrderFilterForm)

    def test_get_order_context_data_form_initial_values(self, mock_request_with_filters):
        """Should initialize form with parsed filter values."""
        mixin = OrderContextMixin()
        mixin.request = mock_request_with_filters

        context = mixin.get_order_context_data()
        form = context["filter_form"]

        assert form.initial["name"] == "John Doe"
        assert form.initial["state"] == "1"
        assert form.initial["start"] == date(2023, 1, 1)
        assert form.initial["end"] == date(2023, 12, 31)


class TestOrderMixinIntegration:
    """Test mixin integration and edge cases."""

    def test_mixin_inheritance_pattern(self):
        """Test that mixins can be combined properly."""
        # This is more of a structural test to ensure mixins don't conflict

        class CombinedMixin(OrderFilterMixin, OrderPaginationMixin, OrderDataMixin, OrderContextMixin):
            pass

        # Should be able to create instance without conflicts
        mixin = CombinedMixin()

        # Should have methods from all parent mixins
        assert hasattr(mixin, "get_order_filters")
        assert hasattr(mixin, "get_paginated_orders")
        assert hasattr(mixin, "get_order_summary")
        assert hasattr(mixin, "get_order_context_data")

    def test_mixin_error_handling_session_none(self):
        """Test mixin handles None session gracefully."""
        mixin = OrderFilterMixin()
        mixin.request = MagicMock()
        mixin.request.session = None

        # Should not crash
        filters = mixin.get_order_filters()
        assert filters == {}

    def test_mixin_error_handling_missing_session_key(self):
        """Test mixin handles missing session key gracefully."""
        mixin = OrderFilterMixin()
        mixin.request = MagicMock()
        mixin.request.session = {"other_key": "value"}

        filters = mixin.get_order_filters()
        assert filters == {}

    def test_pagination_mixin_with_invalid_page(self, request_factory):
        """Test pagination mixin handles invalid page numbers."""
        request = request_factory.get("/?page=invalid")
        request.session = {}

        mixin = OrderPaginationMixin()
        mixin.request = request

        page = mixin.get_paginated_orders(page_size=5)

        # Should default to page 1
        assert page.number == 1

    def test_filter_mixin_with_malformed_dates(self):
        """Test filter mixin handles malformed date strings."""
        mixin = OrderFilterMixin()
        mixin.request = MagicMock()
        mixin.request.session = {"order-filters": {"start": "invalid-date", "end": "also-invalid"}}

        initial = mixin.get_filter_form_initial()

        # Should handle invalid dates gracefully
        assert initial["start"] is None
        assert initial["end"] is None
