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
def manufacturer(db):
    """Primary manufacturer for testing."""
    return Manufacturer.objects.create(
        name="Test Manufacturer", slug="test-manufacturer", description="A test manufacturer"
    )


@pytest.fixture
def second_manufacturer(db):
    """Second manufacturer for testing multiple manufacturers."""
    return Manufacturer.objects.create(
        name="Second Manufacturer", slug="second-manufacturer", description="A second test manufacturer"
    )


@pytest.fixture
def manufacturers_list(db, manufacturer, second_manufacturer):
    """List of manufacturers for testing."""
    return [manufacturer, second_manufacturer]


@pytest.fixture
def category(db):
    """Category for testing."""
    return Category.objects.create(name="Test Category", slug="test-category", description="A test category")


@pytest.fixture
def product(db, manufacturer):
    """Product with manufacturer for testing."""
    return Product.objects.create(
        name="Test Product", slug="test-product", price=99.99, active=True, manufacturer=manufacturer
    )


@pytest.fixture
def product_without_manufacturer(db):
    """Product without manufacturer for testing assignment."""
    return Product.objects.create(name="Unassigned Product", slug="unassigned-product", price=49.99, active=True)


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
