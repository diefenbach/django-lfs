"""
Pytest fixtures for CustomerTax testing.

Provides comprehensive test data and utilities for customer tax management tests.
"""

import pytest

from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.customer_tax.models import CustomerTax
from lfs.core.models import Shop

User = get_user_model()


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


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
def customer_tax(db):
    """CustomerTax instance for testing."""
    return CustomerTax.objects.create(rate=19.0, description="Standard VAT")


@pytest.fixture
def multiple_customer_taxes(db):
    """Multiple CustomerTax instances for testing."""
    taxes = []
    for i in range(3):
        tax = CustomerTax.objects.create(
            rate=10.0 + (i * 5.0),
            description=f"Tax {i+1}",
        )
        taxes.append(tax)
    return taxes


@pytest.fixture
def mock_session():
    """Mock session for testing."""
    return {}


@pytest.fixture
def mock_request(admin_user, request_factory):
    """Mock request with admin user."""
    request = request_factory.get("/")
    request.user = admin_user
    request.session = {}
    return request


@pytest.fixture
def shop(db):
    """Shop instance for testing."""
    return Shop.objects.create(name="Test Shop", shop_owner="Test Owner", from_email="test@example.com")


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db, shop):
    """Enable database access for all tests."""
    pass
