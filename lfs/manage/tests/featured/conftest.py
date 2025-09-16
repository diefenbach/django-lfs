import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.catalog.models import Product, Category
from lfs.marketing.models import FeaturedProduct
from lfs.core.models import Shop
from lfs.catalog.models import DeliveryTime
from lfs.core.models import Country

User = get_user_model()


@pytest.fixture(scope="session", autouse=True)
def setup_shop_for_featured_tests(django_db_setup, django_db_blocker):
    """Create a default shop for all featured tests that need it."""
    with django_db_blocker.unblock():
        # Create a default shop if none exists
        if not Shop.objects.exists():
            # Create required dependencies
            country = Country.objects.create(code="us", name="USA")
            delivery_time = DeliveryTime.objects.create(min=1, max=2, unit=1)  # DAYS

            Shop.objects.create(
                name="Test Shop",
                shop_owner="Test Owner",
                from_email="test@example.com",
                notification_emails="test@example.com",
                description="Test shop description",
                default_country=country,
                delivery_time=delivery_time,
            )


@pytest.fixture
def featured_request_factory():
    """Request factory for creating mock requests in featured tests."""
    return RequestFactory()


@pytest.fixture
def featured_admin_user(db):
    """Admin user for testing featured functionality."""
    user = User.objects.create_user(
        username="featured_admin",
        email="featured_admin@example.com",
        password="testpass123",
        is_staff=True,
    )
    # Add the manage_shop permission
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    from lfs.core.models import Shop

    content_type = ContentType.objects.get_for_model(Shop)
    permission = Permission.objects.get(content_type=content_type, codename="manage_shop")
    user.user_permissions.add(permission)
    return user


@pytest.fixture
def featured_regular_user(db):
    """Regular user for testing featured permissions."""
    return User.objects.create_user(username="featured_user", email="featured_user@example.com", password="testpass123")


@pytest.fixture
def featured_mock_request(featured_request_factory):
    """Mock request object for testing featured views."""
    request = featured_request_factory.get("/")
    request.session = {}
    # Mock messages framework for unit tests
    from unittest.mock import MagicMock

    messages_mock = MagicMock()
    messages_mock.success = MagicMock()
    messages_mock.error = MagicMock()
    request._messages = messages_mock
    return request


@pytest.fixture
def featured_test_shop(db):
    """Create a test shop for featured product creation."""
    # Create dependencies first
    country = Country.objects.create(code="us", name="USA")
    delivery_time = DeliveryTime.objects.create(min=1, max=2, unit=1)  # DAYS

    return Shop.objects.create(
        name="Featured Test Shop",
        shop_owner="Test Owner",
        from_email="featured_test@example.com",
        notification_emails="featured_test@example.com",
        description="Test shop for featured products",
        default_country=country,
        delivery_time=delivery_time,
    )


@pytest.fixture
def featured_products_sample(db, featured_test_shop):
    """Create sample products for featured testing."""
    from decimal import Decimal

    products = []
    for i in range(10):
        product = Product.objects.create(
            name=f"Featured Product {i+1}",
            slug=f"featured-product-{i+1}",
            sku=f"FP-{i+1:03d}",
            price=Decimal(f"{(i+1)*10}.99"),
            active=True,
        )
        products.append(product)
    return products


@pytest.fixture
def featured_products_featured(db, featured_products_sample):
    """Create FeaturedProduct instances for testing."""
    featured = []
    for i, product in enumerate(featured_products_sample[:5]):  # Feature first 5 products
        fp = FeaturedProduct.objects.create(
            product=product,
            position=(i + 1) * 10,
        )
        featured.append(fp)
    return featured


@pytest.fixture
def featured_many_products(db, featured_test_shop):
    """Create many products for pagination testing in featured."""
    from decimal import Decimal

    products = []
    for i in range(50):  # Enough to trigger pagination
        product = Product.objects.create(
            name=f"Bulk Product {i+1}",
            slug=f"bulk-product-{i+1}",
            sku=f"BULK-{i+1:03d}",
            price=Decimal(f"{(i+1)*5}.99"),
            active=True,
        )
        products.append(product)
    return products


