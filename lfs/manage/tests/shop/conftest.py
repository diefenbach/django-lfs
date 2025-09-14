"""
Pytest fixtures for Shop testing.

Provides comprehensive test data and utilities for shop management tests.
"""

import pytest
from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from lfs.core.models import Shop, Country

User = get_user_model()


# Common fixtures are now imported from the main conftest.py


@pytest.fixture
def countries(db):
    """Create some test countries."""
    country1 = Country.objects.create(code="DE", name="Germany")
    country2 = Country.objects.create(code="US", name="United States")
    country3 = Country.objects.create(code="FR", name="France")
    return [country1, country2, country3]


@pytest.fixture
def shop(db):
    """Default Shop instance for testing."""
    return Shop.objects.create(
        name="Test Shop",
        shop_owner="Test Owner",
        from_email="test@example.com",
        notification_emails="notify@example.com",
        description="Test shop description",
        checkout_type=1,
        confirm_toc=True,
        google_analytics_id="GA-123456789",
        ga_site_tracking=True,
        ga_ecommerce_tracking=True,
        price_calculator="lfs.gross_price.calculator.GrossPriceCalculator",
    )


@pytest.fixture
def shop_with_image(db):
    """Shop instance with image for testing."""
    shop = Shop.objects.create(
        name="Shop with Image",
        shop_owner="Image Owner",
        from_email="image@example.com",
    )

    # Create a mock image file
    image_file = SimpleUploadedFile("test_image.jpg", b"fake image content", content_type="image/jpeg")
    shop.image = image_file
    shop.save()
    return shop


@pytest.fixture
def minimal_shop(db):
    """Minimal Shop instance with only required fields."""
    return Shop.objects.create(
        name="Minimal Shop",
        shop_owner="Minimal Owner",
        from_email="minimal@example.com",
    )


# Common fixtures (mock_request) are now imported from the main conftest.py


@pytest.fixture
def mock_post_request(admin_user, request_factory):
    """Mock POST request with admin user."""
    request = request_factory.post("/", data={})
    request.user = admin_user
    request.session = {}
    return request


@pytest.fixture
def mock_order_number_generator():
    """Mock order number generator for testing."""
    mock_ong = Mock()
    mock_order_number = Mock()
    mock_order_number.id = "order_number"
    mock_order_number.get_form.return_value = Mock()
    mock_ong.objects.get.return_value = mock_order_number
    mock_ong.objects.create.return_value = mock_order_number
    return mock_ong


@pytest.fixture
def mock_portlets_inline_view():
    """Mock portlets inline view for testing."""
    mock_view = Mock()
    mock_view.get.return_value = {"portlets": []}
    return mock_view


@pytest.fixture
def mock_shop_changed_signal():
    """Mock shop_changed signal for testing."""
    return Mock()


# Common fixtures (enable_db_access_for_all_tests) are now imported from the main conftest.py
