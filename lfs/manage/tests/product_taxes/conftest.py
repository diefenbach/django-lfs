"""
Test fixtures for product_taxes module tests.

Following pytest best practices:
- Fixtures over setup/teardown
- Clear fixture names describing what they provide
- Minimal mocking - prefer real objects
- Fast, isolated fixtures
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.tax.models import Tax
from lfs.core.models import Shop

User = get_user_model()


@pytest.fixture
def admin_user():
    """Create an admin user with manage_shop permission."""
    user = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="testpass123",
        is_staff=True,
        is_superuser=True,
    )
    return user


@pytest.fixture
def shop():
    """Create a default shop for tests."""
    shop, created = Shop.objects.get_or_create(
        name="Test Shop",
        defaults={
            "description": "Test shop description",
            "image": None,
        },
    )
    return shop


@pytest.fixture
def tax():
    """Create a single tax for testing."""
    return Tax.objects.create(rate=19.0, description="VAT 19%")


@pytest.fixture
def multiple_taxes():
    """Create multiple taxes for testing."""
    taxes = []

    # Create first tax
    tax1 = Tax.objects.create(rate=19.0, description="VAT 19%")
    taxes.append(tax1)

    # Create second tax
    tax2 = Tax.objects.create(rate=7.0, description="VAT 7%")
    taxes.append(tax2)

    # Create third tax
    tax3 = Tax.objects.create(rate=0.0, description="No Tax")
    taxes.append(tax3)

    return taxes


class MockSession(dict):
    """Mock session with session_key attribute and proper dict-like behavior."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_key = "test_session_key"

    def get(self, key, default=None):
        """Override get to handle session_key specially."""
        if key == "session_key":
            return self.session_key
        return super().get(key, default)


@pytest.fixture
def mock_session():
    """Create a mock session object."""
    return MockSession()


@pytest.fixture
def mock_request(admin_user, mock_session):
    """Create a mock request with user and session."""
    factory = RequestFactory()
    request = factory.get("/")
    request.user = admin_user
    request.session = mock_session
    return request


@pytest.fixture
def htmx_request(admin_user, mock_session):
    """Create a mock HTMX request."""
    factory = RequestFactory()
    request = factory.get("/")
    request.user = admin_user
    request.session = mock_session
    request.META["HTTP_HX_REQUEST"] = "true"
    return request
