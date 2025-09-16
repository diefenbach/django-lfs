import os
import django
from django.conf import settings

# Configure Django settings before importing other Django modules
if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings.testing")
    django.setup()

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.catalog.models import StaticBlock, Product, Category
from lfs.core.models import Action, ActionGroup, Country
from lfs.catalog.models import File, DeliveryTime
from lfs.catalog.settings import DELIVERY_TIME_UNIT_DAYS
from lfs.voucher.models import VoucherGroup, VoucherOptions, Voucher
from lfs.tax.models import Tax
from lfs.core.models import Shop
from lfs.cart.models import Cart
from lfs.order.models import Order
from lfs.customer.models import Customer
from lfs.shipping.models import ShippingMethod
from lfs.payment.models import PaymentMethod
from lfs.addresses.models import Address
from lfs.page.models import Page
from lfs.marketing.models import FeaturedProduct, Topseller
from lfs.manufacturer.models import Manufacturer

# Portlet imports
from portlets.models import Slot, PortletAssignment, PortletRegistration, PortletBlocking
from portlets.example.models import TextPortlet


User = get_user_model()


@pytest.fixture
def request_factory():
    """Django RequestFactory for creating test requests."""
    return RequestFactory()


@pytest.fixture
def manage_user(db):
    """User with manage_shop permission."""
    user = User.objects.create_user(username="testmanager", email="manager@test.com", password="testpass123")

    # Create superuser to bypass permission check for testing
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def regular_user(db):
    """Regular user without manage permissions."""
    return User.objects.create_user(username="testuser", email="user@test.com", password="testpass123")


@pytest.fixture
def static_block(db):
    """Sample StaticBlock for testing."""
    return StaticBlock.objects.create(name="Test Block", html="<p>Test content</p>", position=10)


@pytest.fixture
def multiple_static_blocks(db):
    """Multiple StaticBlocks for list testing."""
    blocks = []
    for i in range(3):
        block = StaticBlock.objects.create(
            name=f"Test Block {i+1}", html=f"<p>Test content {i+1}</p>", position=(i + 1) * 10
        )
        blocks.append(block)
    return blocks


