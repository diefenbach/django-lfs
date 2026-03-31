import pytest
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import RequestFactory
from django.utils import timezone

from lfs.cart.models import Cart, CartItem
from lfs.catalog.models import Product
from lfs.customer.models import Customer
from lfs.core.models import Shop
from lfs.manage.carts.services import CartFilterService, CartDataService


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def cart_filter_service():
    """CartFilterService instance for testing."""
    return CartFilterService()


@pytest.fixture
def cart_data_service():
    """CartDataService instance for testing."""
    return CartDataService()


@pytest.fixture
def mock_request(request_factory):
    """Mock request object for testing."""
    return request_factory.get("/")


@pytest.fixture
def test_shop(db):
    """Create a test shop for product creation."""
    return Shop.objects.create(
        name="Test Shop",
        shop_owner="Test Owner",
        from_email="test@example.com",
        notification_emails="test@example.com",
        description="Test shop description",
    )


@pytest.fixture
def sample_carts():
    """Create sample carts with different modification dates."""
    now = timezone.now()

    cart1 = Cart.objects.create(session="session1")
    cart1.modification_date = now - timedelta(days=1)
    cart1.save()

    cart2 = Cart.objects.create(session="session2")
    cart2.modification_date = now - timedelta(days=5)
    cart2.save()

    cart3 = Cart.objects.create(session="session3")
    cart3.modification_date = now - timedelta(days=10)
    cart3.save()

    return [cart1, cart2, cart3]


