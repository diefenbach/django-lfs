import pytest
from lfs.catalog.models import PropertyGroup, Property, Product, GroupsPropertiesRelation
from lfs.core.models import Shop


@pytest.fixture
def shop(db):
    """Create a shop for testing."""
    return Shop.objects.create(
        name="Test Shop",
        shop_owner="Test Owner",
        from_email="test@example.com",
        notification_emails="test@example.com",
    )


@pytest.fixture
def sample_property_group():
    """Create a sample property group for testing."""
    return PropertyGroup.objects.create(name="Test Property Group", position=10)


@pytest.fixture
def sample_property():
    """Create a sample property for testing."""
    return Property.objects.create(
        name="Test Property", title="Test Property Title", type=1, required=False  # Text field
    )


@pytest.fixture
def sample_product(shop):
    """Create a sample product for testing."""
    return Product.objects.create(name="Test Product", slug="test-product", sku="TEST-001", price=29.99, active=True)


@pytest.fixture
def comprehensive_property_group_data(shop):
    """Create comprehensive test data for property groups."""
    # Create property group
    property_group = PropertyGroup.objects.create(name="Electronics", position=10)

    # Create properties
    properties = []
    for i in range(3):
        prop = Property.objects.create(
            name=f"property{i+1}", title=f"Property {i+1}", type=1, required=False  # Text field
        )
        properties.append(prop)

        # Create relation
        GroupsPropertiesRelation.objects.create(group=property_group, property=prop, position=(i + 1) * 10)

    # Create products
    products = []
    for i in range(2):
        product = Product.objects.create(
            name=f"product{i+1}", slug=f"product-{i+1}", sku=f"PROD-{i+1:03d}", price=19.99 + (i * 10), active=True
        )
        products.append(product)
        property_group.products.add(product)

    return [{"property_group": property_group, "properties": properties, "products": products}]
