import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal

from django.test import RequestFactory
from django.utils import timezone

from lfs.order.models import Order, OrderItem
from lfs.manage.orders.services import OrderFilterService, OrderDataService


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def order_filter_service():
    """OrderFilterService instance for testing."""
    return OrderFilterService()


@pytest.fixture
def order_data_service():
    """OrderDataService instance for testing."""
    return OrderDataService()


@pytest.fixture
def sample_orders(db, customer, address, payment_method, shipping_method, product):
    """Create sample orders with different states and dates."""
    from django.contrib.contenttypes.models import ContentType

    orders = []
    address_content_type = ContentType.objects.get_for_model(address.__class__)

    # Create orders with different states and dates
    base_date = timezone.now().date()
    for i in range(5):
        order = Order.objects.create(
            user=None,
            session=customer.session,
            state=i % 3,  # Different states (0, 1, 2)
            customer_firstname=f"John{i}",
            customer_lastname=f"Doe{i}",
            customer_email=f"john{i}@example.com",
            price=Decimal("15.00"),
            tax=Decimal("0.00"),
            shipping_price=Decimal("5.00"),
            payment_price=Decimal("0.00"),
            created=base_date - timedelta(days=i),
            # Set address relationships
            sa_content_type=address_content_type,
            sa_object_id=address.id,
            ia_content_type=address_content_type,
            ia_object_id=address.id,
        )

        # Create order item for this order
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            product_price_net=Decimal("10.00"),
            product_price_gross=Decimal("10.00"),
            product_amount=1,
            price_net=Decimal("10.00"),
            price_gross=Decimal("10.00"),
        )
        orders.append(order)

    return orders


class TestOrderFilterService:
    """Test OrderFilterService functionality."""

    def test_filter_orders_no_filters(self, order_filter_service, sample_orders):
        """Should return all orders when no filters provided."""
        queryset = Order.objects.all()
        filters = {}

        result = order_filter_service.filter_orders(queryset, filters)

        assert result.count() == len(sample_orders)

    def test_filter_orders_by_name(self, order_filter_service, sample_orders):
        """Should filter orders by customer name."""
        queryset = Order.objects.all()
        filters = {"name": "John0"}

        result = order_filter_service.filter_orders(queryset, filters)

        assert result.count() == 1
        assert result.first().customer_firstname == "John0"

    def test_filter_orders_by_state(self, order_filter_service, sample_orders):
        """Should filter orders by state."""
        queryset = Order.objects.all()
        filters = {"state": "1"}

        result = order_filter_service.filter_orders(queryset, filters)

        # The sample_orders fixture creates 5 orders with states 0, 1, 2, 0, 1
        # So there should be 2 orders with state 1
        assert result.count() == 2
        assert result.first().state == 1

    def test_filter_orders_by_date_range(self, order_filter_service, sample_orders):
        """Should filter orders by date range."""
        queryset = Order.objects.all()
        # Use a broader date range that should include some sample orders
        base_date = timezone.now().date()
        filters = {"start": str(base_date - timedelta(days=10)), "end": str(base_date + timedelta(days=1))}

        result = order_filter_service.filter_orders(queryset, filters)

        # Should find orders within the date range (sample_orders creates orders from today back to 4 days ago)
        assert result.count() >= 1

    def test_filter_orders_combined_filters(self, order_filter_service, sample_orders):
        """Should apply multiple filters correctly."""
        queryset = Order.objects.all()
        filters = {"name": "John", "state": "2"}

        result = order_filter_service.filter_orders(queryset, filters)

        assert result.count() == 1
        order = result.first()
        assert "John" in order.customer_firstname
        assert order.state == 2

    def test_parse_iso_date_valid(self, order_filter_service):
        """Should parse valid ISO date string."""
        date_string = "2023-12-25"
        result = order_filter_service.parse_iso_date(date_string)

        assert result == date(2023, 12, 25)

    def test_parse_iso_date_invalid(self, order_filter_service):
        """Should return None for invalid date string."""
        invalid_date_strings = ["", "invalid", "2023-13-45", "23-12-25"]

        for date_string in invalid_date_strings:
            result = order_filter_service.parse_iso_date(date_string)
            assert result is None

    def test_parse_iso_date_none(self, order_filter_service):
        """Should return None for None input."""
        result = order_filter_service.parse_iso_date(None)
        assert result is None

    def test_format_iso_date_date_object(self, order_filter_service):
        """Should format date object to ISO string."""
        test_date = date(2023, 12, 25)
        result = order_filter_service.format_iso_date(test_date)

        assert result == "2023-12-25"

    def test_format_iso_date_datetime_object(self, order_filter_service):
        """Should format datetime object to ISO string."""
        test_datetime = datetime(2023, 12, 25, 15, 30, 45)
        result = order_filter_service.format_iso_date(test_datetime)

        assert result == "2023-12-25"

    def test_format_iso_date_string(self, order_filter_service):
        """Should return string as-is."""
        test_string = "2023-12-25"
        result = order_filter_service.format_iso_date(test_string)

        assert result == "2023-12-25"

    def test_format_iso_date_none(self, order_filter_service):
        """Should return empty string for None."""
        result = order_filter_service.format_iso_date(None)
        assert result == ""

    def test_filter_orders_empty_name_filter(self, order_filter_service, sample_orders):
        """Should handle empty name filter gracefully."""
        queryset = Order.objects.all()
        filters = {"name": ""}

        result = order_filter_service.filter_orders(queryset, filters)

        assert result.count() == len(sample_orders)

    def test_filter_orders_invalid_state_filter(self, order_filter_service, sample_orders):
        """Should handle invalid state filter gracefully."""
        queryset = Order.objects.all()
        filters = {"state": "invalid"}

        result = order_filter_service.filter_orders(queryset, filters)

        # Should not crash, should return all orders
        assert result.count() == len(sample_orders)

    def test_filter_orders_case_insensitive_name_search(self, order_filter_service, sample_orders):
        """Should perform case-insensitive name search."""
        queryset = Order.objects.all()
        filters = {"name": "JOHN0"}  # Uppercase

        result = order_filter_service.filter_orders(queryset, filters)

        assert result.count() == 1
        assert result.first().customer_firstname == "John0"


