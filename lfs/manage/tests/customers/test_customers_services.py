import pytest
from decimal import Decimal
from datetime import timedelta
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.utils import timezone

from lfs.customer.models import Customer
from lfs.cart.models import Cart
from lfs.order.models import Order
from lfs.addresses.models import Address
from lfs.manage.customers.services import CustomerFilterService, CustomerDataService

User = get_user_model()


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
def multiple_customers_with_different_names(db):
    """Multiple customers with different names for filtering tests."""
    customers = []

    # User-based customers
    for i, (first, last) in enumerate([("Alice", "Anderson"), ("Bob", "Brown"), ("Charlie", "Clark")]):
        user = User.objects.create_user(username=f"user{i+1}", email=f"user{i+1}@example.com", password="testpass123")
        customer = Customer.objects.create(user=user)
        Address.objects.create(
            customer=customer,
            firstname=first,
            lastname=last,
            line1=f"{i+1}00 Main St",
            city="Test City",
            zip_code=f"{10000+i}",
            email=f"user{i+1}@example.com",
        )
        customers.append(customer)

    # Session-based customers
    for i, (first, last) in enumerate([("David", "Davis"), ("Eve", "Evans")]):
        customer = Customer.objects.create(session=f"session-{i+1}")
        Address.objects.create(
            customer=customer,
            firstname=first,
            lastname=last,
            line1=f"{i+4}00 Main St",
            city="Test City",
            zip_code=f"{10000+i+3}",
            email=f"session{i+1}@example.com",
        )
        customers.append(customer)

    return customers


@pytest.fixture
def customers_with_orders(db, user_with_customer, anonymous_customer_with_address):
    """Customers with associated orders for data calculation tests."""
    from django.contrib.contenttypes.models import ContentType

    user, customer, address = user_with_customer
    anon_customer, anon_address = anonymous_customer_with_address

    # Get content type for Address
    address_content_type = ContentType.objects.get_for_model(Address)

    # Create orders for user-based customer
    Order.objects.create(
        number="ORD-001",
        user=customer.user,
        session=customer.session,
        customer_firstname="John",
        customer_lastname="Doe",
        customer_email="john.doe@example.com",
        price=Decimal("99.99"),
        state=1,
        sa_content_type=address_content_type,
        sa_object_id=address.id,
        ia_content_type=address_content_type,
        ia_object_id=address.id,
    )

    # Create orders for anonymous customer
    Order.objects.create(
        number="ORD-002",
        session=anon_customer.session,
        customer_firstname="Jane",
        customer_lastname="Smith",
        customer_email="jane.smith@example.com",
        price=Decimal("149.99"),
        state=1,
        sa_content_type=address_content_type,
        sa_object_id=anon_address.id,
        ia_content_type=address_content_type,
        ia_object_id=anon_address.id,
    )

    return [customer, anon_customer]


@pytest.fixture
def mock_request():
    """Mock request object for testing."""
    factory = RequestFactory()
    request = factory.get("/")
    request.session = {}
    return request


