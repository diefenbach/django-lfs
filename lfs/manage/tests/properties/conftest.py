import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory, Client

from lfs.core.models import Shop
from lfs.catalog.models import Property, PropertyOption
from lfs.catalog.settings import (
    PROPERTY_TEXT_FIELD,
    PROPERTY_NUMBER_FIELD,
    PROPERTY_SELECT_FIELD,
)

User = get_user_model()


# Shop fixtures
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


# User fixtures
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
def user_with_customer(db):
    """User with associated customer."""
    from lfs.customer.models import Customer

    user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
    customer = Customer.objects.create(user=user, session="test_session")
    return user, customer


# Request fixtures
@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def mock_request(request_factory):
    """Mock request object for testing."""
    request = request_factory.get("/")
    request.session = {}
    return request


@pytest.fixture
def mock_request_with_user(request_factory, admin_user):
    """Mock request object with authenticated admin user."""
    request = request_factory.get("/")
    request.user = admin_user
    request.session = {}
    return request


@pytest.fixture
def mock_request_with_messages(request_factory):
    """Mock request object with messages framework support."""
    request = request_factory.get("/")
    request.session = {}
    # Minimal messages mock
    messages_mock = type(
        "MockMessages",
        (),
        {
            "success": staticmethod(lambda *a, **k: None),
            "error": staticmethod(lambda *a, **k: None),
            "add": staticmethod(lambda *a, **k: None),
        },
    )
    request._messages = messages_mock
    return request


# Client fixture
@pytest.fixture
def client():
    """Django test client."""
    return Client()


# Property fixtures
@pytest.fixture
def sample_properties(db):
    """Create sample properties for testing."""
    properties = []
    properties.append(Property.objects.create(name="Color", title="Color"))
    properties.append(Property.objects.create(name="Size", title="Size"))
    properties.append(Property.objects.create(name="Material", title="Material"))
    properties.append(Property.objects.create(name="Weight", title="Weight"))
    properties.append(Property.objects.create(name="Length", title="Length"))
    return properties


@pytest.fixture
def comprehensive_property_data(db):
    """Comprehensive property data for workflow testing."""
    properties = []

    # Create diverse properties for testing
    test_data = [
        {"name": "Color", "title": "Color", "type": PROPERTY_TEXT_FIELD},
        {"name": "Size", "title": "Size", "type": PROPERTY_SELECT_FIELD},
        {"name": "Weight", "title": "Weight", "type": PROPERTY_NUMBER_FIELD},
        {"name": "Material", "title": "Material", "type": PROPERTY_TEXT_FIELD},
        {"name": "Price", "title": "Price", "type": PROPERTY_NUMBER_FIELD},
        {"name": "Brand", "title": "Brand", "type": PROPERTY_TEXT_FIELD},
        {"name": "Category", "title": "Category", "type": PROPERTY_SELECT_FIELD},
        {"name": "SKU", "title": "SKU", "type": PROPERTY_TEXT_FIELD},
    ]

    for data in test_data:
        prop = Property.objects.create(**data)
        properties.append(prop)

        # Add options for select-type properties
        if data["type"] == PROPERTY_SELECT_FIELD:
            if data["name"] == "Size":
                PropertyOption.objects.create(name="Small", property=prop, price=0)
                PropertyOption.objects.create(name="Medium", property=prop, price=5.00)
                PropertyOption.objects.create(name="Large", property=prop, price=10.00)
            elif data["name"] == "Category":
                PropertyOption.objects.create(name="Electronics", property=prop, price=0)
                PropertyOption.objects.create(name="Clothing", property=prop, price=0)
                PropertyOption.objects.create(name="Books", property=prop, price=0)

    return properties


@pytest.fixture
def edge_case_properties(db):
    """Properties with edge case data for testing."""
    properties = []

    # Property with very long name
    properties.append(Property.objects.create(name="a" * 255, title="Very Long Property Name"))  # Maximum name length

    # Property with special characters in name
    properties.append(
        Property.objects.create(name="Property-with-special-chars!@#$%^&*()", title="Special Characters Property")
    )

    # Property with unicode characters
    properties.append(Property.objects.create(name="Property-with-unicode-李小明", title="Unicode Property"))

    # Property with numeric name
    properties.append(Property.objects.create(name="123456789", title="Numeric Property"))

    # Property with empty title
    properties.append(Property.objects.create(name="Empty Title Property", title=""))

    # Property with very long title
    properties.append(Property.objects.create(name="Long Title Property", title="a" * 255))

    return properties
