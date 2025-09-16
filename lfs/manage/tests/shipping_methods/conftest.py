import pytest

from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.shipping.models import ShippingMethod, ShippingMethodPrice
from lfs.catalog.models import DeliveryTime
from lfs.catalog.settings import DELIVERY_TIME_UNIT_DAYS
from lfs.tax.models import Tax
from lfs.core.models import Shop
from lfs.customer.models import Customer

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
def delivery_time(db):
    """DeliveryTime instance for testing."""
    return DeliveryTime.objects.create(min=1, max=3, unit=DELIVERY_TIME_UNIT_DAYS, description="1-3 days")


@pytest.fixture
def tax(db):
    """Tax instance for testing."""
    return Tax.objects.create(rate=19.0, description="Standard Tax")


@pytest.fixture
def shipping_method(db, delivery_time, tax):
    """ShippingMethod instance for testing."""
    return ShippingMethod.objects.create(
        name="Standard Shipping",
        description="Standard shipping method",
        note="Delivered within 1-3 business days",
        active=True,
        priority=10,
        price=5.99,
        delivery_time=delivery_time,
        tax=tax,
        price_calculator="lfs.shipping.GrossShippingMethodPriceCalculator",
    )


@pytest.fixture
def inactive_shipping_method(db, delivery_time):
    """Inactive ShippingMethod instance for testing."""
    return ShippingMethod.objects.create(
        name="Inactive Shipping",
        description="Inactive shipping method",
        active=False,
        priority=20,
        price=2.99,
        delivery_time=delivery_time,
    )


@pytest.fixture
def multiple_shipping_methods(db, delivery_time, tax):
    """Multiple ShippingMethod instances for testing."""
    methods = []
    for i in range(3):
        method = ShippingMethod.objects.create(
            name=f"Shipping Method {i+1}",
            description=f"Description for method {i+1}",
            active=True,
            priority=(i + 1) * 10,
            price=float(5.99 + i),
            delivery_time=delivery_time,
            tax=tax if i % 2 == 0 else None,
        )
        methods.append(method)
    return methods


@pytest.fixture
def shipping_method_price(db, shipping_method):
    """ShippingMethodPrice instance for testing."""
    return ShippingMethodPrice.objects.create(shipping_method=shipping_method, price=7.99, priority=10, active=True)


@pytest.fixture
def multiple_shipping_prices(db, shipping_method):
    """Multiple ShippingMethodPrice instances for testing."""
    prices = []
    for i in range(3):
        price = ShippingMethodPrice.objects.create(
            shipping_method=shipping_method, price=float(10.99 + i), priority=(i + 1) * 10, active=True
        )
        prices.append(price)
    return prices


@pytest.fixture
def customer_with_shipping_method(db, shipping_method):
    """Customer with selected shipping method."""
    return Customer.objects.create(selected_shipping_method=shipping_method, session_id="test_session_123")


@pytest.fixture
def mock_session():
    """Mock session for testing."""
    return {}


@pytest.fixture
def mock_request(admin_user, request_factory):
    """Mock request with admin user."""
    request = request_factory.get("/")
    request.user = admin_user
    request.session = {}
    return request


@pytest.fixture
def mock_htmx_request(admin_user, request_factory):
    """Mock HTMX request with admin user."""
    request = request_factory.post("/", data={})
    request.user = admin_user
    request.session = {}
    request.META["HTTP_HX_REQUEST"] = "true"
    return request


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db, shop):
    """Enable database access for all tests."""
    pass
