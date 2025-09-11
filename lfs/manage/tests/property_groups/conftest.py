"""
Pytest configuration for property_groups tests.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.core.models import Shop

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
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def mock_request(request_factory):
    """Mock request object for testing."""
    request = request_factory.get("/")
    # Create a proper session object
    from django.contrib.sessions.backends.db import SessionStore

    request.session = SessionStore()
    request.session.create()
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


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    return User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="testpass123",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def regular_user(db):
    """Create a regular user for testing."""
    return User.objects.create_user(
        username="user",
        email="user@example.com",
        password="testpass123",
        is_staff=False,
        is_superuser=False,
    )
