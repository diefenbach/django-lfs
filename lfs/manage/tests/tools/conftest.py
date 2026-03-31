import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.catalog.models import Product, Category
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
def shop(db):
    """Shop instance for testing."""
    return Shop.objects.create(name="Test Shop", shop_owner="Test Owner", from_email="test@example.com")


@pytest.fixture
def mock_request(admin_user, request_factory):
    """Mock request with admin user."""
    request = request_factory.get("/")
    request.user = admin_user
    request.session = {}
    return request


@pytest.fixture
def mock_request_regular_user(regular_user, request_factory):
    """Mock request with regular user."""
    request = request_factory.get("/")
    request.user = regular_user
    request.session = {}
    return request


@pytest.fixture
def sample_products(db):
    """Sample products for testing."""
    products = []
    for i in range(3):
        product = Product.objects.create(name=f"Product {i+1}", slug=f"product-{i+1}", price=10.00 + i, active=True)
        products.append(product)
    return products


@pytest.fixture
def sample_categories(db):
    """Sample categories for testing."""
    categories = []
    for i in range(3):
        category = Category.objects.create(name=f"Category {i+1}", slug=f"category-{i+1}", active=True)
        categories.append(category)
    return categories


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db, shop):
    """Enable database access for all tests."""
    pass
