"""
Comprehensive unit tests for customer mixins.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Parametrization for variations

Tests cover:
- CustomerFilterMixin (filtering logic, session handling)
- CustomerPaginationMixin (pagination logic)
- CustomerDataMixin (data calculation)
- CustomerContextMixin (context data)
- Edge cases and error conditions
"""

import pytest
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.customer.models import Customer
from lfs.addresses.models import Address
from lfs.manage.customers.mixins import (
    CustomerFilterMixin,
    CustomerPaginationMixin,
    CustomerDataMixin,
    CustomerContextMixin,
)
from lfs.manage.customers.forms import CustomerFilterForm

User = get_user_model()


@pytest.fixture
def mock_request():
    """Mock request object for testing."""
    factory = RequestFactory()
    request = factory.get("/")
    request.session = {}
    return request


@pytest.fixture
def mock_request_with_session():
    """Mock request object with session data for testing."""
    factory = RequestFactory()
    request = factory.get("/")
    request.session = {
        "customer-filters": {"name": "John", "start": "2024-01-01", "end": "2024-12-31"},
        "customer-ordering": "lastname",
        "customer-ordering-order": "-",
    }
    return request


@pytest.fixture
def user_with_customer(db):
    """User with associated customer and address."""
    user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
    customer = Customer.objects.create(user=user)
    address = Address.objects.create(
        customer=customer,
        firstname="John",
        lastname="Doe",
        line1="123 Main St",
        city="Test City",
        zip_code="12345",
        email="john.doe@example.com",
    )
    return user, customer, address


@pytest.fixture
def multiple_customers(db):
    """Multiple customers for pagination testing."""
    customers = []

    for i in range(25):  # Enough to test pagination
        user = User.objects.create_user(username=f"user{i+1}", email=f"user{i+1}@example.com", password="testpass123")
        customer = Customer.objects.create(user=user)
        Address.objects.create(
            customer=customer,
            firstname=f"User{i+1}",
            lastname="Test",
            line1=f"{i+1}00 Main St",
            city="Test City",
            zip_code=f"{10000+i}",
            email=f"user{i+1}@example.com",
        )
        customers.append(customer)

    return customers


