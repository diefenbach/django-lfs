"""
Pytest configuration for topseller tests.
"""

import pytest
from lfs.core.models import Shop
from lfs.catalog.models import Product, Category
from lfs.marketing.models import Topseller
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
def regular_user(db):
    """Regular user without admin permissions."""
    return User.objects.create_user(username="user", email="user@example.com", password="testpass123")


@pytest.fixture
def sample_products(db, test_shop):
    """Create sample products for testing."""
    products = []

    # Create main products
    for i in range(5):
        product = Product.objects.create(
            name=f"Test Product {i+1}",
            sku=f"SKU-{i+1:03d}",
            slug=f"test-product-{i+1}",
            price=10.00 + i,
            active=True,
        )
        products.append(product)

    return products


@pytest.fixture
def sample_categories(db):
    """Create sample categories for testing."""
    categories = []

    # Create parent category
    parent = Category.objects.create(
        name="Parent Category",
        slug="parent-category",
    )
    categories.append(parent)

    # Create child categories
    for i in range(3):
        child = Category.objects.create(
            name=f"Child Category {i+1}",
            slug=f"child-category-{i+1}",
            parent=parent,
        )
        categories.append(child)

    return categories


@pytest.fixture
def sample_topsellers(db, sample_products):
    """Create sample topseller products for testing."""
    topsellers = []

    for i, product in enumerate(sample_products[:3]):
        topseller = Topseller.objects.create(
            product=product,
            position=(i + 1) * 10,
        )
        topsellers.append(topseller)

    return topsellers


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    from django.test import RequestFactory

    return RequestFactory()


@pytest.fixture
def mock_request(request_factory):
    """Mock request object for testing."""
    request = request_factory.get("/")

    # Mock session that behaves like a dictionary
    class MockSession(dict):
        def __init__(self):
            super().__init__()
            self.session_key = "test_session_key"

        def get(self, key, default=None):
            return super().get(key, default)

        def __setitem__(self, key, value):
            super().__setitem__(key, value)

        def __getitem__(self, key):
            return super().__getitem__(key)

        def __contains__(self, key):
            return super().__contains__(key)

    request.session = MockSession()
    # Set default session values
    request.session["topseller-amount"] = 25
    # Add session_key attribute for cart utils
    request.session.session_key = "test_session_key"
    # Mock messages framework for unit tests
    messages_mock = type(
        "MockMessages",
        (),
        {
            "success": lambda msg: None,
            "error": lambda msg: None,
            "add": lambda self, level, message, extra_tags="": None,
        },
    )()
    request._messages = messages_mock
    return request
