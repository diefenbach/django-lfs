"""
Shared fixtures for Product management tests.

Following TDD principles:
- Use pytest fixtures for test initialization
- Prefer real objects over mocks when possible
- Keep fixtures minimal and focused
"""

import pytest
from django.contrib.auth import get_user_model

from lfs.catalog.models import (
    Product,
    Category,
    Property,
    PropertyGroup,
    PropertyOption,
)
from lfs.catalog.settings import VARIANT as PRODUCT_VARIANT

User = get_user_model()


# Common fixtures are now imported from the main conftest.py


@pytest.fixture
def category(db):
    """Create a basic category."""
    return Category.objects.create(name="Test Category", slug="test-category", description="Test category description")


@pytest.fixture
def product(db, shop):
    """Create a basic product."""
    return Product.objects.create(name="Test Product", slug="test-product", sku="TEST001", price=29.99, active=True)


@pytest.fixture
def inactive_product(db, shop):
    """Create an inactive product."""
    return Product.objects.create(
        name="Inactive Product", slug="inactive-product", sku="TEST002", price=19.99, active=False
    )


@pytest.fixture
def variant_product(db, product, shop):
    """Create a product variant."""
    return Product.objects.create(
        name="Test Variant",
        slug="test-variant",
        sku="TEST001-V1",
        price=39.99,
        active=True,
        sub_type=PRODUCT_VARIANT,
        parent=product,
    )


@pytest.fixture
def multiple_products(db, shop):
    """Create multiple products for testing."""
    products = []
    for i in range(3):
        product = Product.objects.create(
            name=f"Product {i+1}", slug=f"product-{i+1}", sku=f"TEST{i+1:03d}", price=10.00 * (i + 1), active=True
        )
        products.append(product)
    return products


@pytest.fixture
def property_group(db):
    """Create a property group."""
    return PropertyGroup.objects.create(name="Test Property Group")


@pytest.fixture
def product_property(db, property_group):
    """Create a product property."""
    # Use PROPERTY_TEXT_FIELD constant instead of string
    from lfs.catalog.settings import PROPERTY_TEXT_FIELD

    property_obj = Property.objects.create(name="Test Property", type=PROPERTY_TEXT_FIELD)
    property_obj.groups.add(property_group)
    return property_obj


@pytest.fixture
def property_option(db, product_property):
    """Create a property option."""
    return PropertyOption.objects.create(
        property=product_property, name="Test Option", position=1  # Use property ForeignKey
    )


@pytest.fixture
def product_with_properties(db, product, property_group):
    """Create a product with property groups assigned."""
    product.property_groups.add(property_group)
    return product


@pytest.fixture
def shop(db):
    """Create a default shop."""
    from lfs.core.models import Shop, Country
    from django.contrib.auth import get_user_model

    # Create a default country first if it doesn't exist
    country, created = Country.objects.get_or_create(code="US", defaults={"name": "United States"})

    # Create a test user for shop owner if needed
    User = get_user_model()
    shop_owner, created = User.objects.get_or_create(
        username="shop_owner", defaults={"email": "owner@example.com", "first_name": "Shop", "last_name": "Owner"}
    )

    return Shop.objects.create(
        name="Test Shop",
        shop_owner="Test Shop Owner",
        from_email="test@example.com",
        notification_emails="test@example.com",
        default_country=country,
        price_calculator="lfs.gross_price.calculator.GrossPriceCalculator",
    )


@pytest.fixture
def products_with_categories(db, category, shop):
    """Create products with category assignments."""
    products = []
    for i in range(3):
        product = Product.objects.create(
            name=f"Categorized Product {i+1}",
            slug=f"categorized-product-{i+1}",
            sku=f"CAT{i+1:03d}",
            price=15.00 * (i + 1),
            active=True,
        )
        product.categories.add(category)
        products.append(product)
    return products
