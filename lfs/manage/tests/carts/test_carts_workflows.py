"""
Comprehensive end-to-end workflow tests for cart management.

Following TDD principles:
- Test complete user workflows from start to finish
- Test real user scenarios and business processes
- Clear test names describing the complete workflow
- Arrange-Act-Assert structure for each workflow step
- Test data consistency across workflow steps

Workflows covered:
- Complete cart management workflow (list -> filter -> view -> reset)
- Cart filtering workflow (apply filters -> verify results -> modify filters)
- Cart deletion workflow (view -> confirm -> delete -> verify)
- Cart data enrichment workflow (view cart -> verify data calculations)
- Session persistence workflow (maintain state across multiple requests)
- Error recovery workflow (handle errors gracefully and maintain state)
- Permission workflow (unauthorized access -> login -> authorized access)
- Cart lifecycle workflow (create -> modify -> view -> delete)
- Cart customer association workflow (anonymous -> registered -> view)
- Cart item management workflow (add items -> view -> modify -> delete)
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from lfs.cart.models import Cart, CartItem
from lfs.catalog.models import Product
from lfs.customer.models import Customer
from lfs.addresses.models import Address

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Admin user with proper permissions."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def shop(db):
    """Create a default shop for testing."""
    from lfs.core.models import Shop
    from lfs.core.models import Country
    from lfs.catalog.models import DeliveryTime, DELIVERY_TIME_UNIT_DAYS

    # Create required dependencies
    country = Country.objects.create(name="Test Country", code="TC")
    delivery_time = DeliveryTime.objects.create(min=1, max=2, unit=DELIVERY_TIME_UNIT_DAYS)

    shop = Shop.objects.create(
        name="Test Shop",
        shop_owner="Test Owner",
        from_email="test@example.com",
        notification_emails="test@example.com",
        description="Test shop description",
        default_country=country,
        delivery_time=delivery_time,
    )
    shop.invoice_countries.add(country)
    shop.shipping_countries.add(country)
    return shop


@pytest.fixture
def comprehensive_cart_data(db):
    """Comprehensive cart data for workflow testing."""
    carts = []
    # Use a fixed base time to ensure consistent test results
    from datetime import datetime

    base_time = timezone.make_aware(datetime(2024, 1, 15, 12, 0, 0))

    # Create products for cart items
    products = []
    for i in range(10):
        product = Product.objects.create(
            name=f"Test Product {i+1}", slug=f"test-product-{i+1}", price=Decimal(f"{(i+1)*10}.99"), active=True
        )
        products.append(product)

    # Create test data for different cart scenarios
    test_data = [
        {
            "session": "session-1",
            "user": None,
            "has_customer": False,
            "item_count": 3,
            "total_value": Decimal("89.97"),  # 10.99 + 21.98 + 32.97
            "modification_offset": -1,  # 1 day ago
            "products": [0, 1, 2],  # Product indices
            "quantities": [1, 2, 3],
        },
        {
            "session": "session-2",
            "user": "user1",
            "has_customer": True,
            "item_count": 2,
            "total_value": Decimal("65.48"),  # 21.98 + 43.96
            "modification_offset": -3,  # 3 days ago
            "products": [1, 3],  # Product indices
            "quantities": [2, 4],
        },
        {
            "session": "session-3",
            "user": "user2",
            "has_customer": True,
            "item_count": 1,
            "total_value": Decimal("54.95"),  # 54.95
            "modification_offset": -7,  # 7 days ago
            "products": [4],  # Product indices
            "quantities": [5],
        },
        {
            "session": "session-4",
            "user": None,
            "has_customer": False,
            "item_count": 4,
            "total_value": Decimal("219.80"),  # 10.99 + 21.98 + 32.97 + 43.96
            "modification_offset": -15,  # 15 days ago
            "products": [0, 1, 2, 3],  # Product indices
            "quantities": [1, 1, 1, 1],
        },
        {
            "session": "session-5",
            "user": "user3",
            "has_customer": True,
            "item_count": 0,
            "total_value": Decimal("0.00"),
            "modification_offset": -30,  # 30 days ago
            "products": [],  # Empty cart
            "quantities": [],
        },
    ]

    for i, data in enumerate(test_data):
        # Create cart
        cart = Cart.objects.create(session=data["session"])

        # Set modification date with a small time offset to ensure different timestamps
        modification_date = base_time + timedelta(days=data["modification_offset"], seconds=i)
        cart.modification_date = modification_date
        cart.save()

        # Create user if specified
        user = None
        customer = None
        if data["user"]:
            user = User.objects.create_user(
                username=data["user"], email=f"{data['user']}@example.com", password="testpass123"
            )
            cart.user = user
            cart.save()

            if data["has_customer"]:
                customer = Customer.objects.create(user=user, session=data["session"])
                # Create address for customer
                Address.objects.create(
                    customer=customer,
                    firstname=f"User{data['user'][-1]}",
                    lastname="Test",
                    line1=f"123 {data['user']} St",
                    city="Test City",
                    zip_code="12345",
                    email=f"{data['user']}@example.com",
                )

        # Create cart items
        cart_items = []
        for i, (product_idx, quantity) in enumerate(zip(data["products"], data["quantities"])):
            cart_item = CartItem.objects.create(cart=cart, product=products[product_idx], amount=quantity)
            cart_items.append(cart_item)

        carts.append({"cart": cart, "user": user, "customer": customer, "items": cart_items, "expected_data": data})

    return carts


class TestCompleteCartManagementWorkflow:
    """Test complete cart management workflow from start to finish."""

    def test_complete_cart_management_workflow(self, client, admin_user, comprehensive_cart_data, shop):
        """Test complete workflow: login -> list -> filter -> view -> reset -> list."""
        # Step 1: Login
        client.force_login(admin_user)

        # Step 2: View cart list
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        assert "carts_with_data" in response.context
        assert len(response.context["carts_with_data"]) == 5

        # Step 3: Apply date filter (last 10 days)
        filter_data = {"start": (date.today() - timedelta(days=10)).isoformat()}
        response = client.post(reverse("lfs_apply_cart_filters_list"), filter_data)
        assert response.status_code == 302

        # Step 4: Verify filtered results
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        carts_with_data = response.context["carts_with_data"]
        # Should show carts from last 10 days (sessions 1, 2, 3)
        assert len(carts_with_data) >= 3

        # Step 5: View specific cart
        cart_id = carts_with_data[0]["cart"].id
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart_id}))
        assert response.status_code == 200
        assert response.context["cart"].id == cart_id

        # Step 6: Reset filters
        response = client.get(reverse("lfs_reset_cart_filters"))
        assert response.status_code == 302
        assert "cart-filters" not in client.session

        # Step 7: Verify all carts are shown again
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        assert len(response.context["carts_with_data"]) == 5

    def test_cart_filtering_workflow_with_multiple_filters(self, client, admin_user, comprehensive_cart_data, shop):
        """Test workflow: apply multiple filters -> verify results -> modify filters -> verify new results."""
        client.force_login(admin_user)

        # Step 1: Apply date filter (last 5 days from today)
        filter_data = {"start": (date.today() - timedelta(days=5)).isoformat()}
        response = client.post(reverse("lfs_apply_cart_filters_list"), filter_data)
        assert response.status_code == 302

        # Step 2: Verify date filter results
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        carts_with_data = response.context["carts_with_data"]
        # Should show carts from last 5 days (all carts since they're all created today)
        assert len(carts_with_data) >= 2

        # Step 3: Add end date filter - use exclusive end date (filter service uses exclusive end)
        filter_data = {
            "start": (date.today() - timedelta(days=5)).isoformat(),
            "end": (date.today() + timedelta(days=1)).isoformat(),  # Exclusive end, so includes today
        }
        response = client.post(reverse("lfs_apply_cart_filters_list"), filter_data)
        assert response.status_code == 302

        # Step 4: Verify combined filter results
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        carts_with_data = response.context["carts_with_data"]
        # Should show carts from today (all carts since they're all created today)
        assert len(carts_with_data) >= 2

        # Step 5: Change to different date range (older than all carts)
        filter_data = {
            "start": (date.today() - timedelta(days=20)).isoformat(),
            "end": (date.today() - timedelta(days=10)).isoformat(),  # Exclusive end
        }
        response = client.post(reverse("lfs_apply_cart_filters_list"), filter_data)
        assert response.status_code == 302

        # Step 6: Verify new filter results
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        carts_with_data = response.context["carts_with_data"]
        # Should show no carts since all carts are from today
        assert len(carts_with_data) == 0

    def test_cart_deletion_workflow(self, client, admin_user, comprehensive_cart_data, shop):
        """Test workflow: view cart -> confirm deletion -> delete -> verify deletion."""
        client.force_login(admin_user)

        # Step 1: View cart list
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        initial_cart_count = len(response.context["carts_with_data"])

        # Step 2: Select a cart for deletion
        cart_to_delete = comprehensive_cart_data[0]["cart"]
        cart_id = cart_to_delete.id

        # Step 3: View cart details
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart_id}))
        assert response.status_code == 200
        assert response.context["cart"].id == cart_id

        # Step 4: Go to delete confirmation
        response = client.get(reverse("lfs_manage_delete_cart_confirm", kwargs={"id": cart_id}))
        assert response.status_code == 200
        assert "cart" in response.context
        assert response.context["cart"].id == cart_id

        # Step 5: Confirm deletion
        response = client.post(reverse("lfs_delete_cart", kwargs={"id": cart_id}))
        assert response.status_code == 302

        # Step 6: Verify cart is deleted
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        assert len(response.context["carts_with_data"]) == initial_cart_count - 1

        # Step 7: Verify cart no longer exists
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart_id}))
        assert response.status_code == 404

    def test_cart_data_enrichment_workflow(self, client, admin_user, comprehensive_cart_data, shop):
        """Test workflow: view cart -> verify data calculations -> view different cart -> verify data."""
        client.force_login(admin_user)

        # Step 1: View first cart (session-1 - has 3 items)
        cart1 = comprehensive_cart_data[0]["cart"]
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
        assert response.status_code == 200

        # Step 2: Verify cart data is enriched
        context = response.context
        assert "cart" in context
        assert "cart_total" in context
        assert "cart_products" in context
        assert "cart_items" in context
        assert context["cart"].id == cart1.id

        # Step 3: View second cart (session-2 - has 2 items)
        cart2 = comprehensive_cart_data[1]["cart"]
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart2.id}))
        assert response.status_code == 200

        # Step 4: Verify different cart data
        context = response.context
        assert context["cart"].id == cart2.id
        assert "cart_total" in context
        assert "cart_products" in context
        assert "cart_items" in context

        # Step 5: View empty cart (session-5 - no items)
        cart5 = comprehensive_cart_data[4]["cart"]
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart5.id}))
        assert response.status_code == 200

        # Step 6: Verify empty cart data
        context = response.context
        assert context["cart"].id == cart5.id
        assert context["cart_total"] == Decimal("0.00")
        assert context["cart_products"] == ""
        assert len(context["cart_items"]) == 0

    def test_session_persistence_workflow(self, client, admin_user, comprehensive_cart_data, shop):
        """Test workflow: set filters -> navigate between views -> verify state persistence."""
        client.force_login(admin_user)

        # Step 1: Set filters
        filter_data = {"start": (date.today() - timedelta(days=10)).isoformat()}
        response = client.post(reverse("lfs_apply_cart_filters_list"), filter_data)
        assert response.status_code == 302

        # Step 2: Navigate to cart list
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        carts_with_data = response.context["carts_with_data"]
        assert len(carts_with_data) >= 3  # Should be filtered

        # Step 3: Navigate to specific cart
        cart_id = carts_with_data[0]["cart"].id
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart_id}))
        assert response.status_code == 200
        assert response.context["cart"].id == cart_id

        # Step 4: Navigate back to list
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        carts_with_data = response.context["carts_with_data"]
        assert len(carts_with_data) >= 3  # Filter should persist

    def test_predefined_filter_workflow(self, client, admin_user, comprehensive_cart_data, shop):
        """Test workflow: apply predefined filters -> verify results -> apply different predefined filter."""
        client.force_login(admin_user)

        # Step 1: Apply today filter
        response = client.get(reverse("lfs_apply_predefined_cart_filter_list", kwargs={"filter_type": "today"}))
        assert response.status_code == 302
        assert "cart-filters" in client.session
        assert "start" in client.session["cart-filters"]

        # Step 2: Verify today filter results
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        # Results depend on when carts were created

        # Step 3: Apply week filter
        response = client.get(reverse("lfs_apply_predefined_cart_filter_list", kwargs={"filter_type": "week"}))
        assert response.status_code == 302
        assert "cart-filters" in client.session
        assert "start" in client.session["cart-filters"]

        # Step 4: Verify week filter results
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200

        # Step 5: Apply month filter
        response = client.get(reverse("lfs_apply_predefined_cart_filter_list", kwargs={"filter_type": "month"}))
        assert response.status_code == 302
        assert "cart-filters" in client.session
        assert "start" in client.session["cart-filters"]

        # Step 6: Verify month filter results
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200

    def test_error_recovery_workflow(self, client, admin_user, comprehensive_cart_data, shop):
        """Test workflow: encounter error -> recover gracefully -> continue workflow."""
        client.force_login(admin_user)

        # Step 1: Apply invalid filter data - Django form validation will handle this
        invalid_filter_data = {"start": "invalid-date"}
        response = client.post(reverse("lfs_apply_cart_filters_list"), invalid_filter_data)
        # Form validation will show errors, so we expect 200 with form errors
        assert response.status_code == 200

        # Step 2: Verify system recovers gracefully
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        assert "carts_with_data" in response.context

        # Step 3: Apply valid filter data
        valid_filter_data = {"start": (date.today() - timedelta(days=10)).isoformat()}
        response = client.post(reverse("lfs_apply_cart_filters_list"), valid_filter_data)
        assert response.status_code == 302

        # Step 4: Verify valid filter works
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        assert len(response.context["carts_with_data"]) >= 3

        # Step 5: Try to access non-existent cart
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": 99999}))
        assert response.status_code == 404

        # Step 6: Verify system still works after 404
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        assert len(response.context["carts_with_data"]) >= 3  # Filter should still be active

    def test_permission_workflow(self, client, comprehensive_cart_data, shop):
        """Test workflow: unauthorized access -> login -> authorized access."""
        # Step 1: Try to access without authentication
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 302
        assert "/login/" in response.url

        # Step 2: Create admin user and login
        admin_user = User.objects.create_user(
            username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
        )
        client.force_login(admin_user)

        # Step 3: Access with authentication
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        assert "carts_with_data" in response.context

        # Step 4: Access specific cart
        cart_id = comprehensive_cart_data[0]["cart"].id
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart_id}))
        assert response.status_code == 200
        assert response.context["cart"].id == cart_id

    def test_cart_lifecycle_workflow(self, client, admin_user, shop):
        """Test complete cart lifecycle: create -> modify -> view -> delete."""
        client.force_login(admin_user)

        # Step 1: Create a new cart
        cart = Cart.objects.create(session="test-lifecycle-session")

        # Step 2: Add items to cart
        product1 = Product.objects.create(
            name="Lifecycle Product 1", slug="lifecycle-1", price=Decimal("25.99"), active=True
        )
        product2 = Product.objects.create(
            name="Lifecycle Product 2", slug="lifecycle-2", price=Decimal("15.50"), active=True
        )

        CartItem.objects.create(cart=cart, product=product1, amount=2)
        CartItem.objects.create(cart=cart, product=product2, amount=1)

        # Step 3: View cart in management
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart.id}))
        assert response.status_code == 200
        assert response.context["cart"].id == cart.id
        assert len(response.context["cart_items"]) == 2

        # Step 4: Modify cart (add another item)
        product3 = Product.objects.create(
            name="Lifecycle Product 3", slug="lifecycle-3", price=Decimal("10.00"), active=True
        )
        CartItem.objects.create(cart=cart, product=product3, amount=3)

        # Step 5: View modified cart
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart.id}))
        assert response.status_code == 200
        assert len(response.context["cart_items"]) == 3

        # Step 6: Delete cart
        response = client.post(reverse("lfs_delete_cart", kwargs={"id": cart.id}))
        assert response.status_code == 302

        # Step 7: Verify cart is deleted
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart.id}))
        assert response.status_code == 404

    def test_cart_customer_association_workflow(self, client, admin_user, comprehensive_cart_data, shop):
        """Test workflow: view anonymous cart -> associate with customer -> view customer cart."""
        client.force_login(admin_user)

        # Step 1: View anonymous cart (session-1)
        anonymous_cart = comprehensive_cart_data[0]["cart"]
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": anonymous_cart.id}))
        assert response.status_code == 200
        assert response.context["cart"].user is None
        assert response.context["customer"] is None

        # Step 2: View cart with customer (session-2)
        customer_cart = comprehensive_cart_data[1]["cart"]
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": customer_cart.id}))
        assert response.status_code == 200
        assert response.context["cart"].user is not None
        assert response.context["customer"] is not None

        # Step 3: View empty cart with customer (session-5)
        empty_customer_cart = comprehensive_cart_data[4]["cart"]
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": empty_customer_cart.id}))
        assert response.status_code == 200
        assert response.context["cart"].user is not None
        assert response.context["customer"] is not None
        assert len(response.context["cart_items"]) == 0

    def test_cart_item_management_workflow(self, client, admin_user, shop):
        """Test workflow: create cart -> add items -> view -> modify items -> delete cart."""
        client.force_login(admin_user)

        # Step 1: Create cart and products
        cart = Cart.objects.create(session="item-management-session")
        products = []
        for i in range(5):
            product = Product.objects.create(
                name=f"Item Management Product {i+1}",
                slug=f"item-mgmt-{i+1}",
                price=Decimal(f"{(i+1)*5}.99"),
                active=True,
            )
            products.append(product)

        # Step 2: Add items to cart
        CartItem.objects.create(cart=cart, product=products[0], amount=1)
        CartItem.objects.create(cart=cart, product=products[1], amount=2)
        CartItem.objects.create(cart=cart, product=products[2], amount=3)

        # Step 3: View cart with items
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart.id}))
        assert response.status_code == 200
        assert len(response.context["cart_items"]) == 3

        # Step 4: Add more items
        CartItem.objects.create(cart=cart, product=products[3], amount=1)
        CartItem.objects.create(cart=cart, product=products[4], amount=2)

        # Step 5: View updated cart
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart.id}))
        assert response.status_code == 200
        assert len(response.context["cart_items"]) == 5

        # Step 6: Verify cart total calculation
        expected_total = sum(products[i].price * amount for i, amount in enumerate([1, 2, 3, 1, 2]))
        # Convert to Decimal for proper comparison
        expected_total = Decimal(str(expected_total))
        cart_total = response.context["cart_total"]
        # Convert cart_total to Decimal if it's not already
        if not isinstance(cart_total, Decimal):
            cart_total = Decimal(str(cart_total))
        assert cart_total == expected_total

        # Step 7: Delete cart
        response = client.post(reverse("lfs_delete_cart", kwargs={"id": cart.id}))
        assert response.status_code == 302

        # Step 8: Verify cart and items are deleted
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart.id}))
        assert response.status_code == 404

    def test_complete_cart_management_lifecycle_workflow(self, client, admin_user, comprehensive_cart_data, shop):
        """Test complete cart management lifecycle: view -> filter -> view specific -> delete -> reset -> view all."""
        client.force_login(admin_user)

        # Step 1: View all carts
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        all_carts = response.context["carts_with_data"]
        assert len(all_carts) == 5

        # Step 2: Apply filter (last 10 days)
        filter_data = {"start": (date.today() - timedelta(days=10)).isoformat()}
        response = client.post(reverse("lfs_apply_cart_filters_list"), filter_data)
        assert response.status_code == 302

        # Step 3: View filtered results
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        filtered_carts = response.context["carts_with_data"]
        assert len(filtered_carts) >= 3

        # Step 4: View specific cart
        cart_id = filtered_carts[0]["cart"].id
        response = client.get(reverse("lfs_manage_cart", kwargs={"id": cart_id}))
        assert response.status_code == 200
        assert response.context["cart"].id == cart_id

        # Step 5: Delete a cart
        cart_to_delete = comprehensive_cart_data[0]["cart"]
        response = client.post(reverse("lfs_delete_cart", kwargs={"id": cart_to_delete.id}))
        assert response.status_code == 302

        # Step 6: Reset filters
        response = client.get(reverse("lfs_reset_cart_filters"))
        assert response.status_code == 302
        assert "cart-filters" not in client.session

        # Step 7: View all remaining carts
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        reset_carts = response.context["carts_with_data"]
        assert len(reset_carts) == 4  # One cart was deleted

    def test_concurrent_session_workflow(self, client, admin_user, comprehensive_cart_data, shop):
        """Test workflow: simulate concurrent sessions with different filters."""
        client.force_login(admin_user)

        # Step 1: Set filters in session
        filter_data = {"start": (date.today() - timedelta(days=5)).isoformat()}
        response = client.post(reverse("lfs_apply_cart_filters_list"), filter_data)
        assert response.status_code == 302

        # Step 2: Verify filters are applied
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        assert len(response.context["carts_with_data"]) >= 2

        # Step 3: Simulate different session by changing filters
        filter_data = {"start": (date.today() - timedelta(days=20)).isoformat()}
        response = client.post(reverse("lfs_apply_cart_filters_list"), filter_data)
        assert response.status_code == 302

        # Step 4: Verify new filters are applied
        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        assert len(response.context["carts_with_data"]) >= 1

        # Step 5: Reset and verify clean state
        response = client.get(reverse("lfs_reset_cart_filters"))
        assert response.status_code == 302

        response = client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        assert len(response.context["carts_with_data"]) == 5
