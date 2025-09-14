"""
Pytest configuration and shared fixtures for order tests.
"""

import pytest
from decimal import Decimal

from lfs.core.models import Shop
from lfs.order.models import OrderItem
from lfs.catalog.models import Product
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
def product(db):
    """Create a test product."""
    return Product.objects.create(
        name="Test Product",
        slug="test-product",
        sku="TEST001",
        price=Decimal("10.00"),
        active=True,
    )


@pytest.fixture
def order_item(db, order, product):
    """Create a test order item."""
    return OrderItem.objects.create(
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
        username="manage_user", email="manage@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def regular_user(db):
    """Regular user without special permissions."""
    return User.objects.create_user(username="regular", email="regular@example.com", password="testpass123")


# Order-specific fixtures that don't conflict with main conftest.py