class TestCustomerFilterMixin:
    """Test CustomerFilterMixin functionality."""

    def test_should_return_empty_dict_when_no_session_filters(self, mock_request):
        """Test that empty dict is returned when no session filters exist."""
        mixin = CustomerFilterMixin()
        mixin.request = mock_request

        result = mixin.get_customer_filters()

        assert result == {}

    def test_should_return_session_filters_when_exist(self, mock_request_with_session):
        """Test that session filters are returned when they exist."""
        mixin = CustomerFilterMixin()
        mixin.request = mock_request_with_session

        result = mixin.get_customer_filters()

        assert result == {"name": "John", "start": "2024-01-01", "end": "2024-12-31"}

    def test_should_return_all_customers_when_no_filters(self, mock_request, multiple_customers):
        """Test that all customers are returned when no filters are applied."""
        mixin = CustomerFilterMixin()
        mixin.request = mock_request

        result = mixin.get_filtered_customers_queryset()

        assert result.count() == 25

    def test_should_apply_filters_when_session_has_filters(self, mock_request_with_session, multiple_customers):
        """Test that filters are applied when session has filters."""
        mixin = CustomerFilterMixin()
        mixin.request = mock_request_with_session

        with patch("lfs.manage.customers.mixins.CustomerFilterService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.filter_customers.return_value = Customer.objects.filter(id__in=[1, 2, 3])
            mock_service.get_ordering.return_value = "-addresses__lastname"

            result = mixin.get_filtered_customers_queryset()

            mock_service.filter_customers.assert_called_once()
            mock_service.get_ordering.assert_called_once_with("lastname", "-")

    def test_should_return_correct_initial_data_when_no_filters(self, mock_request):
        """Test that correct initial data is returned when no filters exist."""
        mixin = CustomerFilterMixin()
        mixin.request = mock_request

        result = mixin.get_filter_form_initial()

        assert result == {"name": "", "start": "", "end": ""}

    def test_should_return_correct_initial_data_when_filters_exist(self, mock_request_with_session):
        """Test that correct initial data is returned when filters exist."""
        mixin = CustomerFilterMixin()
        mixin.request = mock_request_with_session

        result = mixin.get_filter_form_initial()

        assert result == {"name": "John", "start": "2024-01-01", "end": "2024-12-31"}

    def test_should_handle_missing_filter_keys(self, mock_request):
        """Test that missing filter keys are handled gracefully."""
        mock_request.session = {"customer-filters": {"name": "John"}}
        mixin = CustomerFilterMixin()
        mixin.request = mock_request

        result = mixin.get_filter_form_initial()

        assert result == {"name": "John", "start": "", "end": ""}

    def test_should_handle_none_session_filters(self, mock_request):
        """Test that None session filters are handled gracefully."""
        mock_request.session = {"customer-filters": None}
        mixin = CustomerFilterMixin()
        mixin.request = mock_request

        result = mixin.get_customer_filters()

        assert result == {}


class TestCustomerPaginationMixin:
    """Test CustomerPaginationMixin functionality."""

    def test_should_return_paginated_customers_with_default_page_size(self, mock_request, multiple_customers):
        """Test that paginated customers are returned with default page size."""

        # Create a mixin that combines both filter and pagination mixins
        class TestMixin(CustomerFilterMixin, CustomerPaginationMixin):
            pass

        mixin = TestMixin()
        mixin.request = mock_request

        # Mock the filter method
        with patch.object(mixin, "get_filtered_customers_queryset") as mock_get_queryset:
            mock_get_queryset.return_value = Customer.objects.all()

            result = mixin.get_paginated_customers()

            assert result.number == 1
            assert len(result) == 25  # All customers on first page
            assert result.paginator.per_page == 30  # Default page size

    def test_should_return_paginated_customers_with_custom_page_size(self, mock_request, multiple_customers):
        """Test that paginated customers are returned with custom page size."""

        # Create a mixin that combines both filter and pagination mixins
        class TestMixin(CustomerFilterMixin, CustomerPaginationMixin):
            pass

        mixin = TestMixin()
        mixin.request = mock_request

        # Mock the filter method
        with patch.object(mixin, "get_filtered_customers_queryset") as mock_get_queryset:
            mock_get_queryset.return_value = Customer.objects.all()

            result = mixin.get_paginated_customers(page_size=10)

            assert result.number == 1
            assert len(result) == 10  # First 10 customers
            assert result.paginator.per_page == 10  # Custom page size

    def test_should_handle_page_parameter(self, mock_request, multiple_customers):
        """Test that page parameter is handled correctly."""
        mock_request.GET = {"page": "2"}

        # Create a mixin that combines both filter and pagination mixins
        class TestMixin(CustomerFilterMixin, CustomerPaginationMixin):
            pass

        mixin = TestMixin()
        mixin.request = mock_request

        # Mock the filter method
        with patch.object(mixin, "get_filtered_customers_queryset") as mock_get_queryset:
            mock_get_queryset.return_value = Customer.objects.all()

            result = mixin.get_paginated_customers(page_size=10)

            assert result.number == 2

    def test_should_handle_invalid_page_parameter(self, mock_request, multiple_customers):
        """Test that invalid page parameter is handled gracefully."""
        mock_request.GET = {"page": "invalid"}

        # Create a mixin that combines both filter and pagination mixins
        class TestMixin(CustomerFilterMixin, CustomerPaginationMixin):
            pass

        mixin = TestMixin()
        mixin.request = mock_request

        # Mock the filter method
        with patch.object(mixin, "get_filtered_customers_queryset") as mock_get_queryset:
            mock_get_queryset.return_value = Customer.objects.all()

            result = mixin.get_paginated_customers(page_size=10)

            assert result.number == 1  # Should default to first page

    def test_should_handle_page_out_of_range(self, mock_request, multiple_customers):
        """Test that page out of range is handled gracefully."""
        mock_request.GET = {"page": "999"}

        # Create a mixin that combines both filter and pagination mixins
        class TestMixin(CustomerFilterMixin, CustomerPaginationMixin):
            pass

        mixin = TestMixin()
        mixin.request = mock_request

        # Mock the filter method
        with patch.object(mixin, "get_filtered_customers_queryset") as mock_get_queryset:
            mock_get_queryset.return_value = Customer.objects.all()

            result = mixin.get_paginated_customers(page_size=10)

            assert result.number == 3  # Should return last page (25 customers / 10 per page = 3 pages)

    def test_should_handle_empty_queryset(self, mock_request):
        """Test that empty queryset is handled gracefully."""

        # Create a mixin that combines both filter and pagination mixins
        class TestMixin(CustomerFilterMixin, CustomerPaginationMixin):
            pass

        mixin = TestMixin()
        mixin.request = mock_request

        # Mock the filter method to return empty queryset
        with patch.object(mixin, "get_filtered_customers_queryset") as mock_get_queryset:
            mock_get_queryset.return_value = Customer.objects.none()

            result = mixin.get_paginated_customers()

            assert result.number == 1
            assert len(result) == 0
            assert result.paginator.num_pages == 1  # Django Paginator always returns at least 1 page


class TestCustomerDataMixin:
    """Test CustomerDataMixin functionality."""

    def test_should_return_customers_with_data(self, mock_request, multiple_customers):
        """Test that customers with data are returned."""
        mixin = CustomerDataMixin()
        mixin.request = mock_request

        with patch("lfs.manage.customers.mixins.CustomerDataService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            expected_data = [{"customer": c, "orders_count": 0, "cart_price": None} for c in multiple_customers[:5]]
            mock_service.get_customers_with_data.return_value = expected_data

            result = mixin.get_customers_with_data(multiple_customers[:5])

            mock_service.get_customers_with_data.assert_called_once_with(multiple_customers[:5], mock_request)
            assert result == expected_data

    def test_should_return_customer_with_data(self, mock_request, user_with_customer):
        """Test that single customer with data is returned."""
        user, customer, address = user_with_customer
        mixin = CustomerDataMixin()
        mixin.request = mock_request

        with patch("lfs.manage.customers.mixins.CustomerDataService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            expected_data = {"customer": customer, "orders": [], "cart": None}
            mock_service.get_customer_with_data.return_value = expected_data

            result = mixin.get_customer_with_data(customer)

            mock_service.get_customer_with_data.assert_called_once_with(customer, mock_request)
            assert result == expected_data

    def test_should_pass_request_to_service(self, mock_request, multiple_customers):
        """Test that request is passed to service correctly."""
        mixin = CustomerDataMixin()
        mixin.request = mock_request

        with patch("lfs.manage.customers.mixins.CustomerDataService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.get_customers_with_data.return_value = []

            mixin.get_customers_with_data(multiple_customers[:5])

            mock_service.get_customers_with_data.assert_called_once_with(multiple_customers[:5], mock_request)


class TestCustomerContextMixin:
    """Test CustomerContextMixin functionality."""

    def test_should_return_correct_context_data_when_no_filters(self, mock_request):
        """Test that correct context data is returned when no filters exist."""
        mixin = CustomerContextMixin()
        mixin.request = mock_request

        # Mock the parent class methods
        # Create a mixin that combines filter and context mixins
        class TestMixin(CustomerFilterMixin, CustomerContextMixin):
            pass

        mixin = TestMixin()
        mixin.request = mock_request

        with patch.object(mixin, "get_customer_filters") as mock_get_filters, patch.object(
            mixin, "get_filter_form_initial"
        ) as mock_get_initial:

            mock_get_filters.return_value = {}
            mock_get_initial.return_value = {"name": "", "start": "", "end": ""}

            result = mixin.get_customer_context_data()

            assert result["customer_filters"] == {}
            assert isinstance(result["filter_form"], CustomerFilterForm)
            assert result["ordering"] == "id"

    def test_should_return_correct_context_data_when_filters_exist(self, mock_request_with_session):
        """Test that correct context data is returned when filters exist."""
        mixin = CustomerContextMixin()
        mixin.request = mock_request_with_session

        # Mock the parent class methods
        # Create a mixin that combines filter and context mixins
        class TestMixin(CustomerFilterMixin, CustomerContextMixin):
            pass

        mixin = TestMixin()
        mixin.request = mock_request_with_session

        with patch.object(mixin, "get_customer_filters") as mock_get_filters, patch.object(
            mixin, "get_filter_form_initial"
        ) as mock_get_initial:

            mock_get_filters.return_value = {"name": "John"}
            mock_get_initial.return_value = {"name": "John", "start": "", "end": ""}

            result = mixin.get_customer_context_data()

            assert result["customer_filters"] == {"name": "John"}
            assert isinstance(result["filter_form"], CustomerFilterForm)
            assert result["ordering"] == "lastname"

    def test_should_handle_missing_ordering_in_session(self, mock_request):
        """Test that missing ordering in session is handled gracefully."""
        mock_request.session = {}
        mixin = CustomerContextMixin()
        mixin.request = mock_request

        # Mock the parent class methods
        # Create a mixin that combines filter and context mixins
        class TestMixin(CustomerFilterMixin, CustomerContextMixin):
            pass

        mixin = TestMixin()
        mixin.request = mock_request

        with patch.object(mixin, "get_customer_filters") as mock_get_filters, patch.object(
            mixin, "get_filter_form_initial"
        ) as mock_get_initial:

            mock_get_filters.return_value = {}
            mock_get_initial.return_value = {"name": "", "start": "", "end": ""}

            result = mixin.get_customer_context_data()

            assert result["ordering"] == "id"  # Default value

    def test_should_handle_none_ordering_in_session(self, mock_request):
        """Test that None ordering in session is handled gracefully."""
        mock_request.session = {"customer-ordering": None}
        mixin = CustomerContextMixin()
        mixin.request = mock_request

        # Mock the parent class methods
        # Create a mixin that combines filter and context mixins
        class TestMixin(CustomerFilterMixin, CustomerContextMixin):
            pass

        mixin = TestMixin()
        mixin.request = mock_request

        with patch.object(mixin, "get_customer_filters") as mock_get_filters, patch.object(
            mixin, "get_filter_form_initial"
        ) as mock_get_initial:

            mock_get_filters.return_value = {}
            mock_get_initial.return_value = {"name": "", "start": "", "end": ""}

            result = mixin.get_customer_context_data()

            assert result["ordering"] == "id"  # Default value

    def test_should_initialize_filter_form_with_correct_initial_data(self, mock_request):
        """Test that filter form is initialized with correct initial data."""
        mixin = CustomerContextMixin()
        mixin.request = mock_request

        # Mock the parent class methods
        # Create a mixin that combines filter and context mixins
        class TestMixin(CustomerFilterMixin, CustomerContextMixin):
            pass

        mixin = TestMixin()
        mixin.request = mock_request

        with patch.object(mixin, "get_customer_filters") as mock_get_filters, patch.object(
            mixin, "get_filter_form_initial"
        ) as mock_get_initial:

            mock_get_filters.return_value = {}
            initial_data = {"name": "John", "start": "2024-01-01", "end": "2024-12-31"}
            mock_get_initial.return_value = initial_data

            result = mixin.get_customer_context_data()

            form = result["filter_form"]
            assert form.initial["name"] == "John"
            assert form.initial["start"] == "2024-01-01"
            assert form.initial["end"] == "2024-12-31"

    def test_should_handle_additional_kwargs(self, mock_request):
        """Test that additional kwargs are handled correctly."""
        mixin = CustomerContextMixin()
        mixin.request = mock_request

        # Mock the parent class methods
        # Create a mixin that combines filter and context mixins
        class TestMixin(CustomerFilterMixin, CustomerContextMixin):
            pass

        mixin = TestMixin()
        mixin.request = mock_request

        with patch.object(mixin, "get_customer_filters") as mock_get_filters, patch.object(
            mixin, "get_filter_form_initial"
        ) as mock_get_initial:

            mock_get_filters.return_value = {}
            mock_get_initial.return_value = {"name": "", "start": "", "end": ""}

            result = mixin.get_customer_context_data(extra_data="test")

            # Should not include extra kwargs in result
            assert "extra_data" not in result
            assert "customer_filters" in result
            assert "filter_form" in result
            assert "ordering" in result


class TestMixinIntegration:
    """Test integration between different mixins."""

    def test_should_work_together_when_combined(self, mock_request_with_session, multiple_customers):
        """Test that mixins work together when combined."""

        class TestView(CustomerFilterMixin, CustomerPaginationMixin, CustomerContextMixin):
            def __init__(self, request):
                self.request = request

        view = TestView(mock_request_with_session)

        # Test that filters are applied
        filters = view.get_customer_filters()
        assert filters["name"] == "John"

        # Test that context data is generated
        context = view.get_customer_context_data()
        assert "customer_filters" in context
        assert "filter_form" in context
        assert "ordering" in context

        # Test that pagination works
        with patch.object(view, "get_filtered_customers_queryset") as mock_get_queryset:
            mock_get_queryset.return_value = Customer.objects.all()
            paginated = view.get_paginated_customers(page_size=10)
            assert paginated.number == 1
            assert paginated.paginator.per_page == 10

    def test_should_handle_missing_session_keys_gracefully(self, mock_request, multiple_customers):
        """Test that missing session keys are handled gracefully when mixins are combined."""

        class TestView(CustomerFilterMixin, CustomerPaginationMixin, CustomerContextMixin):
            def __init__(self, request):
                self.request = request

        view = TestView(mock_request)

        # Should not raise exceptions
        filters = view.get_customer_filters()
        assert filters == {}

        context = view.get_customer_context_data()
        assert context["ordering"] == "id"

        with patch.object(view, "get_filtered_customers_queryset") as mock_get_queryset:
            mock_get_queryset.return_value = Customer.objects.all()
            paginated = view.get_paginated_customers()
            assert paginated.number == 1
