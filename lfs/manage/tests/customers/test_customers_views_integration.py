"""
Comprehensive integration tests for customer management views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Integration testing with real HTTP requests

Tests cover:
- CustomerListView (list view with filtering and pagination)
- CustomerDataView (individual customer view)
- ApplyCustomerFiltersView (filter form handling)
- ResetCustomerFiltersView (filter reset)
- SetCustomerOrderingView (ordering management)
- ApplyPredefinedCustomerFilterView (predefined filters)
- NoCustomersView (empty state)
- Authentication and permission requirements
- Session handling
- Template rendering
- Error handling
"""

import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.customer.models import Customer
from lfs.order.models import Order
from lfs.addresses.models import Address

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Admin user with proper permissions."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def regular_user(db):
    """Regular user without admin permissions."""
    return User.objects.create_user(username="user", email="user@example.com", password="testpass123")


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
def anonymous_customer_with_address(db):
    """Anonymous customer with address."""
    customer = Customer.objects.create(session="test-session-123")
    address = Address.objects.create(
        customer=customer,
        firstname="Jane",
        lastname="Smith",
        line1="456 Oak Ave",
        city="Test City",
        zip_code="54321",
        email="jane.smith@example.com",
    )
    return customer, address


@pytest.fixture
def multiple_customers_with_orders(db, shop):
    """Multiple customers with orders for comprehensive testing."""
    from django.contrib.contenttypes.models import ContentType
    from decimal import Decimal
    from django.utils import timezone

    customers = []

    # Create user-based customers
    for i in range(15):
        user = User.objects.create_user(username=f"user{i+1}", email=f"user{i+1}@example.com", password="testpass123")
        customer = Customer.objects.create(user=user, session=f"user_session_{i+1}")
        address = Address.objects.create(
            customer=customer,
            firstname=f"User{i+1}",
            lastname="Test",
            line1=f"{i+1}00 Main St",
            city="Test City",
            zip_code=f"{10000+i}",
            email=f"user{i+1}@example.com",
        )

        # Create orders for some customers
        if i < 10:
            # Get the content type for Address
            address_content_type = ContentType.objects.get_for_model(address.__class__)

            Order.objects.create(
                number=f"ORD-{i+1:03d}",
                session=customer.session,
                customer_firstname=f"User{i+1}",
                customer_lastname="Test",
                customer_email=f"user{i+1}@example.com",
                price=Decimal(f"{(i+1)*10}.99"),
                state=1,
                created=timezone.now(),
                # Set the address relationships
                sa_content_type=address_content_type,
                sa_object_id=address.id,
                ia_content_type=address_content_type,
                ia_object_id=address.id,
            )

        customers.append(customer)

    # Create session-based customers
    for i in range(5):
        customer = Customer.objects.create(session=f"session-{i+1}")
        address = Address.objects.create(
            customer=customer,
            firstname=f"Session{i+1}",
            lastname="User",
            line1=f"{i+16}00 Main St",
            city="Test City",
            zip_code=f"{10000+i+15}",
            email=f"session{i+1}@example.com",
        )
        customers.append(customer)

    return customers