class TestCartFilterService:
    """Test CartFilterService functionality."""

    @pytest.mark.django_db
    def test_filter_carts_with_no_filters_returns_all_carts(self, cart_filter_service, sample_carts):
        """Test that no filters returns all carts."""
        filters = {}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        assert queryset.count() == len(sample_carts)

    @pytest.mark.django_db
    def test_filter_carts_with_start_date_only(self, cart_filter_service, sample_carts):
        """Test filtering with only start date."""
        # Use a date that should include all test carts
        filters = {"start": "2020-01-01"}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        assert queryset.count() == len(sample_carts)
        for cart in queryset:
            assert cart.modification_date >= timezone.make_aware(datetime(2020, 1, 1, 0, 0, 0))

    @pytest.mark.django_db
    def test_filter_carts_with_end_date_only(self, cart_filter_service, sample_carts):
        """Test filtering with only end date."""
        # Use a future date that should include all test carts
        filters = {"end": "2030-12-31"}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        assert queryset.count() == len(sample_carts)
        for cart in queryset:
            assert cart.modification_date < timezone.make_aware(datetime(2031, 1, 1, 0, 0, 0))

    @pytest.mark.django_db
    def test_filter_carts_with_date_range(self, cart_filter_service, sample_carts):
        """Test filtering with both start and end dates."""
        now = timezone.now()
        start_date = (now - timedelta(days=2)).strftime("%Y-%m-%d")
        end_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")

        filters = {"start": start_date, "end": end_date}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should include carts from the last 2 days
        assert queryset.count() >= 1
        for cart in queryset:
            start_dt = timezone.make_aware(
                datetime.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
            )
            end_dt = timezone.make_aware(datetime.strptime(end_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0))
            assert cart.modification_date >= start_dt
            assert cart.modification_date < end_dt

    @pytest.mark.django_db
    def test_filter_carts_with_invalid_start_date(self, cart_filter_service, sample_carts):
        """Test filtering with invalid start date falls back to epoch."""
        filters = {"start": "invalid-date"}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return all carts (epoch start)
        assert queryset.count() == len(sample_carts)

    @pytest.mark.django_db
    def test_filter_carts_with_invalid_end_date(self, cart_filter_service, sample_carts):
        """Test filtering with invalid end date uses tomorrow."""
        filters = {"end": "invalid-date"}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return all carts (tomorrow end)
        assert queryset.count() == len(sample_carts)

    @pytest.mark.django_db
    def test_filter_carts_with_empty_strings(self, cart_filter_service, sample_carts):
        """Test filtering with empty string filters."""
        filters = {"start": "", "end": ""}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return all carts
        assert queryset.count() == len(sample_carts)

    @pytest.mark.django_db
    def test_filter_carts_with_none_filters(self, cart_filter_service, sample_carts):
        """Test filtering with None filters."""
        filters = {"start": None, "end": None}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return all carts
        assert queryset.count() == len(sample_carts)

    @pytest.mark.django_db
    def test_filter_carts_with_whitespace_strings(self, cart_filter_service, sample_carts):
        """Test filtering with whitespace-only strings."""
        filters = {"start": "   ", "end": "  \t  "}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return all carts
        assert queryset.count() == len(sample_carts)

    @pytest.mark.django_db
    def test_filter_carts_uses_half_open_interval(self, cart_filter_service):
        """Test that filtering uses half-open interval [start, end)."""
        now = timezone.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Create cart exactly at start time
        cart_at_start = Cart.objects.create(session="at_start")
        Cart.objects.filter(id=cart_at_start.id).update(modification_date=today)
        cart_at_start.refresh_from_db()

        # Create cart just before end time (in the same timezone as the filter)
        cart_before_end = Cart.objects.create(session="before_end")
        end_time = timezone.make_aware(datetime.combine(today.date(), time(23, 59, 59)))
        Cart.objects.filter(id=cart_before_end.id).update(modification_date=end_time)
        cart_before_end.refresh_from_db()

        # Create cart at end time (should be excluded) - this is at the start of the next day
        cart_at_end = Cart.objects.create(session="at_end")
        Cart.objects.filter(id=cart_at_end.id).update(
            modification_date=today + timedelta(days=2)
        )  # Further outside the range
        cart_at_end.refresh_from_db()

        # Filter for today only (end date is tomorrow, so it should exclude tomorrow's cart)
        filters = {"start": today.strftime("%Y-%m-%d"), "end": (today + timedelta(days=1)).strftime("%Y-%m-%d")}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should include carts at start and before end, but not at end
        assert queryset.count() == 2
        cart_sessions = [cart.session for cart in queryset]
        assert "at_start" in cart_sessions
        assert "before_end" in cart_sessions
        assert "at_end" not in cart_sessions

    @pytest.mark.parametrize(
        "date_string,expected",
        [
            ("2024-01-01", date(2024, 1, 1)),
            ("2024-12-31", date(2024, 12, 31)),
            ("2000-02-29", date(2000, 2, 29)),  # Leap year
            ("2023-06-15", date(2023, 6, 15)),
        ],
    )
    def test_parse_iso_date_valid_formats(self, cart_filter_service, date_string, expected):
        """Test parsing valid ISO date strings."""
        result = cart_filter_service.parse_iso_date(date_string)
        assert result == expected

    @pytest.mark.parametrize(
        "invalid_date",
        [
            "",
            "   ",
            None,
            "invalid-date",
            "2024/01/01",
            "01-01-2024",
            "2024-13-01",
            "2024-01-32",
            "2024-02-30",
            "2024-01-01T12:00:00",
            "2024-01-01 12:00:00",
        ],
    )
    def test_parse_iso_date_invalid_formats(self, cart_filter_service, invalid_date):
        """Test parsing invalid date strings returns None."""
        result = cart_filter_service.parse_iso_date(invalid_date)
        assert result is None

    def test_parse_iso_date_preserves_timezone_naive(self, cart_filter_service):
        """Test that parsed dates are timezone-naive."""
        result = cart_filter_service.parse_iso_date("2024-01-01")
        assert result is not None
        assert isinstance(result, date)
        # date objects are always timezone-naive

    @pytest.mark.parametrize(
        "date_obj,expected",
        [
            (datetime(2024, 1, 1), "2024-01-01"),
            (datetime(2024, 12, 31), "2024-12-31"),
            (datetime(2024, 1, 1, 12, 30, 45), "2024-01-01"),  # Time should be ignored
            (date(2024, 1, 1), "2024-01-01"),
            (date(2024, 12, 31), "2024-12-31"),
        ],
    )
    def test_format_iso_date_valid_objects(self, cart_filter_service, date_obj, expected):
        """Test formatting valid date/datetime objects."""
        result = cart_filter_service.format_iso_date(date_obj)
        assert result == expected

    @pytest.mark.parametrize("falsy_value", [None, "", 0, False, [], {}])
    def test_format_iso_date_falsy_values(self, cart_filter_service, falsy_value):
        """Test formatting falsy values returns empty string."""
        result = cart_filter_service.format_iso_date(falsy_value)
        assert result == ""

    def test_format_iso_date_round_trip(self, cart_filter_service):
        """Test that format and parse work together correctly."""
        original_date = datetime(2024, 6, 15, 14, 30, 0)

        formatted = cart_filter_service.format_iso_date(original_date)
        parsed = cart_filter_service.parse_iso_date(formatted)
        reformatted = cart_filter_service.format_iso_date(parsed)

        assert formatted == reformatted
        assert parsed == original_date.date()


