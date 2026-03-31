import pytest
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.discounts.models import Discount
from lfs.discounts.settings import DISCOUNT_TYPE_ABSOLUTE, DISCOUNT_TYPE_PERCENTAGE
from lfs.catalog.models import Product, Category
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
def shop(db):
    """Shop instance for testing."""
    return Shop.objects.create(name="Test Shop", shop_owner="Test Owner", from_email="test@example.com")


@pytest.fixture
def discount(db):
    """Discount instance for testing."""
    return Discount.objects.create(
        name="Test Discount",
        value=Decimal("10.00"),
        type=DISCOUNT_TYPE_ABSOLUTE,
        active=True,
    )


@pytest.fixture
def inactive_discount(db):
    """Inactive Discount instance for testing."""
    return Discount.objects.create(
        name="Inactive Discount",
        value=Decimal("5.00"),
        type=DISCOUNT_TYPE_PERCENTAGE,
        active=False,
    )


@pytest.fixture
def multiple_discounts(db):
    """Multiple Discount instances for testing."""
    discounts = []
    for i in range(3):
        discount = Discount.objects.create(
            name=f"Discount {i+1}",
            value=Decimal(f"{(i+1)*5}.00"),
            type=DISCOUNT_TYPE_ABSOLUTE,
            active=True,
        )
        discounts.append(discount)
    return discounts


@pytest.fixture
def percentage_discount(db):
    """Percentage-based discount for testing."""
    return Discount.objects.create(
        name="Percentage Discount",
        value=Decimal("15.00"),
        type=DISCOUNT_TYPE_PERCENTAGE,
        active=True,
    )


@pytest.fixture
def product(db, shop):
    """Product instance for testing."""
    return Product.objects.create(
        name="Test Product",
        slug="test-product",
        sku="TEST-001",
        price=Decimal("29.99"),
        active=True,
    )


@pytest.fixture
def multiple_products(db, shop):
    """Multiple Product instances for testing."""
    products = []
    for i in range(5):
        product = Product.objects.create(
            name=f"Product {i+1}",
            slug=f"product-{i+1}",
            sku=f"SKU-{i+1:03d}",
            price=Decimal(f"{(i+1)*10}.99"),
            active=True,
        )
        products.append(product)
    return products


@pytest.fixture
def category(db):
    """Category instance for testing."""
    return Category.objects.create(
        name="Test Category",
        slug="test-category",
        position=10,
    )


@pytest.fixture
def manufacturer(db):
    """Manufacturer instance for testing."""
    return Manufacturer.objects.create(
        name="Test Manufacturer",
        slug="test-manufacturer",
        position=10,
    )


@pytest.fixture
def discount_with_products(discount, multiple_products):
    """Discount with assigned products."""
    discount.products.add(multiple_products[0], multiple_products[1])
    return discount


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


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db, shop):
    """Enable database access for all tests."""
    pass
