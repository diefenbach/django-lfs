"""
Pytest configuration and shared fixtures for delivery times tests.
"""

import pytest
from lfs.core.models import Shop
from lfs.catalog.models import DeliveryTime, DELIVERY_TIME_UNIT_DAYS
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture(scope="session", autouse=True)
def setup_shop_for_tests(django_db_setup, django_db_blocker):
    """Create a default shop for all tests that need it."""
    with django_db_blocker.unblock():
        # Create a default shop if none exists
        if not Shop.objects.exists():
            Shop.objects.create(
                name="Test Shop",
                shop_owner="Test Owner",
                from_email="test@example.com",
                notification_emails="test@example.com",
                description="Test shop description",
            )


@pytest.fixture
def test_shop(db):
    """Create a test shop for individual tests."""
    return Shop.objects.create(
        name="Test Shop",
        shop_owner="Test Owner",
        from_email="test@example.com",
        notification_emails="test@example.com",
        description="Test shop description",
    )


@pytest.fixture
def admin_user(db):
    """Admin user with proper permissions."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def manage_user(db):
    """Create a user with manage permissions."""
    return User.objects.create_user(
        username="manage_user", email="manage@example.com", password="testpass123", is_staff=True
    )


@pytest.fixture
def regular_user(db):
    """Regular user without special permissions."""
    return User.objects.create_user(username="regular", email="regular@example.com", password="testpass123")


@pytest.fixture
def delivery_time(db):
    """Create a sample delivery time for testing."""
    return DeliveryTime.objects.create(min=1.0, max=3.0, unit=DELIVERY_TIME_UNIT_DAYS, description="Standard delivery")


@pytest.fixture
def multiple_delivery_times(db):
    """Create multiple delivery times for testing."""
    return [
        DeliveryTime.objects.create(min=1, max=3, unit=DELIVERY_TIME_UNIT_DAYS, description="Express delivery"),
        DeliveryTime.objects.create(min=2, max=5, unit=DELIVERY_TIME_UNIT_DAYS, description="Standard delivery"),
        DeliveryTime.objects.create(min=5, max=10, unit=DELIVERY_TIME_UNIT_DAYS, description="Economy delivery"),
    ]


@pytest.fixture
def delivery_time_with_search_term(db):
    """Create a delivery time with a specific description for search testing."""
    return DeliveryTime.objects.create(
        min=1.0, max=3.0, unit=DELIVERY_TIME_UNIT_DAYS, description="Express delivery service"
    )


@pytest.fixture
def empty_delivery_times(db):
    """Fixture that ensures no delivery times exist."""
    DeliveryTime.objects.all().delete()
    return []


@pytest.fixture
def delivery_time_edge_cases(db):
    """Create delivery times with edge case values."""
    return [
        DeliveryTime.objects.create(min=0.1, max=0.2, unit=DELIVERY_TIME_UNIT_DAYS, description="Minimum delivery"),
        DeliveryTime.objects.create(
            min=365.0, max=730.0, unit=DELIVERY_TIME_UNIT_DAYS, description="Year long delivery"
        ),
        DeliveryTime.objects.create(min=0.0, max=1.0, unit=DELIVERY_TIME_UNIT_DAYS, description="Immediate delivery"),
    ]


@pytest.fixture
def delivery_time_large_dataset(db):
    """Create a large dataset of delivery times for performance testing."""
    delivery_times = []
    for i in range(100):
        delivery_times.append(
            DeliveryTime.objects.create(
                min=float(i + 1), max=float(i + 3), unit=DELIVERY_TIME_UNIT_DAYS, description=f"Delivery time {i}"
            )
        )
    return delivery_times