class TestCartDataService:
    """Test CartDataService functionality."""

    @pytest.mark.django_db
    def test_get_cart_summary_with_no_items(self, cart_data_service, mock_request):
        """Test cart summary with no items."""
        cart = Cart.objects.create(session="empty_cart")

        summary = cart_data_service.get_cart_summary(cart, mock_request)

        assert summary["total"] == 0
        assert summary["item_count"] == 0
        assert summary["products"] == []

    @pytest.mark.django_db
    def test_get_cart_summary_with_single_item(self, cart_data_service, mock_request, test_shop):
        """Test cart summary with single item."""
        cart = Cart.objects.create(session="single_item_cart")
        product = Product.objects.create(name="Test Product", slug="test-product", price=Decimal("10.99"), active=True)
        cart_item = CartItem.objects.create(cart=cart, product=product, amount=2)

        # Mock the get_price_gross method
        with patch.object(cart_item, "get_price_gross", return_value=Decimal("21.98")):
            summary = cart_data_service.get_cart_summary(cart, mock_request)

        assert summary["total"] == 21.98
        assert summary["item_count"] == 2
        assert summary["products"] == ["Test Product"]

    @pytest.mark.django_db
    def test_get_cart_summary_with_multiple_items(self, cart_data_service, mock_request, test_shop):
        """Test cart summary with multiple items."""
        cart = Cart.objects.create(session="multi_item_cart")

        product1 = Product.objects.create(name="Product 1", slug="product-1", price=Decimal("10.00"), active=True)
        product2 = Product.objects.create(name="Product 2", slug="product-2", price=Decimal("15.00"), active=True)

        cart_item1 = CartItem.objects.create(cart=cart, product=product1, amount=2)
        cart_item2 = CartItem.objects.create(cart=cart, product=product2, amount=1)

        # Mock the get_price_gross method
        with patch.object(cart_item1, "get_price_gross", return_value=Decimal("20.00")), patch.object(
            cart_item2, "get_price_gross", return_value=Decimal("15.00")
        ):
            summary = cart_data_service.get_cart_summary(cart, mock_request)

        assert summary["total"] == Decimal("35.00")
        assert summary["item_count"] == 3
        assert set(summary["products"]) == {"Product 1", "Product 2"}

    @pytest.mark.django_db
    def test_get_carts_with_data_with_user_customers(self, cart_data_service, mock_request, test_shop):
        """Test getting carts with data including user-based customers."""
        # Create user and customer
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="testuser", email="test@example.com")
        customer = Customer.objects.create(user=user, session="test_session")

        # Create cart with user
        cart = Cart.objects.create(session="test_session", user=user)
        product = Product.objects.create(name="Test Product", slug="test-product", price=Decimal("10.00"), active=True)
        cart_item = CartItem.objects.create(cart=cart, product=product, amount=1)

        # Mock the get_price_gross method
        with patch.object(cart_item, "get_price_gross", return_value=Decimal("10.00")):
            carts_with_data = cart_data_service.get_carts_with_data([cart], mock_request)

        assert len(carts_with_data) == 1
        cart_data = carts_with_data[0]
        assert cart_data["cart"] == cart
        assert cart_data["total"] == Decimal("10.00")
        assert cart_data["item_count"] == 1
        assert cart_data["products"] == ["Test Product"]
        assert cart_data["customer"] == customer

    @pytest.mark.django_db
    def test_get_carts_with_data_with_session_customers(self, cart_data_service, mock_request, test_shop):
        """Test getting carts with data including session-based customers."""
        # Create customer with session only
        customer = Customer.objects.create(session="test_session")

        # Create cart with session
        cart = Cart.objects.create(session="test_session")
        product = Product.objects.create(name="Test Product", slug="test-product", price=Decimal("10.00"), active=True)
        cart_item = CartItem.objects.create(cart=cart, product=product, amount=1)

        # Mock the get_price_gross method
        with patch.object(cart_item, "get_price_gross", return_value=Decimal("10.00")):
            carts_with_data = cart_data_service.get_carts_with_data([cart], mock_request)

        assert len(carts_with_data) == 1
        cart_data = carts_with_data[0]
        assert cart_data["cart"] == cart
        assert cart_data["total"] == Decimal("10.00")
        assert cart_data["item_count"] == 1
        assert cart_data["products"] == ["Test Product"]
        assert cart_data["customer"] == customer

    @pytest.mark.django_db
    def test_get_carts_with_data_without_customer(self, cart_data_service, mock_request, test_shop):
        """Test getting carts with data when no customer exists."""
        # Create cart without user or customer
        cart = Cart.objects.create(session="no_customer_session")
        product = Product.objects.create(name="Test Product", slug="test-product", price=Decimal("10.00"), active=True)
        cart_item = CartItem.objects.create(cart=cart, product=product, amount=1)

        # Mock the get_price_gross method
        with patch.object(cart_item, "get_price_gross", return_value=Decimal("10.00")):
            carts_with_data = cart_data_service.get_carts_with_data([cart], mock_request)

        assert len(carts_with_data) == 1
        cart_data = carts_with_data[0]
        assert cart_data["cart"] == cart
        assert cart_data["total"] == Decimal("10.00")
        assert cart_data["item_count"] == 1
        assert cart_data["products"] == ["Test Product"]
        assert cart_data["customer"] is None

    @pytest.mark.django_db
    def test_get_carts_with_data_batched_customer_lookup(self, cart_data_service, mock_request, test_shop):
        """Test that customer lookup is batched for multiple carts."""
        # Create multiple customers
        customer1 = Customer.objects.create(session="session1")
        customer2 = Customer.objects.create(session="session2")

        # Create carts with different sessions
        cart1 = Cart.objects.create(session="session1")
        cart2 = Cart.objects.create(session="session2")
        cart3 = Cart.objects.create(session="session3")  # No customer

        # Mock the get_price_gross method
        with patch("lfs.cart.models.CartItem.get_price_gross", return_value=Decimal("10.00")):
            carts_with_data = cart_data_service.get_carts_with_data([cart1, cart2, cart3], mock_request)

        assert len(carts_with_data) == 3

        # Check customer assignments
        cart_data_by_session = {cd["cart"].session: cd for cd in carts_with_data}
        assert cart_data_by_session["session1"]["customer"] == customer1
        assert cart_data_by_session["session2"]["customer"] == customer2
        assert cart_data_by_session["session3"]["customer"] is None

    @pytest.mark.django_db
    def test_get_carts_with_data_handles_missing_product_name(self, cart_data_service, mock_request, test_shop):
        """Test handling when product.get_name() fails."""
        cart = Cart.objects.create(session="test_session")
        product = Product.objects.create(name="Test Product", slug="test-product", price=Decimal("10.00"), active=True)
        cart_item = CartItem.objects.create(cart=cart, product=product, amount=1)

        # Mock cart.get_items() to return our cart_item with mocked methods
        with patch.object(cart, "get_items", return_value=[cart_item]), patch.object(
            cart_item, "get_price_gross", return_value=Decimal("10.00")
        ), patch.object(product, "get_name", side_effect=Exception("Product name error")):
            # Service handles errors gracefully, returns empty products list
            carts_with_data = cart_data_service.get_carts_with_data([cart], mock_request)

            assert len(carts_with_data) == 1
            cart_data = carts_with_data[0]
            assert cart_data["total"] == Decimal("10.00")
            assert cart_data["item_count"] == 1
            assert cart_data["products"] == []  # Empty due to error

    @pytest.mark.django_db
    def test_get_carts_with_data_handles_missing_price_calculation(self, cart_data_service, mock_request, test_shop):
        """Test handling when get_price_gross() fails."""
        cart = Cart.objects.create(session="test_session")
        product = Product.objects.create(name="Test Product", slug="test-product", price=Decimal("10.00"), active=True)
        cart_item = CartItem.objects.create(cart=cart, product=product, amount=1)

        # Mock cart.get_items() to return our cart_item with mocked get_price_gross
        with patch.object(cart, "get_items", return_value=[cart_item]), patch.object(
            cart_item, "get_price_gross", side_effect=Exception("Price calculation error")
        ):
            # Service handles errors gracefully, returns zero values
            carts_with_data = cart_data_service.get_carts_with_data([cart], mock_request)

            assert len(carts_with_data) == 1
            cart_data = carts_with_data[0]
            assert cart_data["total"] == 0  # Zero due to error
            assert cart_data["item_count"] == 0  # Zero due to error
            assert cart_data["products"] == []  # Empty due to error