@pytest.fixture
def authenticated_request(request_factory, manage_user):
    """Factory for creating authenticated requests."""

    def _make_request(method="GET", path="/", data=None, **kwargs):
        if method.upper() == "GET":
            request = request_factory.get(path, data or {}, **kwargs)
        elif method.upper() == "POST":
            request = request_factory.post(path, data or {}, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")

        request.user = manage_user

        # Add messages framework support for testing
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.contrib.sessions.backends.db import SessionStore
        from django.contrib.sessions.models import Session

        # Create a session store
        session = SessionStore()
        session.create()
        request.session = session

        # Add messages storage
        messages = FallbackStorage(request)
        request._messages = messages

        return request

    return _make_request


@pytest.fixture
def action_group(db):
    """Sample ActionGroup for testing."""
    return ActionGroup.objects.create(name="Test Group")


@pytest.fixture
def action(db, action_group):
    """Sample Action for testing."""
    return Action.objects.create(
        title="Test Action", link="https://example.com", active=True, group=action_group, position=10
    )


@pytest.fixture
def multiple_actions(db, action_group):
    """Multiple Actions for list testing."""
    actions = []
    for i in range(3):
        action = Action.objects.create(
            title=f"Test Action {i+1}",
            link=f"https://example{i+1}.com",
            active=True,
            group=action_group,
            position=(i + 1) * 10,
        )
        actions.append(action)
    return actions


@pytest.fixture
def multiple_action_groups(db):
    """Multiple ActionGroups for testing."""
    groups = []
    for i in range(3):
        group = ActionGroup.objects.create(name=f"Test Group {i+1}")
        groups.append(group)
    return groups


@pytest.fixture
def action_with_mixed_groups(db, multiple_action_groups):
    """Actions distributed across multiple groups."""
    actions = []
    for i, group in enumerate(multiple_action_groups):
        for j in range(2):  # 2 actions per group
            action = Action.objects.create(
                title=f"Action {i+1}-{j+1}",
                link=f"https://example{i+1}-{j+1}.com",
                active=True,
                group=group,
                position=(j + 1) * 10,
            )
            actions.append(action)
    return actions


@pytest.fixture
def files_for_static_block(db, static_block):
    """Multiple Files attached to a StaticBlock for testing."""
    files = []
    for i in range(3):
        file_obj = File.objects.create(
            content=static_block,
            title=f"Test File {i+1}",
            position=(i + 1) * 10,
        )
        files.append(file_obj)
    return files


@pytest.fixture
def single_file(db, static_block):
    """Single File for testing."""
    return File.objects.create(
        content=static_block,
        title="Test File",
        position=10,
    )


# Voucher-related fixtures


@pytest.fixture
def voucher_group(db, manage_user):
    """Sample VoucherGroup for testing."""
    return VoucherGroup.objects.create(name="Test Voucher Group", creator=manage_user, position=10)


@pytest.fixture
def multiple_voucher_groups(db, manage_user):
    """Multiple VoucherGroups for list testing."""
    groups = []
    for i in range(3):
        group = VoucherGroup.objects.create(name=f"Group {i+1}", creator=manage_user, position=(i + 1) * 10)
        groups.append(group)
    return groups


@pytest.fixture
def voucher_options(db):
    """Sample VoucherOptions for testing."""
    return VoucherOptions.objects.create(
        number_prefix="TEST-", number_suffix="-2024", number_length=8, number_letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )


@pytest.fixture
def voucher(db, voucher_group, manage_user):
    """Sample Voucher for testing."""
    from decimal import Decimal

    return Voucher.objects.create(
        number="TEST123",
        group=voucher_group,
        creator=manage_user,
        kind_of=0,  # Absolute
        value=Decimal("25.00"),
        active=True,
    )


@pytest.fixture
def multiple_vouchers(db, voucher_group, manage_user):
    """Multiple Vouchers for testing."""
    from decimal import Decimal

    vouchers = []
    for i in range(3):
        voucher = Voucher.objects.create(
            number=f"VOUCHER{i+1:03d}",
            group=voucher_group,
            creator=manage_user,
            kind_of=i % 2,  # Mix of absolute (0) and percentage (1)
            value=Decimal(f"{(i+1)*10}.00"),
            active=True,
        )
        vouchers.append(voucher)
    return vouchers


@pytest.fixture
def used_and_unused_vouchers(db, voucher_group, manage_user):
    """Mix of used and unused vouchers for testing filters."""
    from decimal import Decimal

    vouchers = []

    # Create used voucher
    used_voucher = Voucher.objects.create(
        number="USED001",
        group=voucher_group,
        creator=manage_user,
        kind_of=0,
        value=Decimal("50.00"),
        used_amount=Decimal("50.00"),
        active=True,
    )
    vouchers.append(used_voucher)

    # Create unused voucher
    unused_voucher = Voucher.objects.create(
        number="UNUSED001", group=voucher_group, creator=manage_user, kind_of=0, value=Decimal("25.00"), active=True
    )
    vouchers.append(unused_voucher)

    return vouchers


@pytest.fixture
def tax(db):
    """Sample Tax for testing."""
    from decimal import Decimal

    return Tax.objects.create(rate=Decimal("19.00"))


@pytest.fixture
def default_country(db):
    """Create a default country for testing."""
    return Country.objects.create(code="us", name="USA")


@pytest.fixture
def delivery_time(db):
    """Create a default delivery time for testing."""
    return DeliveryTime.objects.create(min=1, max=2, unit=DELIVERY_TIME_UNIT_DAYS)


@pytest.fixture
def shop(db, default_country, delivery_time):
    """Sample Shop for testing with all required dependencies."""
    shop = Shop.objects.create(
        name="Test Shop",
        shop_owner="Test Owner",
        from_email="test@example.com",
        notification_emails="test@example.com",
        description="Test shop description",
        default_country=default_country,
        delivery_time=delivery_time,
    )
    shop.invoice_countries.add(default_country)
    shop.shipping_countries.add(default_country)
    return shop


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    return User.objects.create_user(username="admin", password="testpass123", is_staff=True, is_superuser=True)


@pytest.fixture
def authenticated_client(client, admin_user, shop):
    """Create an authenticated client."""
    client.login(username="admin", password="testpass123")
    return client


@pytest.fixture
def test_carts(db, shop):
    """Create test carts."""
    cart1 = Cart.objects.create(session="test_session_1")
    cart2 = Cart.objects.create(session="test_session_2")
    return cart1, cart2


# Order-related fixtures


@pytest.fixture
def customer(db):
    """Sample Customer for testing."""
    return Customer.objects.create(
        session="test_session_123",
    )


@pytest.fixture
def address(db, customer, default_country):
    """Sample Address for testing."""
    return Address.objects.create(
        customer=customer,
        firstname="John",
        lastname="Doe",
        line1="123 Main St",
        city="Test City",
        zip_code="12345",
        country=default_country,
        email="john.doe@example.com",
    )


@pytest.fixture
def shipping_method(db):
    """Sample ShippingMethod for testing."""
    return ShippingMethod.objects.create(
        name="Standard Shipping",
        active=True,
        price=5.99,
    )


@pytest.fixture
def payment_method(db):
    """Sample PaymentMethod for testing."""
    return PaymentMethod.objects.create(
        name="Credit Card",
        active=True,
        price=0.00,
    )


@pytest.fixture
def order(db, customer, address, shipping_method, payment_method, shop):
    """Sample Order for testing."""
    from decimal import Decimal
    from django.utils import timezone
    from django.contrib.contenttypes.models import ContentType

    # Get the content type for Address
    address_content_type = ContentType.objects.get_for_model(address.__class__)

    return Order.objects.create(
        number="ORD-001",
        session=customer.session,
        customer_firstname="John",
        customer_lastname="Doe",
        customer_email="john.doe@example.com",
        shipping_method=shipping_method,
        payment_method=payment_method,
        price=Decimal("99.99"),
        tax=Decimal("19.00"),
        shipping_price=Decimal("5.99"),
        payment_price=Decimal("0.00"),
        state=1,  # Pending
        created=timezone.now(),
        # Set the address relationships
        sa_content_type=address_content_type,
        sa_object_id=address.id,
        ia_content_type=address_content_type,
        ia_object_id=address.id,
    )


@pytest.fixture
def multiple_orders(db, customer, address, shipping_method, payment_method, shop):
    """Multiple Orders for testing."""
    from decimal import Decimal
    from django.utils import timezone
    from django.contrib.contenttypes.models import ContentType
    import lfs.order.settings

    orders = []
    states = [state[0] for state in lfs.order.settings.ORDER_STATES]

    # Get the content type for Address
    address_content_type = ContentType.objects.get_for_model(address.__class__)

    for i in range(5):
        order = Order.objects.create(
            number=f"ORD-{i+1:03d}",
            session=customer.session,
            customer_firstname=f"Customer{i+1}",
            customer_lastname="Test",
            customer_email=f"customer{i+1}@example.com",
            shipping_method=shipping_method,
            payment_method=payment_method,
            price=Decimal(f"{(i+1)*50}.00"),
            tax=Decimal(f"{(i+1)*10}.00"),
            shipping_price=Decimal("5.99"),
            payment_price=Decimal("0.00"),
            state=states[i % len(states)],
            created=timezone.now(),
            # Set the address relationships
            sa_content_type=address_content_type,
            sa_object_id=address.id,
            ia_content_type=address_content_type,
            ia_object_id=address.id,
        )
        orders.append(order)

    return orders


@pytest.fixture
def order_with_items(db, order):
    """Order with order items for testing."""
    from lfs.catalog.models import Product
    from lfs.order.models import OrderItem
    from decimal import Decimal

    # Create a test product
    product = Product.objects.create(
        name="Test Product",
        slug="test-product",
        sku="TEST-001",
        price=Decimal("29.99"),
        active=True,
    )

    # Create order item
    OrderItem.objects.create(
        order=order,
        product=product,
        product_name=product.name,
        product_sku=product.sku,
        product_price_gross=product.price,
        product_tax=Decimal("5.70"),
        product_amount=2,
        price_gross=Decimal("59.98"),
    )

    return order


# Page-related fixtures


@pytest.fixture
def root_page(db):
    """Create the root page (id=1) for testing."""
    return Page.objects.create(
        id=1,
        title="Root Page",
        slug="root",
        active=True,
        position=1,
        short_text="Root page short text",
        body="Root page body content",
        meta_title="<title>",
        meta_description="Root page meta description",
        meta_keywords="root, page, meta",
    )


@pytest.fixture
def page(db, shop_for_portlets):
    """Sample Page for testing."""
    return Page.objects.create(
        title="Test Page",
        slug="test-page",
        active=True,
        position=10,
        short_text="Test page short text",
        body="Test page body content",
        meta_title="<title>",
        meta_description="Test page meta description",
        meta_keywords="test, page, meta",
    )


@pytest.fixture
def regular_page(db):
    """Sample regular Page (not root) for testing."""
    # Ensure we don't get id=1 by creating with explicit id
    return Page.objects.create(
        id=2,  # Explicitly set id to avoid root page conflict
        title="Regular Page",
        slug="regular-page",
        active=True,
        position=15,
        short_text="Regular page short text",
        body="Regular page body content",
        meta_title="<title>",
        meta_description="Regular page meta description",
        meta_keywords="regular, page, meta",
    )


@pytest.fixture
def multiple_pages(db):
    """Multiple Pages for list testing."""
    pages = []
    for i in range(3):
        page = Page.objects.create(
            title=f"Test Page {i+1}",
            slug=f"test-page-{i+1}",
            active=True,
            position=(i + 1) * 10,
            short_text=f"Test page {i+1} short text",
            body=f"Test page {i+1} body content",
            meta_title="<title>",
            meta_description=f"Test page {i+1} meta description",
            meta_keywords=f"test, page{i+1}, meta",
        )
        pages.append(page)
    return pages


@pytest.fixture
def inactive_page(db):
    """Inactive Page for testing."""
    return Page.objects.create(
        title="Inactive Page",
        slug="inactive-page",
        active=False,
        position=20,
        short_text="Inactive page short text",
        body="Inactive page body content",
        meta_title="<title>",
        meta_description="Inactive page meta description",
        meta_keywords="inactive, page, meta",
    )


@pytest.fixture
def page_with_file(db, tmp_path):
    """Page with attached file for testing."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    # Create a temporary file


# Portlet-related fixtures


@pytest.fixture
def slot(db):
    """Sample Slot for testing."""
    return Slot.objects.create(name="Test Slot")


@pytest.fixture
def multiple_slots(db):
    """Multiple Slots for testing."""
    slots = []
    for i in range(3):
        slot = Slot.objects.create(name=f"Test Slot {i+1}")
        slots.append(slot)
    return slots


@pytest.fixture
def text_portlet(db):
    """Sample TextPortlet for testing."""
    return TextPortlet.objects.create(title="Test Portlet", text="Test portlet content")


@pytest.fixture
def portlet_registration(db):
    """Sample PortletRegistration for testing."""
    return PortletRegistration.objects.create(type="textportlet", name="Text Portlet", active=True)


@pytest.fixture
def portlet_assignment(db, page, slot, text_portlet, shop_for_portlets):
    """Sample PortletAssignment for testing."""
    from django.contrib.contenttypes.models import ContentType

    return PortletAssignment.objects.create(slot=slot, content=page, portlet=text_portlet, position=10)


@pytest.fixture
def portlet_blocking(db, page, slot):
    """Sample PortletBlocking for testing."""
    from django.contrib.contenttypes.models import ContentType

    return PortletBlocking.objects.create(
        slot=slot, content_type=ContentType.objects.get_for_model(page), content_id=page.id
    )


@pytest.fixture
def multiple_portlet_assignments(db, page, multiple_slots, shop_for_portlets):
    """Multiple PortletAssignments for testing."""
    from django.contrib.contenttypes.models import ContentType

    assignments = []
    for i, slot in enumerate(multiple_slots):
        portlet = TextPortlet.objects.create(title=f"Test Portlet {i+1}", text=f"Content {i+1}")
        assignment = PortletAssignment.objects.create(slot=slot, content=page, portlet=portlet, position=(i + 1) * 10)
        assignments.append(assignment)
    return assignments


@pytest.fixture
def shop_for_portlets(db, default_country, delivery_time):
    """Create a shop for portlet testing."""
    from lfs.core.models import Shop

    return Shop.objects.create(
        name="Test Shop for Portlets",
        shop_owner="Test Owner",
        from_email="test@example.com",
        notification_emails="admin@example.com",
        default_country=default_country,
        delivery_time=delivery_time,
    )


@pytest.fixture
def page_with_file(db, tmp_path):
    """Page with attached file for testing."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    test_file = SimpleUploadedFile("test_file.txt", b"Test file content", content_type="text/plain")

    page = Page.objects.create(
        title="Page With File",
        slug="page-with-file",
        active=True,
        position=30,
        short_text="Page with file short text",
        body="Page with file body content",
        meta_title="<title>",
        meta_description="Page with file meta description",
        meta_keywords="page, file, meta",
    )

    # Attach the file
    page.file = test_file
    page.save()

    return page


# Featured product fixtures


@pytest.fixture
def multiple_products(db, shop):
    """Multiple Products for testing."""
    from decimal import Decimal

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
def many_products(db, shop):
    """Many Products for pagination testing."""
    from decimal import Decimal

    products = []
    for i in range(30):  # Enough to trigger pagination
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
def multiple_categories(db):
    """Multiple Categories for testing."""
    categories = []
    for i, name in enumerate(["Category C", "Category A", "Category B"]):  # Unsorted for testing
        category = Category.objects.create(
            name=name,
            slug=f"category-{name.lower().replace(' ', '-')}",
            position=(i + 1) * 10,
        )
        categories.append(category)
    return categories


@pytest.fixture
def featured_products(db, multiple_products):
    """Multiple FeaturedProducts for testing."""
    featured = []
    for i, product in enumerate(multiple_products[:3]):  # Feature first 3 products
        fp = FeaturedProduct.objects.create(
            product=product,
            position=(i + 1) * 10,
        )
        featured.append(fp)
    return featured


@pytest.fixture
def product_with_variant(db, shop):
    """Product with variant for testing variant filtering."""
    from decimal import Decimal
    from lfs.catalog.settings import PRODUCT_WITH_VARIANTS, VARIANT

    # Create parent product
    parent = Product.objects.create(
        name="Parent Product",
        slug="parent-product",
        sku="PARENT-001",
        price=Decimal("29.99"),
        active=True,
        sub_type=PRODUCT_WITH_VARIANTS,
    )

    # Create variant
    variant = Product.objects.create(
        name="Variant Product",
        slug="variant-product",
        sku="VARIANT-001",
        price=Decimal("39.99"),
        active=True,
        sub_type=VARIANT,
        parent=parent,
        active_sku=False,  # Use parent's SKU
        active_name=False,  # Use parent's name
    )

    return parent, variant


# Topseller product fixtures


@pytest.fixture
def topseller_products(db, multiple_products):
    """Multiple Topseller products for testing."""
    topseller = []
    for i, product in enumerate(multiple_products[:3]):  # Make first 3 products topseller
        tp = Topseller.objects.create(
            product=product,
            position=(i + 1) * 10,
        )
        topseller.append(tp)
    return topseller


@pytest.fixture
def hierarchical_categories(db):
    """Create hierarchical categories for testing category filtering."""
    # Create parent categories
    parent1 = Category.objects.create(
        name="Parent Category 1",
        slug="parent-category-1",
        position=10,
    )
    parent2 = Category.objects.create(
        name="Parent Category 2",
        slug="parent-category-2",
        position=20,
    )

    # Create child categories
    child1 = Category.objects.create(
        name="Child Category 1",
        slug="child-category-1",
        position=10,
        parent=parent1,
    )
    child2 = Category.objects.create(
        name="Child Category 2",
        slug="child-category-2",
        position=20,
        parent=parent1,
    )

    # Create grandchild category
    grandchild = Category.objects.create(
        name="Grandchild Category",
        slug="grandchild-category",
        position=10,
        parent=child1,
    )

    return [parent1, parent2, child1, child2, grandchild]


# Customer-related fixtures for edge case testing


@pytest.fixture
def mock_request():
    """Mock request object for testing."""
    factory = RequestFactory()
    request = factory.get("/")
    request.session = {}
    return request


@pytest.fixture
def user_with_customer(db):
    """User with associated customer and address."""
    user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
    customer = Customer.objects.create(user=user, session="test_session_123")
    address = Address.objects.create(
        customer=customer,
        firstname="John",
        lastname="Doe",
        line1="123 Main St",
        city="Test City",
        zip_code="12345",
        email="john.doe@example.com",
    )
    return user, customer, address


@pytest.fixture
def multiple_customers(db):
    """Multiple customers for testing pagination and filtering."""
    customers = []

    # Create user-based customers
    for i in range(15):
        user = User.objects.create_user(username=f"user{i+1}", email=f"user{i+1}@example.com", password="testpass123")
        customer = Customer.objects.create(user=user, session=f"user_session_{i+1}")
        Address.objects.create(
            customer=customer,
            firstname=f"User{i+1}",
            lastname="Test",
            line1=f"{i+1}00 Main St",
            city="Test City",
            zip_code=f"{10000+i}",
            email=f"user{i+1}@example.com",
        )
        customers.append(customer)

    # Create session-based customers
    for i in range(5):
        customer = Customer.objects.create(session=f"session_{i+1}")
        Address.objects.create(
            customer=customer,
            firstname=f"Session{i+1}",
            lastname="User",
            line1=f"{i+16}00 Main St",
            city="Test City",
            zip_code=f"{10000+i+15}",
            email=f"session{i+1}@example.com",
        )
        customers.append(customer)

    return customers


# Manufacturer and Category fixtures for portlet testing


@pytest.fixture
def manufacturer(db):
    """Sample Manufacturer for testing."""
    return Manufacturer.objects.create(
        name="Test Manufacturer",
        slug="test-manufacturer",
        short_description="Test manufacturer short description",
        description="Test manufacturer description",
        position=10,
    )


@pytest.fixture
def category(db):
    """Sample Category for testing."""
    return Category.objects.create(
        name="Test Category",
        slug="test-category",
        position=10,
    )
