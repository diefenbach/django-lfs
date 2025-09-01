import pytest
from datetime import datetime, timedelta
from django.test import RequestFactory
from django.utils import timezone

from lfs.cart.models import Cart
from lfs.manage.carts.services import CartFilterService


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def cart_filter_service():
    return CartFilterService()


@pytest.fixture
def sample_carts():
    """Create sample carts for testing."""
    now = timezone.now()

    # Create carts with different modification dates
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


@pytest.mark.django_db
class TestCartFilterService:
    """Test the CartFilterService class."""

    def test_filter_carts_with_start_date_only(self, cart_filter_service, sample_carts):
        """Test filtering carts with only start date."""
        # Use a date in the past since our test carts are created with past dates
        filters = {"start": "2023-01-01"}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return carts modified after start date
        assert queryset.count() > 0
        for cart in queryset:
            assert cart.modification_date >= timezone.make_aware(datetime(2023, 1, 1, 0, 0, 0))

    def test_filter_carts_with_end_date_only(self, cart_filter_service, sample_carts):
        """Test filtering carts with only end date."""
        # Use a date in the future since our test carts are created with current dates
        filters = {"end": "2025-12-31"}

        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return carts modified before end date
        assert queryset.count() > 0
        for cart in queryset:
            assert cart.modification_date <= timezone.make_aware(datetime(2025, 12, 31, 23, 59, 59))

    def test_filter_carts_with_date_range(self, cart_filter_service, sample_carts):
        """Test filtering carts with both start and end dates."""
        # Use a date range that includes our test carts
        filters = {"start": "2025-01-01", "end": "2025-12-31"}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return carts within the date range
        assert queryset.count() > 0
        for cart in queryset:
            assert timezone.make_aware(datetime(2025, 1, 1, 0, 0, 0)) <= cart.modification_date
            assert cart.modification_date <= timezone.make_aware(datetime(2025, 12, 31, 23, 59, 59))

    def test_filter_carts_with_no_filters(self, cart_filter_service, sample_carts):
        """Test filtering carts with no filters applied."""
        filters = {}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return all carts
        assert queryset.count() == len(sample_carts)

    def test_filter_carts_with_invalid_dates(self, cart_filter_service, sample_carts):
        """Test filtering carts with invalid date formats."""
        filters = {"start": "invalid-date", "end": "also-invalid"}
        queryset = cart_filter_service.filter_carts(Cart.objects.all(), filters)

        # Should return all carts when dates are invalid
        assert queryset.count() == len(sample_carts)

    def test_parse_iso_date_valid(self, cart_filter_service):
        """Test parsing valid ISO date strings."""
        date_str = "2024-01-15"
        result = cart_filter_service.parse_iso_date(date_str)

        assert result == datetime(2024, 1, 15)

    def test_parse_iso_date_invalid(self, cart_filter_service):
        """Test parsing invalid date strings."""
        invalid_dates = ["", "invalid", "2024-13-45", None]

        for date_str in invalid_dates:
            result = cart_filter_service.parse_iso_date(date_str)
            assert result is None

    def test_format_iso_date_valid(self, cart_filter_service):
        """Test formatting valid datetime objects."""
        date_obj = datetime(2024, 1, 15, 14, 30, 0)
        result = cart_filter_service.format_iso_date(date_obj)

        assert result == "2024-01-15"

    def test_format_iso_date_none(self, cart_filter_service):
        """Test formatting None date."""
        result = cart_filter_service.format_iso_date(None)
        assert result == ""