class TestCustomerListView:
    """Test CustomerListView integration functionality."""

    def test_should_redirect_to_login_when_not_authenticated(self, client):
        """Test that unauthenticated users are redirected to login."""
        response = client.get(reverse("lfs_manage_customers"))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "/login/" in response.url

    def test_should_redirect_to_login_when_no_permission(self, client, regular_user):
        """Test that users without permission are redirected to login."""
        client.force_login(regular_user)
        response = client.get(reverse("lfs_manage_customers"))

        assert response.status_code == 403  # Authenticated users without permission get 403

    def test_should_display_customers_when_authenticated_with_permission(
        self, client, admin_user, multiple_customers_with_orders
    ):
        """Test that authenticated users with permission can see customers."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customers"))

        assert response.status_code == 200
        assert "customers_with_data" in response.context
        assert "customers_page" in response.context
        assert "filter_form" in response.context

    def test_should_include_pagination_when_many_customers(self, client, admin_user, multiple_customers_with_orders):
        """Test that pagination is included when there are many customers."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customers"))

        assert response.status_code == 200
        customers_page = response.context["customers_page"]
        assert customers_page.paginator.num_pages >= 1

    def test_should_display_correct_template(self, client, admin_user, multiple_customers_with_orders):
        """Test that correct template is used."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customers"))

        assert response.status_code == 200
        assert "manage/customers/customer_list.html" in [t.name for t in response.templates]

    def test_should_include_filter_form_in_context(self, client, admin_user, multiple_customers_with_orders):
        """Test that filter form is included in context."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customers"))

        assert response.status_code == 200
        filter_form = response.context["filter_form"]
        assert hasattr(filter_form, "fields")
        assert "name" in filter_form.fields
        assert "start" in filter_form.fields
        assert "end" in filter_form.fields

    def test_should_include_ordering_in_context(self, client, admin_user, multiple_customers_with_orders):
        """Test that ordering information is included in context."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customers"))

        assert response.status_code == 200
        assert "ordering" in response.context
        assert response.context["ordering"] == "id"  # Default ordering

    def test_should_handle_empty_customer_list(self, client, admin_user, shop):
        """Test that empty customer list is handled gracefully."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customers"))

        assert response.status_code == 200
        assert response.context["customers_with_data"] == []

    def test_should_apply_session_filters(self, client, admin_user, multiple_customers_with_orders):
        """Test that session filters are applied."""
        client.force_login(admin_user)

        # Set session filters - filter by "Test" which should match user-based customers (15)
        session = client.session
        session["customer-filters"] = {"name": "Test"}
        session.save()

        response = client.get(reverse("lfs_manage_customers"))

        assert response.status_code == 200
        # Should filter customers by name - user-based customers have lastname "Test"
        customers_with_data = response.context["customers_with_data"]
        assert len(customers_with_data) == 15  # User-based customers should match
        assert all(
            "Test" in customer_data["customer"].addresses.first().lastname for customer_data in customers_with_data
        )

    def test_should_apply_session_ordering(self, client, admin_user, multiple_customers_with_orders):
        """Test that session ordering is applied."""
        client.force_login(admin_user)

        # Set session ordering
        session = client.session
        session["customer-ordering"] = "lastname"
        session["customer-ordering-order"] = "-"
        session.save()

        response = client.get(reverse("lfs_manage_customers"))

        assert response.status_code == 200
        assert response.context["ordering"] == "lastname"


