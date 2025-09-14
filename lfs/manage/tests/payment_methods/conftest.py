"""
Pytest configuration for payment method tests.
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import Client
from lfs.core.models import Shop
from lfs.payment.models import PaymentMethod, PaymentMethodPrice
from lfs.tax.models import Tax
from lfs.manage.payment_methods.views import PaymentMethodTabMixin

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


# Common fixtures are now imported from the main conftest.py


@pytest.fixture
def payment_method(db):
    """Create a basic payment method for testing."""
    return PaymentMethod.objects.create(
        name="Test Payment Method", description="Test payment method description", active=True, priority=10
    )


@pytest.fixture
def inactive_payment_method(db):
    """Create an inactive payment method for testing."""
    return PaymentMethod.objects.create(
        name="Inactive Payment Method", description="Inactive payment method", active=False, priority=20
    )


@pytest.fixture
def payment_method_with_prices(db, payment_method):
    """Create a payment method with multiple prices."""
    PaymentMethodPrice.objects.create(payment_method=payment_method, price=Decimal("5.00"), priority=10)
    PaymentMethodPrice.objects.create(payment_method=payment_method, price=Decimal("10.00"), priority=20)
    return payment_method


@pytest.fixture
def multiple_payment_methods(db):
    """Create multiple payment methods for testing."""
    methods = []
    for i in range(3):
        method = PaymentMethod.objects.create(
            name=f"Payment Method {i+1}",
            description=f"Description for method {i+1}",
            active=True,
            priority=(i + 1) * 10,
        )
        methods.append(method)
    return methods


@pytest.fixture
def payment_method_price(db, payment_method):
    """Create a payment method price for testing."""
    return PaymentMethodPrice.objects.create(payment_method=payment_method, price=Decimal("15.00"), priority=10)


@pytest.fixture
def client():
    """Django test client."""
    return Client()


# Common fixtures (request_factory, mock_request) are now imported from the main conftest.py


@pytest.fixture
def tax_rate(db):
    """Create a tax rate for testing."""
    return Tax.objects.create(rate=19.0)


@pytest.fixture
def mock_view():
    """Mock view that uses PaymentMethodTabMixin."""

    class MockBaseView:
        def get_context_data(self, **kwargs):
            return {}

    class MockView(PaymentMethodTabMixin, MockBaseView):
        def __init__(self):
            self.request = None
            self.kwargs = {}
            self.object = None
            self.tab_name = None

        def get_object(self):
            return self.object

    return MockView()
