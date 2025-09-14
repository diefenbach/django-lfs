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

from lfs.catalog.models import Category, Product
from lfs.customer.models import Customer
from lfs.manufacturer.models import Manufacturer

User = get_user_model()


# Common fixtures are now imported from the main conftest.py


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


# Common fixtures (mock_session, shop, enable_db_access_for_all_tests)
# are now imported from the main conftest.py
