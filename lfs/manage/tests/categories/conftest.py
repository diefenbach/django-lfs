"""
Test fixtures and configuration for category tests.

Following TDD principles:
- Shared fixtures for all category tests
- Clean setup and teardown
- Minimal mocking with real objects when possible
- Fast test execution
"""

import pytest
from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.catalog.models import Category, Product
from lfs.customer.models import Customer
from lfs.manufacturer.models import Manufacturer
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
def mock_request(request_factory, admin_user):
    """Mock request with admin user."""
    request = request_factory.get("/")
    request.user = admin_user
    return request


@pytest.fixture
def mock_request_regular(request_factory, regular_user):
    """Mock request with regular user."""
    request = request_factory.get("/")
    request.user = regular_user
    return request


@pytest.fixture
def root_category(db):
    """Root category for testing."""
    return Category.objects.create(
        name="Root Category", slug="root-category", description="A root category for testing"
    )


@pytest.fixture
def child_category(db, root_category):
    """Child category for testing."""
    return Category.objects.create(
        name="Child Category", slug="child-category", description="A child category for testing", parent=root_category
    )


@pytest.fixture
def grandchild_category(db, child_category):
    """Grandchild category for testing hierarchical structure."""
    return Category.objects.create(
        name="Grandchild Category",
        slug="grandchild-category",
        description="A grandchild category for testing",
        parent=child_category,
    )


@pytest.fixture
def categories_hierarchy(db, root_category, child_category, grandchild_category):
    """Complete category hierarchy for testing."""
    return [root_category, child_category, grandchild_category]


@pytest.fixture
def manufacturer(db):
    """Manufacturer for testing."""
    return Manufacturer.objects.create(name="Test Manufacturer", slug="test-manufacturer")


@pytest.fixture
def product(db, manufacturer):
    """Product for testing."""
    return Product.objects.create(
        name="Test Product", slug="test-product", price=99.99, active=True, manufacturer=manufacturer
    )


@pytest.fixture
def customer(db):
    """Customer for testing."""
    return Customer.objects.create(firstname="Test", lastname="Customer", email="test@example.com")


@pytest.fixture
def mock_messages():
    """Mock Django messages framework."""
    return MagicMock()


@pytest.fixture
def mock_session():
    """Mock session for testing."""
    return {}


@pytest.fixture
def shop(db):
    """Shop instance for testing."""
    return Shop.objects.create(name="Test Shop", shop_owner="Test Owner", from_email="test@example.com")


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db, shop):
    """Enable database access for all tests."""
    pass