@pytest.fixture
def featured_categories_sample(db):
    """Create sample categories for featured testing."""
    categories = []
    for i, name in enumerate(["Electronics", "Books", "Clothing", "Home", "Sports"]):
        category = Category.objects.create(
            name=name,
            slug=f"category-{name.lower()}",
            position=(i + 1) * 10,
        )
        categories.append(category)
    return categories


@pytest.fixture
def featured_products_with_categories(db, featured_products_sample, featured_categories_sample):
    """Create products assigned to categories for testing category filtering."""
    # Assign products to categories
    for i, product in enumerate(featured_products_sample):
        category_index = i % len(featured_categories_sample)
        product.categories.add(featured_categories_sample[category_index])
    return featured_products_sample


@pytest.fixture
def featured_hierarchical_categories(db):
    """Create hierarchical categories for testing category tree functionality."""
    # Create parent categories
    parent1 = Category.objects.create(
        name="Electronics",
        slug="electronics",
        position=10,
    )
    parent2 = Category.objects.create(
        name="Clothing",
        slug="clothing",
        position=20,
    )

    # Create child categories
    child1 = Category.objects.create(
        name="Smartphones",
        slug="smartphones",
        position=10,
        parent=parent1,
    )
    child2 = Category.objects.create(
        name="Laptops",
        slug="laptops",
        position=20,
        parent=parent1,
    )
    child3 = Category.objects.create(
        name="Men's Clothing",
        slug="mens-clothing",
        position=10,
        parent=parent2,
    )

    # Create grandchild category
    grandchild = Category.objects.create(
        name="Premium Smartphones",
        slug="premium-smartphones",
        position=10,
        parent=child1,
    )

    return [parent1, parent2, child1, child2, child3, grandchild]


@pytest.fixture
def featured_empty_state(db, featured_test_shop):
    """Setup for testing empty featured state."""
    # Ensure no featured products exist
    FeaturedProduct.objects.all().delete()
    return {"message": "Empty featured state ready for testing"}


@pytest.fixture
def featured_single_product(db, featured_test_shop):
    """Single product for testing edge cases."""
    from decimal import Decimal

    return Product.objects.create(
        name="Single Test Product",
        slug="single-test-product",
        sku="SINGLE-001",
        price=Decimal("99.99"),
        active=True,
    )


@pytest.fixture
def featured_single_featured(db, featured_single_product):
    """Single featured product for testing."""
    return FeaturedProduct.objects.create(
        product=featured_single_product,
        position=10,
    )


@pytest.fixture
def featured_inactive_product(db, featured_test_shop):
    """Inactive product for testing filtering."""
    from decimal import Decimal

    return Product.objects.create(
        name="Inactive Product",
        slug="inactive-product",
        sku="INACTIVE-001",
        price=Decimal("49.99"),
        active=False,
    )


@pytest.fixture
def featured_variant_product(db, featured_test_shop):
    """Product with variants for testing variant filtering."""
    from decimal import Decimal
    from lfs.catalog.settings import PRODUCT_WITH_VARIANTS, VARIANT

    # Create parent product
    parent = Product.objects.create(
        name="Variant Parent Product",
        slug="variant-parent-product",
        sku="VARIANT-PARENT-001",
        price=Decimal("29.99"),
        active=True,
        sub_type=PRODUCT_WITH_VARIANTS,
    )

    # Create variant
    variant = Product.objects.create(
        name="Variant Child Product",
        slug="variant-child-product",
        sku="VARIANT-CHILD-001",
        price=Decimal("39.99"),
        active=True,
        sub_type=VARIANT,
        parent=parent,
        active_sku=False,  # Use parent's SKU
        active_name=False,  # Use parent's name
    )

    return parent, variant