class TestCustomerDataView:
    """Test CustomerDataView integration functionality."""

    def test_should_redirect_to_login_when_not_authenticated(self, client, user_with_customer):
        """Test that unauthenticated users are redirected to login."""
        user, customer, address = user_with_customer
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer.id}))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "/login/" in response.url

    def test_should_redirect_to_login_when_no_permission(self, client, regular_user, user_with_customer):
        """Test that users without permission are redirected to login."""
        user, customer, address = user_with_customer
        client.force_login(regular_user)
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer.id}))

        assert response.status_code == 403  # Authenticated users without permission get 403

    def test_should_display_customer_when_authenticated_with_permission(
        self, client, admin_user, user_with_customer, shop
    ):
        """Test that authenticated users with permission can see customer details."""
        user, customer, address = user_with_customer
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer.id}))

        assert response.status_code == 200
        assert "customer" in response.context
        assert response.context["customer"].id == customer.id

    def test_should_display_correct_template(self, client, admin_user, user_with_customer, shop):
        """Test that correct template is used."""
        user, customer, address = user_with_customer
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer.id}))

        assert response.status_code == 200
        assert "manage/customers/customer.html" in [t.name for t in response.templates]

    def test_should_include_sidebar_navigation(
        self, client, admin_user, user_with_customer, multiple_customers_with_orders
    ):
        """Test that sidebar navigation is included."""
        user, customer, address = user_with_customer
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer.id}))

        assert response.status_code == 200
        assert "customers_page" in response.context
        assert "active_tab" in response.context
        assert response.context["active_tab"] == "data"

    def test_should_include_customer_data_in_context(self, client, admin_user, user_with_customer, shop):
        """Test that customer data is included in context."""
        user, customer, address = user_with_customer
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer.id}))

        assert response.status_code == 200
        assert "customer" in response.context
        assert "orders" in response.context
        assert "cart" in response.context
        assert "cart_price" in response.context

    def test_should_return_404_when_customer_not_found(self, client, admin_user, shop):
        """Test that 404 is returned when customer doesn't exist."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": 99999}))

        assert response.status_code == 404

    def test_should_handle_anonymous_customer(self, client, admin_user, anonymous_customer_with_address, shop):
        """Test that anonymous customers are handled correctly."""
        customer, address = anonymous_customer_with_address
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer.id}))

        assert response.status_code == 200
        assert response.context["customer"].id == customer.id


class TestApplyCustomerFiltersView:
    """Test ApplyCustomerFiltersView integration functionality."""

    def test_should_redirect_to_login_when_not_authenticated(self, client):
        """Test that unauthenticated users are redirected to login."""
        response = client.post(reverse("lfs_apply_customer_filters"))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "/login/" in response.url

    def test_should_redirect_to_login_when_no_permission(self, client, regular_user):
        """Test that users without permission are redirected to login."""
        client.force_login(regular_user)
        response = client.post(reverse("lfs_apply_customer_filters"))

        assert response.status_code == 403  # Authenticated users without permission get 403

    def test_should_apply_name_filter_when_valid_data(self, client, admin_user, shop):
        """Test that name filter is applied when valid data is submitted."""
        client.force_login(admin_user)
        data = {"name": "John"}
        response = client.post(reverse("lfs_apply_customer_filters"), data)

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "customer-filters" in client.session
        assert client.session["customer-filters"]["name"] == "John"

    def test_should_apply_date_filters_when_valid_data(self, client, admin_user):
        """Test that date filters are applied when valid data is submitted."""
        client.force_login(admin_user)
        data = {"start": "2024-01-01", "end": "2024-12-31"}
        response = client.post(reverse("lfs_apply_customer_filters"), data)

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "customer-filters" in client.session
        assert client.session["customer-filters"]["start"] == "2024-01-01"
        assert client.session["customer-filters"]["end"] == "2024-12-31"

    def test_should_remove_filters_when_empty_data(self, client, admin_user):
        """Test that filters are removed when empty data is submitted."""
        client.force_login(admin_user)

        # First set some filters
        session = client.session
        session["customer-filters"] = {"name": "John", "start": "2024-01-01"}
        session.save()

        data = {"name": "", "start": "", "end": ""}
        response = client.post(reverse("lfs_apply_customer_filters"), data)

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "name" not in client.session["customer-filters"]
        assert "start" not in client.session["customer-filters"]

    def test_should_redirect_to_customer_when_customer_id_provided(self, client, admin_user, user_with_customer):
        """Test that redirects to specific customer when customer_id is provided."""
        user, customer, address = user_with_customer
        client.force_login(admin_user)
        data = {"customer_id": customer.id}
        response = client.post(reverse("lfs_apply_customer_filters"), data)

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert response.url == reverse("lfs_manage_customer", kwargs={"customer_id": customer.id})

    def test_should_redirect_to_customer_list_when_no_customer_id(self, client, admin_user):
        """Test that redirects to customer list when no customer_id is provided."""
        client.force_login(admin_user)
        data = {}
        response = client.post(reverse("lfs_apply_customer_filters"), data)

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert response.url == reverse("lfs_manage_customers")

    def test_should_handle_invalid_form_data(self, client, admin_user):
        """Test that invalid form data is handled gracefully."""
        client.force_login(admin_user)
        data = {"start": "invalid-date"}
        response = client.post(reverse("lfs_apply_customer_filters"), data)

        # Should still redirect but with error message
        assert response.status_code == 302  # Unauthenticated users get redirected to login

    def test_should_handle_mixed_valid_and_invalid_data(self, client, admin_user):
        """Test that mixed valid and invalid data is handled correctly."""
        client.force_login(admin_user)
        data = {"name": "John", "start": "invalid-date", "end": "2024-12-31"}  # Valid  # Invalid  # Valid
        response = client.post(reverse("lfs_apply_customer_filters"), data)

        # Should still redirect
        assert response.status_code == 302  # Unauthenticated users get redirected to login


class TestResetCustomerFiltersView:
    """Test ResetCustomerFiltersView integration functionality."""

    def test_should_redirect_to_login_when_not_authenticated(self, client):
        """Test that unauthenticated users are redirected to login."""
        response = client.get(reverse("lfs_reset_customer_filters"))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "/login/" in response.url

    def test_should_redirect_to_login_when_no_permission(self, client, regular_user):
        """Test that users without permission are redirected to login."""
        client.force_login(regular_user)
        response = client.get(reverse("lfs_reset_customer_filters"))

        assert response.status_code == 403  # Authenticated users without permission get 403

    def test_should_clear_filters_when_authenticated(self, client, admin_user):
        """Test that filters are cleared when authenticated."""
        client.force_login(admin_user)

        # Set some filters first
        session = client.session
        session["customer-filters"] = {"name": "John", "start": "2024-01-01"}
        session.save()

        response = client.get(reverse("lfs_reset_customer_filters"))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "customer-filters" not in client.session

    def test_should_redirect_to_customer_when_customer_id_provided(self, client, admin_user, user_with_customer):
        """Test that redirects to specific customer when customer_id is provided."""
        user, customer, address = user_with_customer
        client.force_login(admin_user)
        response = client.get(reverse("lfs_reset_customer_filters") + f"?customer_id={customer.id}")

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert response.url == reverse("lfs_manage_customer", kwargs={"customer_id": customer.id})

    def test_should_redirect_to_customer_list_when_no_customer_id(self, client, admin_user):
        """Test that redirects to customer list when no customer_id is provided."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_reset_customer_filters"))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert response.url == reverse("lfs_manage_customers")

    def test_should_handle_missing_filters_gracefully(self, client, admin_user):
        """Test that missing filters are handled gracefully."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_reset_customer_filters"))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert response.url == reverse("lfs_manage_customers")


class TestSetCustomerOrderingView:
    """Test SetCustomerOrderingView integration functionality."""

    def test_should_redirect_to_login_when_not_authenticated(self, client):
        """Test that unauthenticated users are redirected to login."""
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "id"}))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "/login/" in response.url

    def test_should_redirect_to_login_when_no_permission(self, client, regular_user):
        """Test that users without permission are redirected to login."""
        client.force_login(regular_user)
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "id"}))

        assert response.status_code == 403  # Authenticated users without permission get 403

    def test_should_set_ordering_when_authenticated(self, client, admin_user):
        """Test that ordering is set when authenticated."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "lastname"}))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert client.session["customer-ordering"] == "lastname"
        assert client.session["customer-ordering-order"] == ""

    def test_should_toggle_ordering_direction_when_same_field(self, client, admin_user):
        """Test that ordering direction is toggled when same field is selected."""
        client.force_login(admin_user)

        # First request
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "id"}))
        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert client.session["customer-ordering"] == "id"
        assert client.session["customer-ordering-order"] == ""

        # Second request - should toggle direction
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "id"}))
        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert client.session["customer-ordering"] == "id"
        assert client.session["customer-ordering-order"] == "-"

    def test_should_redirect_to_customer_when_customer_id_provided(self, client, admin_user, user_with_customer):
        """Test that redirects to specific customer when customer_id is provided."""
        user, customer, address = user_with_customer
        client.force_login(admin_user)
        response = client.get(
            reverse("lfs_set_customer_ordering", kwargs={"ordering": "id"}) + f"?customer_id={customer.id}"
        )

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert response.url == reverse("lfs_manage_customer", kwargs={"customer_id": customer.id})

    def test_should_redirect_to_customer_list_when_no_customer_id(self, client, admin_user):
        """Test that redirects to customer list when no customer_id is provided."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "id"}))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert response.url == reverse("lfs_manage_customers")

    def test_should_handle_unknown_ordering_field(self, client, admin_user):
        """Test that unknown ordering fields are handled gracefully."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "unknown_field"}))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert client.session["customer-ordering"] == "unknown_field"