class TestOrderDataService:
    """Test OrderDataService functionality."""

    def test_get_order_summary(self, order_data_service, order, order_item):
        """Should calculate order summary correctly."""
        summary = order_data_service.get_order_summary(order)

        assert "total" in summary
        assert "item_count" in summary
        assert "products" in summary
        assert summary["total"] == order.price
        assert summary["item_count"] == 1
        assert len(summary["products"]) == 1

    def test_get_orders_with_data(self, order_data_service, sample_orders):
        """Should enrich orders with calculated data."""
        orders_with_data = order_data_service.get_orders_with_data(sample_orders)

        assert len(orders_with_data) == len(sample_orders)

        for order_data in orders_with_data:
            assert "order" in order_data
            assert "total" in order_data
            assert "item_count" in order_data
            assert "products" in order_data
            assert "customer_name" in order_data
            assert "state_name" in order_data

    def test_get_order_with_data(self, order_data_service, order):
        """Should enrich single order with calculated data."""
        order_with_data = order_data_service.get_order_with_data(order)

        assert order_with_data is not None
        assert "order" in order_with_data
        assert "total" in order_with_data
        assert "customer_name" in order_with_data
        assert "state_name" in order_with_data

    def test_get_order_with_data_none_input(self, order_data_service):
        """Should handle None input gracefully."""
        # The method now handles None properly and returns None
        result = order_data_service.get_order_with_data(None)
        assert result is None

    def test_get_state_name_valid_state(self, order_data_service):
        """Should return correct state name for valid state ID."""
        # Test a few common states
        assert order_data_service._get_state_name(0) in ["Submitted", "0"]  # State 0 is Submitted
        assert order_data_service._get_state_name(1) in ["Paid", "1"]  # State 1 is Paid

    def test_get_state_name_invalid_state(self, order_data_service):
        """Should return string representation for invalid state ID."""
        result = order_data_service._get_state_name(999)
        assert result == "999"

    def test_get_order_summary_no_items(self, order_data_service, order):
        """Should handle order with no items."""
        # Remove all items from order
        order.items.all().delete()

        summary = order_data_service.get_order_summary(order)

        assert summary["item_count"] == 0
        assert summary["products"] == []

    def test_get_order_summary_multiple_items(self, order_data_service, order, product):
        """Should handle order with multiple items."""
        # First, ensure the order has one item
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name="Test Product",
            product_sku="TEST001",
            product_price_net=Decimal("10.00"),
            product_price_gross=Decimal("10.00"),
            product_amount=1,
            price_net=Decimal("10.00"),
            price_gross=Decimal("10.00"),
        )

        # Add another item to the order with different product name
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name="Different Product",
            product_sku="TEST002",
            product_price_net=Decimal("5.00"),
            product_price_gross=Decimal("5.00"),
            product_amount=2,
            price_net=Decimal("5.00"),
            price_gross=Decimal("10.00"),
        )

        summary = order_data_service.get_order_summary(order)

        assert summary["item_count"] == 3  # 1 + 2
        assert len(summary["products"]) == 2

    def test_get_orders_with_data_empty_list(self, order_data_service):
        """Should handle empty orders list."""
        result = order_data_service.get_orders_with_data([])
        assert result == []

    def test_get_order_summary_with_none_product(self, order_data_service, order):
        """Should handle order items with None product."""
        # Create item with no product reference
        OrderItem.objects.create(
            order=order,
            product=None,
            product_name="Manual Item",
            product_sku="MANUAL",
            product_price_net=Decimal("5.00"),
            product_price_gross=Decimal("5.00"),
            product_amount=1,
            price_net=Decimal("5.00"),
            price_gross=Decimal("5.00"),
        )

        summary = order_data_service.get_order_summary(order)

        # Should not crash, but products list should be shorter
        assert "Manual Item" not in summary["products"]