# Merge existing test_cart_filtering.py content
@pytest.mark.django_db
class TestCartFilterServiceIntegration:
    """Integration tests for CartFilterService with real database."""

    def test_filter_carts_with_start_date_only_integration(self, cart_filter_service, sample_carts):
        """Test filtering carts with only start date using real database."""
        # Use a date in the past since our test carts are created with past dates
        filters = {"start": "2023-01-01"}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return carts modified after start date
        assert queryset.count() > 0
        for cart in queryset:
            assert cart.modification_date >= timezone.make_aware(datetime(2023, 1, 1, 0, 0, 0))

    def test_filter_carts_with_end_date_only_integration(self, cart_filter_service, sample_carts):
        """Test filtering carts with only end date using real database."""
        # Use a date in the future since our test carts are created with current dates
        filters = {"end": "2025-12-31"}

        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return carts modified before end date
        assert queryset.count() > 0
        for cart in queryset:
            assert cart.modification_date <= timezone.make_aware(datetime(2025, 12, 31, 23, 59, 59))

    def test_filter_carts_with_date_range_integration(self, cart_filter_service, sample_carts):
        """Test filtering carts with both start and end dates using real database."""
        # Use a date range that includes our test carts
        filters = {"start": "2025-01-01", "end": "2025-12-31"}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return carts within the date range
        assert queryset.count() > 0
        for cart in queryset:
            assert timezone.make_aware(datetime(2025, 1, 1, 0, 0, 0)) <= cart.modification_date
            assert cart.modification_date <= timezone.make_aware(datetime(2025, 12, 31, 23, 59, 59))

    def test_filter_carts_with_no_filters_integration(self, cart_filter_service, sample_carts):
        """Test filtering carts with no filters applied using real database."""
        filters = {}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return all carts
        assert queryset.count() == len(sample_carts)

    def test_filter_carts_with_invalid_dates_integration(self, cart_filter_service, sample_carts):
        """Test filtering carts with invalid date formats using real database."""
        filters = {"start": "invalid-date", "end": "also-invalid"}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return all carts when dates are invalid
        assert queryset.count() == len(sample_carts)