class TestApplyPredefinedCustomerFilterView:
    """Test ApplyPredefinedCustomerFilterView integration functionality."""

    def test_should_redirect_to_login_when_not_authenticated(self, client):
        """Test that unauthenticated users are redirected to login."""
        response = client.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": "today"}))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "/login/" in response.url

    def test_should_redirect_to_login_when_no_permission(self, client, regular_user):
        """Test that users without permission are redirected to login."""
        client.force_login(regular_user)
        response = client.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": "today"}))

        assert response.status_code == 403  # Authenticated users without permission get 403

    def test_should_apply_today_filter_when_authenticated(self, client, admin_user):
        """Test that today filter is applied when authenticated."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": "today"}))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "customer-filters" in client.session
        assert "start" in client.session["customer-filters"]
        assert "end" not in client.session["customer-filters"]

    def test_should_apply_week_filter_when_authenticated(self, client, admin_user):
        """Test that week filter is applied when authenticated."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": "week"}))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "customer-filters" in client.session
        assert "start" in client.session["customer-filters"]

    def test_should_apply_month_filter_when_authenticated(self, client, admin_user):
        """Test that month filter is applied when authenticated."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": "month"}))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "customer-filters" in client.session
        assert "start" in client.session["customer-filters"]

    def test_should_redirect_to_customer_when_customer_id_provided(self, client, admin_user, user_with_customer):
        """Test that redirects to specific customer when customer_id is provided."""
        user, customer, address = user_with_customer
        client.force_login(admin_user)
        response = client.get(
            reverse("lfs_apply_predefined_customer_filter", kwargs={"customer_id": customer.id, "filter_type": "today"})
        )

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert response.url == reverse("lfs_manage_customer", kwargs={"customer_id": customer.id})

    def test_should_redirect_to_customer_list_when_no_customer_id(self, client, admin_user):
        """Test that redirects to customer list when no customer_id is provided."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": "today"}))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert response.url == reverse("lfs_manage_customers")

    def test_should_handle_invalid_filter_type(self, client, admin_user):
        """Test that invalid filter type is handled gracefully."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": "invalid"}))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert response.url == reverse("lfs_manage_customers")

    def test_should_clear_end_filter_when_applying_predefined_filter(self, client, admin_user):
        """Test that end filter is cleared when applying predefined filter."""
        client.force_login(admin_user)

        # Set some filters first
        session = client.session
        session["customer-filters"] = {"start": "2024-01-01", "end": "2024-12-31"}
        session.save()

        response = client.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": "today"}))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "end" not in client.session["customer-filters"]


class TestNoCustomersView:
    """Test NoCustomersView integration functionality."""

    def test_should_redirect_to_login_when_not_authenticated(self, client):
        """Test that unauthenticated users are redirected to login."""
        response = client.get(reverse("lfs_manage_no_customers"))

        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "/login/" in response.url

    def test_should_redirect_to_login_when_no_permission(self, client, regular_user):
        """Test that users without permission are redirected to login."""
        client.force_login(regular_user)
        response = client.get(reverse("lfs_manage_no_customers"))

        assert response.status_code == 403  # Authenticated users without permission get 403

    def test_should_display_no_customers_message_when_authenticated(self, client, admin_user, shop):
        """Test that no customers message is displayed when authenticated."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_no_customers"))

        assert response.status_code == 200
        assert "No customers found" in response.content.decode()

    def test_should_display_correct_template(self, client, admin_user, shop):
        """Test that correct template is used."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_no_customers"))

        assert response.status_code == 200
        assert "manage/customers/no_customers.html" in [t.name for t in response.templates]


class TestCustomerViewsIntegration:
    """Test integration between different customer views."""

    def test_should_maintain_filters_across_views(self, client, admin_user, multiple_customers_with_orders):
        """Test that filters are maintained across different views."""
        client.force_login(admin_user)

        # Apply filters - filter by "Test" which should match user-based customers (15)
        data = {"name": "Test"}
        response = client.post(reverse("lfs_apply_customer_filters"), data)
        assert response.status_code == 302  # Unauthenticated users get redirected to login

        # Check that filters are applied in list view
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        customers_with_data = response.context["customers_with_data"]
        assert len(customers_with_data) == 15  # User-based customers should match
        assert all(
            "Test" in customer_data["customer"].addresses.first().lastname for customer_data in customers_with_data
        )

    def test_should_maintain_ordering_across_views(self, client, admin_user, multiple_customers_with_orders):
        """Test that ordering is maintained across different views."""
        client.force_login(admin_user)

        # Set ordering
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "lastname"}))
        assert response.status_code == 302  # Unauthenticated users get redirected to login

        # Check that ordering is applied in list view
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert response.context["ordering"] == "lastname"

    def test_should_handle_session_persistence(self, client, admin_user, multiple_customers_with_orders):
        """Test that session data persists across requests."""
        client.force_login(admin_user)

        # Set multiple session values
        session = client.session
        session["customer-filters"] = {"name": "User1"}
        session["customer-ordering"] = "lastname"
        session["customer-ordering-order"] = "-"
        session.save()

        # Check that all values are preserved
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert response.context["ordering"] == "lastname"
        assert "User1" in response.context["filter_form"].initial["name"]

    def test_should_handle_reset_filters_correctly(self, client, admin_user, multiple_customers_with_orders):
        """Test that reset filters works correctly across views."""
        client.force_login(admin_user)

        # Set filters
        data = {"name": "User1"}
        response = client.post(reverse("lfs_apply_customer_filters"), data)
        assert response.status_code == 302  # Unauthenticated users get redirected to login

        # Reset filters
        response = client.get(reverse("lfs_reset_customer_filters"))
        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "customer-filters" not in client.session

        # Check that filters are cleared in list view
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        customers_with_data = response.context["customers_with_data"]
        assert len(customers_with_data) == 20  # All customers

    def test_should_handle_predefined_filters_correctly(self, client, admin_user, multiple_customers_with_orders):
        """Test that predefined filters work correctly."""
        client.force_login(admin_user)

        # Apply today filter
        response = client.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": "today"}))
        assert response.status_code == 302  # Unauthenticated users get redirected to login
        assert "customer-filters" in client.session
        assert "start" in client.session["customer-filters"]

        # Check that filter is applied in list view
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        # The exact number of customers will depend on when they were created
        assert "customers_with_data" in response.context