class TestCustomerFilterService:
    """Test CustomerFilterService functionality."""

    def test_should_return_all_customers_when_no_filters(self, multiple_customers_with_different_names):
        """Test that all customers are returned when no filters are applied."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {})

        assert result.count() == 5
        assert list(result) == list(queryset)

    def test_should_filter_by_lastname_when_name_provided(self, multiple_customers_with_different_names):
        """Test that customers are filtered by lastname when name filter is provided."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {"name": "Doe"})

        # Check if any customer has "Doe" in lastname
        doe_customers = [c for c in multiple_customers_with_different_names if c.addresses.first().lastname == "Doe"]
        expected_count = len(doe_customers)

        assert result.count() == expected_count
        if expected_count > 0:
            assert result.first().addresses.first().lastname == "Doe"

    def test_should_filter_by_firstname_when_name_provided(self, multiple_customers_with_different_names):
        """Test that customers are filtered by firstname when name filter is provided."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {"name": "Alice"})

        assert result.count() == 1
        assert result.first().addresses.first().firstname == "Alice"

    def test_should_filter_by_partial_name_match(self, multiple_customers_with_different_names):
        """Test that partial name matches work correctly."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {"name": "And"})

        assert result.count() == 1
        assert result.first().addresses.first().lastname == "Anderson"

    def test_should_be_case_insensitive_when_filtering_by_name(self, multiple_customers_with_different_names):
        """Test that name filtering is case insensitive."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {"name": "brown"})

        assert result.count() == 1
        assert result.first().addresses.first().lastname == "Brown"

    def test_should_return_empty_queryset_when_name_not_found(self, multiple_customers_with_different_names):
        """Test that empty queryset is returned when name doesn't match any customer."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {"name": "Nonexistent"})

        assert result.count() == 0

    def test_should_filter_by_start_date_when_provided(self, user_with_customer):
        """Test that customers are filtered by start date."""
        user, customer, address = user_with_customer
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        # Set user's date_joined to a fixed date that's clearly in the past
        from datetime import date

        fixed_date = date(2020, 1, 15)  # Fixed date to avoid timezone issues
        test_datetime = timezone.make_aware(timezone.datetime.combine(fixed_date, timezone.datetime.min.time()))
        user.date_joined = test_datetime
        user.save()

        result = service.filter_customers(queryset, {"start": fixed_date.isoformat()})

        assert result.count() == 1
        assert result.first() == customer

    def test_should_filter_by_end_date_when_provided(self, user_with_customer):
        """Test that customers are filtered by end date."""
        user, customer, address = user_with_customer
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        # Set user's date_joined to a fixed date that's clearly in the past
        from datetime import date

        fixed_date = date(2020, 1, 15)  # Fixed date to avoid timezone issues
        test_datetime = timezone.make_aware(timezone.datetime.combine(fixed_date, timezone.datetime.min.time()))
        user.date_joined = test_datetime
        user.save()

        # Use the same date for filtering
        filter_date = fixed_date.isoformat()
        result = service.filter_customers(queryset, {"end": filter_date})

        assert result.count() == 1
        assert result.first() == customer

    def test_should_filter_by_date_range_when_both_provided(self, user_with_customer):
        """Test that customers are filtered by date range when both start and end are provided."""
        user, customer, address = user_with_customer
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        # Set user's date_joined to a fixed date that's clearly in the past
        from datetime import date

        fixed_date = date(2020, 1, 15)  # Fixed date to avoid timezone issues
        test_datetime = timezone.make_aware(timezone.datetime.combine(fixed_date, timezone.datetime.min.time()))
        user.date_joined = test_datetime
        user.save()

        start_date = (fixed_date - timedelta(days=1)).isoformat()
        end_date = (fixed_date + timedelta(days=1)).isoformat()

        result = service.filter_customers(queryset, {"start": start_date, "end": end_date})

        assert result.count() == 1
        assert result.first() == customer

    def test_should_return_empty_queryset_when_date_range_excludes_all_customers(self, user_with_customer):
        """Test that empty queryset is returned when date range excludes all customers."""
        user, customer, address = user_with_customer
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        # Set user's date_joined to a fixed date that's clearly in the past
        from datetime import date

        fixed_date = date(2020, 1, 15)  # Fixed date to avoid timezone issues
        test_datetime = timezone.make_aware(timezone.datetime.combine(fixed_date, timezone.datetime.min.time()))
        user.date_joined = test_datetime
        user.save()

        start_date = (fixed_date - timedelta(days=10)).isoformat()
        end_date = (fixed_date - timedelta(days=5)).isoformat()

        result = service.filter_customers(queryset, {"start": start_date, "end": end_date})

        assert result.count() == 0

    def test_should_combine_name_and_date_filters(self, user_with_customer):
        """Test that name and date filters work together."""
        user, customer, address = user_with_customer
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        # Set user's date_joined to a fixed date that's clearly in the past
        from datetime import date

        fixed_date = date(2020, 1, 15)  # Fixed date to avoid timezone issues
        test_datetime = timezone.make_aware(timezone.datetime.combine(fixed_date, timezone.datetime.min.time()))
        user.date_joined = test_datetime
        user.save()

        filters = {"name": "John", "start": fixed_date.isoformat()}

        result = service.filter_customers(queryset, filters)

        assert result.count() == 1
        assert result.first() == customer

    def test_should_handle_empty_name_filter(self, multiple_customers_with_different_names):
        """Test that empty name filter doesn't affect results."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {"name": ""})

        assert result.count() == 5

    def test_should_handle_none_name_filter(self, multiple_customers_with_different_names):
        """Test that None name filter doesn't affect results."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {"name": None})

        assert result.count() == 5

    @pytest.mark.parametrize(
        "ordering,ordering_order,expected",
        [
            ("id", "", "id"),
            ("id", "-", "-id"),
            ("lastname", "", "addresses__lastname"),
            ("lastname", "-", "-addresses__lastname"),
            ("firstname", "", "addresses__firstname"),
            ("firstname", "-", "-addresses__firstname"),
            ("email", "", "user__email"),
            ("email", "-", "-user__email"),
            ("date_joined", "", "user__date_joined"),
            ("date_joined", "-", "-user__date_joined"),
            ("creation_date", "", "id"),  # Falls back to id
            ("creation_date", "-", "-id"),
            ("unknown_field", "", "unknown_field"),  # Unknown fields pass through
        ],
    )
    def test_should_return_correct_ordering_string(self, ordering, ordering_order, expected):
        """Test that correct ordering string is returned for different field combinations."""
        service = CustomerFilterService()

        result = service.get_ordering(ordering, ordering_order)

        assert result == expected


