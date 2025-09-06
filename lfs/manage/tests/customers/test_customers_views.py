"""
Comprehensive unit and integration tests for LFS customer management views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Parametrization for variations

Tests cover:
- CustomerListView (list view with filtering and pagination)
- NoCustomersView (empty state view)
- CustomerTabMixin (tab navigation functionality)
- CustomerDataView (data tab view)
- ApplyCustomerFiltersView (filter form handling)
- ResetCustomerFiltersView (filter reset)
- SetCustomerOrderingView (ordering management)
- Integration tests for complete workflows
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.customer.models import Customer
from lfs.catalog.models import Product
from lfs.manage.customers.views import (
    CustomerTabMixin,
)


User = get_user_model()


@pytest.fixture
def product(db, shop):
    """Sample Product for testing."""
    return Product.objects.create(
        name="Test Product",
        slug="test-product",
        sku="TEST-001",
        price=Decimal("29.99"),
        active=True,
        shop=shop,
    )


@pytest.fixture
def user(db):
    """Sample User for testing."""
    return User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")


@pytest.fixture
def customer(db, user):
    """Sample Customer for testing."""
    return Customer.objects.create(
        user=user,
        session="test_session_123",
    )


@pytest.fixture
def anonymous_customer(db):
    """Sample anonymous Customer for testing."""
    return Customer.objects.create(
        user=None,
        session="test-session-123",
    )


class TestCustomerListView:
    """Test CustomerListView functionality."""

    def test_should_require_permission(self, client):
        """Test that view requires proper permission."""
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 302  # Redirect to login

    def test_should_display_customers_when_authenticated(self, client, admin_user, customer, shop):
        """Test that authenticated users can see customers."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert "customers_with_data" in response.context

    def test_should_include_filter_form_in_context(self, client, admin_user, customer, shop):
        """Test that filter form is included in context."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert "filter_form" in response.context

    def test_should_include_pagination_in_context(self, client, admin_user, customer, shop):
        """Test that pagination is included in context."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert "customers_page" in response.context