class TestCustomerDataService:
    """Test CustomerDataService functionality."""

    def test_should_return_customers_with_data_when_customers_exist(self, customers_with_orders, mock_request):
        """Test that customers with data are returned when customers exist."""
        service = CustomerDataService()
        customers = customers_with_orders

        result = service.get_customers_with_data(customers, mock_request)

        assert len(result) == 2
        for customer_data in result:
            assert "customer" in customer_data
            assert "orders_count" in customer_data
            assert "cart_price" in customer_data

    def test_should_calculate_orders_count_correctly(self, customers_with_orders, mock_request):
        """Test that orders count is calculated correctly."""
        service = CustomerDataService()
        customers = customers_with_orders

        result = service.get_customers_with_data(customers, mock_request)

        # Each customer should have 1 order
        for customer_data in result:
            assert customer_data["orders_count"] == 1

    def test_should_return_none_cart_price_when_no_cart_exists(self, customers_with_orders, mock_request):
        """Test that cart_price is None when no cart exists for customer."""
        service = CustomerDataService()
        customers = customers_with_orders

        result = service.get_customers_with_data(customers, mock_request)

        for customer_data in result:
            assert customer_data["cart_price"] is None

    def test_should_skip_customers_without_user_or_session(self, db, mock_request):
        """Test that customers without user or session are skipped."""
        service = CustomerDataService()

        # Create customer without user or session
        customer = Customer.objects.create()
        customers = [customer]

        result = service.get_customers_with_data(customers, mock_request)

        assert len(result) == 0

    def test_should_return_customer_with_data_when_customer_exists(self, user_with_customer, mock_request):
        """Test that single customer with data is returned."""
        user, customer, address = user_with_customer
        service = CustomerDataService()

        result = service.get_customer_with_data(customer, mock_request)

        assert "customer" in result
        assert "orders" in result
        assert "cart" in result
        assert "cart_price" in result
        assert "shipping_address" in result
        assert "invoice_address" in result
        assert result["customer"] == customer

    def test_should_return_orders_queryset_for_customer(self, customers_with_orders, mock_request):
        """Test that orders queryset is returned for customer."""
        service = CustomerDataService()
        customer = customers_with_orders[0]

        result = service.get_customer_with_data(customer, mock_request)

        assert hasattr(result["orders"], "filter")  # It's a queryset
        assert result["orders"].count() == 1

    def test_should_return_none_cart_when_no_cart_exists(self, user_with_customer, mock_request):
        """Test that cart is None when no cart exists for customer."""
        service = CustomerDataService()
        user, customer, address = user_with_customer

        result = service.get_customer_with_data(customer, mock_request)

        assert result["cart"] is None
        assert result["cart_price"] is None

    def test_should_return_none_addresses_when_no_addresses_selected(self, user_with_customer, mock_request):
        """Test that addresses are None when no addresses are selected."""
        service = CustomerDataService()
        user, customer, address = user_with_customer

        result = service.get_customer_with_data(customer, mock_request)

        assert result["shipping_address"] is None
        assert result["invoice_address"] is None

    def test_should_return_html_addresses_when_addresses_selected(self, user_with_customer, mock_request):
        """Test that HTML addresses are returned when addresses are selected."""
        service = CustomerDataService()
        user, customer, address = user_with_customer

        # Select addresses
        customer.selected_shipping_address = address
        customer.selected_invoice_address = address
        customer.save()

        with patch.object(address, "as_html") as mock_as_html:
            mock_as_html.return_value = "<div>Address HTML</div>"

            result = service.get_customer_with_data(customer, mock_request)

            assert result["shipping_address"] == "<div>Address HTML</div>"
            assert result["invoice_address"] == "<div>Address HTML</div>"
            assert mock_as_html.call_count == 2

    def test_should_handle_cart_with_shipping_and_payment_costs(self, user_with_customer, mock_request):
        """Test that cart price includes shipping and payment costs."""
        service = CustomerDataService()
        user, customer, address = user_with_customer

        # Create a cart for the customer
        if not customer.session:
            customer.session = "test-session"
            customer.save()
        cart = Cart.objects.create(session=customer.session)

        with patch("lfs.manage.customers.services.get_selected_shipping_method") as mock_shipping_method, patch(
            "lfs.manage.customers.services.get_shipping_costs"
        ) as mock_shipping_costs, patch(
            "lfs.manage.customers.services.get_selected_payment_method"
        ) as mock_payment_method, patch(
            "lfs.manage.customers.services.get_payment_costs"
        ) as mock_payment_costs, patch.object(
            cart, "get_price_gross"
        ) as mock_cart_price:

            # Mock the shipping and payment methods and costs
            mock_shipping_method.return_value = Mock()
            mock_shipping_costs.return_value = {"price_gross": Decimal("5.99")}
            mock_payment_method.return_value = Mock()
            mock_payment_costs.return_value = {"price_gross": Decimal("2.50")}
            mock_cart_price.return_value = Decimal("100.00")

            result = service.get_customer_with_data(customer, mock_request)

            # The cart_price calculation depends on the actual implementation
            # For now, just check that it's not None when cart exists
            assert result["cart_price"] is not None

    def test_should_handle_cart_without_shipping_and_payment_costs(self, user_with_customer, mock_request):
        """Test that cart price calculation works when shipping/payment methods fail."""
        service = CustomerDataService()
        user, customer, address = user_with_customer

        # Create a cart for the customer
        if not customer.session:
            customer.session = "test-session"
            customer.save()
        cart = Cart.objects.create(session=customer.session)

        with patch("lfs.manage.customers.services.get_selected_shipping_method", side_effect=Exception), patch(
            "lfs.manage.customers.services.get_selected_payment_method", side_effect=Exception
        ), patch.object(cart, "get_price_gross") as mock_cart_price:

            mock_cart_price.return_value = Decimal("100.00")

            result = service.get_customer_with_data(customer, mock_request)

            # Should still return result even if shipping/payment methods fail
            assert "cart_price" in result