class TestCustomerDataView:
    """Test CustomerDataView functionality."""

    def test_should_require_permission(self, client, customer, shop):
        """Test that view requires proper permission."""
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer.id}))
        assert response.status_code == 302  # Redirect to login

    def test_should_display_customer_when_authenticated(self, client, admin_user, customer, shop):
        """Test that authenticated users can see customer details."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer.id}))
        assert response.status_code == 200
        assert "customer" in response.context

    def test_should_include_customer_data_in_context(self, client, admin_user, customer, shop):
        """Test that customer data is included in context."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer.id}))
        assert response.status_code == 200
        assert response.context["customer"].id == customer.id

    def test_should_include_sidebar_navigation(self, client, admin_user, customer, shop):
        """Test that sidebar navigation is included."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer.id}))
        assert response.status_code == 200
        assert "customers_page" in response.context


class TestApplyCustomerFiltersView:
    """Test ApplyCustomerFiltersView functionality."""

    def test_should_require_permission(self, client, shop):
        """Test that view requires proper permission."""
        response = client.post(reverse("lfs_apply_customer_filters"))
        assert response.status_code == 302  # Redirect to login

    def test_should_apply_name_filter_when_valid(self, client, admin_user, customer, shop):
        """Test that name filter is applied when valid data is submitted."""
        client.force_login(admin_user)
        data = {"name": "test"}
        response = client.post(reverse("lfs_apply_customer_filters"), data)
        assert response.status_code == 302  # Redirect after success
        assert "customer-filters" in client.session
        assert client.session["customer-filters"]["name"] == "test"

    def test_should_remove_name_filter_when_empty(self, client, admin_user, customer, shop):
        """Test that name filter is removed when empty data is submitted."""
        client.force_login(admin_user)
        # First set a filter
        client.session["customer-filters"] = {"name": "test"}
        client.session.save()

        data = {"name": ""}
        response = client.post(reverse("lfs_apply_customer_filters"), data)
        assert response.status_code == 302
        assert "name" not in client.session["customer-filters"]

    def test_should_redirect_to_customer_when_customer_id_provided(self, client, admin_user, customer, shop):
        """Test that redirects to specific customer when customer_id is provided."""
        client.force_login(admin_user)
        data = {"customer_id": customer.id}
        response = client.post(reverse("lfs_apply_customer_filters"), data)
        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_customer", kwargs={"customer_id": customer.id})

    def test_should_redirect_to_customer_list_when_no_customer_id(self, client, admin_user, shop):
        """Test that redirects to customer list when no customer_id is provided."""
        client.force_login(admin_user)
        data = {}
        response = client.post(reverse("lfs_apply_customer_filters"), data)
        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_customers")


class TestResetCustomerFiltersView:
    """Test ResetCustomerFiltersView functionality."""

    def test_should_require_permission(self, client, shop):
        """Test that view requires proper permission."""
        response = client.get(reverse("lfs_reset_customer_filters"))
        assert response.status_code == 302  # Redirect to login

    def test_should_clear_filters_when_authenticated(self, client, admin_user, shop):
        """Test that filters are cleared when authenticated."""
        client.force_login(admin_user)
        # Set some filters first
        client.session["customer-filters"] = {"name": "test"}
        client.session.save()

        response = client.get(reverse("lfs_reset_customer_filters"))
        assert response.status_code == 302
        assert "customer-filters" not in client.session

    def test_should_redirect_to_customer_when_customer_id_provided(self, client, admin_user, customer, shop):
        """Test that redirects to specific customer when customer_id is provided."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_reset_customer_filters") + f"?customer_id={customer.id}")
        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_customer", kwargs={"customer_id": customer.id})

    def test_should_redirect_to_customer_list_when_no_customer_id(self, client, admin_user, shop):
        """Test that redirects to customer list when no customer_id is provided."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_reset_customer_filters"))
        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_customers")


class TestSetCustomerOrderingView:
    """Test SetCustomerOrderingView functionality."""

    def test_should_require_permission(self, client, shop):
        """Test that view requires proper permission."""
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "id"}))
        assert response.status_code == 302  # Redirect to login

    def test_should_set_ordering_when_authenticated(self, client, admin_user, shop):
        """Test that ordering is set when authenticated."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "lastname"}))
        assert response.status_code == 302
        assert client.session["customer-ordering"] == "lastname"

    def test_should_toggle_ordering_direction_when_same_field(self, client, admin_user, shop):
        """Test that ordering direction is toggled when same field is selected."""
        client.force_login(admin_user)

        # First request
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "id"}))
        assert response.status_code == 302
        assert client.session["customer-ordering"] == "id"
        assert client.session["customer-ordering-order"] == ""

        # Second request - should toggle direction
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "id"}))
        assert response.status_code == 302
        assert client.session["customer-ordering"] == "id"
        assert client.session["customer-ordering-order"] == "-"

    def test_should_redirect_to_customer_when_customer_id_provided(self, client, admin_user, customer, shop):
        """Test that redirects to specific customer when customer_id is provided."""
        client.force_login(admin_user)
        response = client.get(
            reverse("lfs_set_customer_ordering", kwargs={"ordering": "id"}) + f"?customer_id={customer.id}"
        )
        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_customer", kwargs={"customer_id": customer.id})

    def test_should_redirect_to_customer_list_when_no_customer_id(self, client, admin_user, shop):
        """Test that redirects to customer list when no customer_id is provided."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "id"}))
        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_customers")


class TestNoCustomersView:
    """Test NoCustomersView functionality."""

    def test_should_require_permission(self, client, shop):
        """Test that view requires proper permission."""
        response = client.get(reverse("lfs_manage_no_customers"))
        assert response.status_code == 302  # Redirect to login

    def test_should_display_no_customers_message_when_authenticated(self, client, admin_user, shop):
        """Test that no customers message is displayed when authenticated."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_no_customers"))
        assert response.status_code == 200
        assert "No customers found" in response.content.decode()


class TestCustomerTabMixin:
    """Test CustomerTabMixin functionality."""

    def test_should_get_customer_by_id(self, customer):
        """Test that customer is retrieved by ID."""
        mixin = CustomerTabMixin()
        mixin.kwargs = {"customer_id": customer.id}

        # Mock the get_object_or_404 behavior
        from unittest.mock import patch

        with patch("lfs.manage.customers.views.get_object_or_404", return_value=customer) as mock_get:
            result = mixin.get_customer()
            assert result == customer
            mock_get.assert_called_once()

    def test_should_have_correct_template_name(self):
        """Test that mixin has correct template name."""
        mixin = CustomerTabMixin()
        assert mixin.template_name == "manage/customers/customer.html"

    def test_should_have_correct_model(self):
        """Test that mixin has correct model."""
        mixin = CustomerTabMixin()
        assert mixin.model == Customer
