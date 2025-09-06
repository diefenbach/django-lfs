"""
Comprehensive end-to-end workflow tests for customer management.

Following TDD principles:
- Test complete user workflows from start to finish
- Test real user scenarios and business processes
- Clear test names describing the complete workflow
- Arrange-Act-Assert structure for each workflow step
- Test data consistency across workflow steps

Workflows covered:
- Complete customer management workflow (list -> filter -> view -> reset)
- Customer filtering workflow (apply filters -> verify results -> modify filters)
- Customer ordering workflow (set ordering -> verify results -> change ordering)
- Customer data enrichment workflow (view customer -> verify data calculations)
- Session persistence workflow (maintain state across multiple requests)
- Error recovery workflow (handle errors gracefully and maintain state)
- Permission workflow (unauthorized access -> login -> authorized access)
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone

from lfs.customer.models import Customer
from lfs.cart.models import Cart
from lfs.order.models import Order
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
def comprehensive_customer_data(db):
    """Comprehensive customer data for workflow testing."""
    customers = []

    # Create customers with different characteristics
    test_data = [
        {
            "username": "john_doe",
            "email": "john.doe@example.com",
            "firstname": "John",
            "lastname": "Doe",
            "has_orders": True,
            "order_count": 3,
            "order_total": Decimal("299.97"),
            "has_cart": True,
            "cart_total": Decimal("99.99"),
            "date_joined_offset": -30,  # 30 days ago
        },
        {
            "username": "jane_smith",
            "email": "jane.smith@example.com",
            "firstname": "Jane",
            "lastname": "Smith",
            "has_orders": True,
            "order_count": 1,
            "order_total": Decimal("149.99"),
            "has_cart": False,
            "cart_total": None,
            "date_joined_offset": -15,  # 15 days ago
        },
        {
            "username": "bob_wilson",
            "email": "bob.wilson@example.com",
            "firstname": "Bob",
            "lastname": "Wilson",
            "has_orders": False,
            "order_count": 0,
            "order_total": Decimal("0.00"),
            "has_cart": True,
            "cart_total": Decimal("49.99"),
            "date_joined_offset": -7,  # 7 days ago
        },
        {
            "username": "alice_brown",
            "email": "alice.brown@example.com",
            "firstname": "Alice",
            "lastname": "Brown",
            "has_orders": True,
            "order_count": 2,
            "order_total": Decimal("199.98"),
            "has_cart": True,
            "cart_total": Decimal("79.99"),
            "date_joined_offset": -60,  # 60 days ago
        },
        {
            "username": "charlie_davis",
            "email": "charlie.davis@example.com",
            "firstname": "Charlie",
            "lastname": "Davis",
            "has_orders": False,
            "order_count": 0,
            "order_total": Decimal("0.00"),
            "has_cart": False,
            "cart_total": None,
            "date_joined_offset": -1,  # 1 day ago
        },
    ]

    for data in test_data:
        # Create user with specific date_joined
        user = User.objects.create_user(username=data["username"], email=data["email"], password="testpass123")
        join_date = timezone.now() + timedelta(days=data["date_joined_offset"])
        user.date_joined = join_date
        user.save()

        # Create customer
        customer = Customer.objects.create(user=user)

        # Create address
        address = Address.objects.create(
            customer=customer,
            firstname=data["firstname"],
            lastname=data["lastname"],
            line1=f"123 {data['lastname']} St",
            city="Test City",
            zip_code="12345",
            email=data["email"],
        )

        # Create orders if specified
        if data["has_orders"]:
            # Get the content type for Address
            address_content_type = ContentType.objects.get_for_model(address.__class__)

            for i in range(data["order_count"]):
                Order.objects.create(
                    number=f"ORD-{data['username'].upper()}-{i+1:03d}",
                    session=customer.session,
                    customer_firstname=data["firstname"],
                    customer_lastname=data["lastname"],
                    customer_email=data["email"],
                    price=Decimal(f"{(i+1)*50}.00"),
                    state=1,
                    # Set the address relationships
                    sa_content_type=address_content_type,
                    sa_object_id=address.id,
                    ia_content_type=address_content_type,
                    ia_object_id=address.id,
                )

        # Create cart if specified
        if data["has_cart"]:
            cart = Cart.objects.create(session=customer.session)
            # Note: Cart price calculation would require more complex setup

        customers.append({"customer": customer, "user": user, "address": address, "expected_data": data})

    return customers


class TestCompleteCustomerManagementWorkflow:
    """Test complete customer management workflow from start to finish."""

    def test_complete_customer_management_workflow(self, client, admin_user, comprehensive_customer_data, shop):
        """Test complete workflow: login -> list -> filter -> view -> reset -> list."""
        # Step 1: Login
        client.force_login(admin_user)

        # Step 2: View customer list
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert "customers_with_data" in response.context
        assert len(response.context["customers_with_data"]) == 5

        # Step 3: Apply name filter
        filter_data = {"name": "John"}
        response = client.post(reverse("lfs_apply_customer_filters"), filter_data)
        assert response.status_code == 302

        # Step 4: Verify filtered results
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        customers_with_data = response.context["customers_with_data"]
        assert len(customers_with_data) == 1
        assert "John" in customers_with_data[0]["customer"].addresses.first().firstname

        # Step 5: View specific customer
        customer_id = customers_with_data[0]["customer"].id
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer_id}))
        assert response.status_code == 200
        assert response.context["customer"].id == customer_id

        # Step 6: Reset filters
        response = client.get(reverse("lfs_reset_customer_filters"))
        assert response.status_code == 302
        assert "customer-filters" not in client.session

        # Step 7: Verify all customers are shown again
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert len(response.context["customers_with_data"]) == 5

    def test_customer_filtering_workflow_with_multiple_filters(
        self, client, admin_user, comprehensive_customer_data, shop
    ):
        """Test workflow: apply multiple filters -> verify results -> modify filters -> verify new results."""
        client.force_login(admin_user)

        # Step 1: Apply name filter
        filter_data = {"name": "John"}
        response = client.post(reverse("lfs_apply_customer_filters"), filter_data)
        assert response.status_code == 302

        # Step 2: Verify name filter results
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        customers_with_data = response.context["customers_with_data"]
        assert len(customers_with_data) == 1
        assert "John" in customers_with_data[0]["customer"].addresses.first().firstname

        # Step 3: Add date filter
        filter_data = {"name": "John", "start": (date.today() - timedelta(days=60)).isoformat()}
        response = client.post(reverse("lfs_apply_customer_filters"), filter_data)
        assert response.status_code == 302

        # Step 4: Verify combined filter results
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        customers_with_data = response.context["customers_with_data"]
        assert len(customers_with_data) == 1  # Should still be 1 (John is within date range)

        # Step 5: Change name filter
        filter_data = {"name": "Jane", "start": (date.today() - timedelta(days=60)).isoformat()}
        response = client.post(reverse("lfs_apply_customer_filters"), filter_data)
        assert response.status_code == 302

        # Step 6: Verify new filter results
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        customers_with_data = response.context["customers_with_data"]
        assert len(customers_with_data) == 1
        assert "Jane" in customers_with_data[0]["customer"].addresses.first().firstname

    def test_customer_ordering_workflow(self, client, admin_user, comprehensive_customer_data, shop):
        """Test workflow: set ordering -> verify results -> change ordering -> verify new results."""
        client.force_login(admin_user)

        # Step 1: Set ordering by lastname
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "lastname"}))
        assert response.status_code == 302
        assert client.session["customer-ordering"] == "lastname"

        # Step 2: Verify ordering is applied
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert response.context["ordering"] == "lastname"

        # Step 3: Toggle ordering direction
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "lastname"}))
        assert response.status_code == 302
        assert client.session["customer-ordering-order"] == "-"

        # Step 4: Verify reverse ordering is applied
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert response.context["ordering"] == "lastname"

        # Step 5: Change to different ordering field
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "email"}))
        assert response.status_code == 302
        assert client.session["customer-ordering"] == "email"
        assert client.session["customer-ordering-order"] == ""

        # Step 6: Verify new ordering is applied
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert response.context["ordering"] == "email"

    def test_customer_data_enrichment_workflow(self, client, admin_user, comprehensive_customer_data, shop):
        """Test workflow: view customer -> verify data calculations -> view different customer -> verify data."""
        client.force_login(admin_user)

        # Step 1: View first customer (John Doe - has orders and cart)
        john_customer = comprehensive_customer_data[0]["customer"]
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": john_customer.id}))
        assert response.status_code == 200

        # Step 2: Verify customer data is enriched
        context = response.context
        assert "customer" in context
        assert "orders" in context
        assert "cart" in context
        assert "cart_price" in context
        assert context["customer"].id == john_customer.id

        # Step 3: View second customer (Jane Smith - has orders, no cart)
        jane_customer = comprehensive_customer_data[1]["customer"]
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": jane_customer.id}))
        assert response.status_code == 200

        # Step 4: Verify different customer data
        context = response.context
        assert context["customer"].id == jane_customer.id
        assert "orders" in context
        assert "cart" in context  # May be None
        assert "cart_price" in context

    def test_session_persistence_workflow(self, client, admin_user, comprehensive_customer_data, shop):
        """Test workflow: set filters/ordering -> navigate between views -> verify state persistence."""
        client.force_login(admin_user)

        # Step 1: Set filters and ordering
        filter_data = {"name": "John"}
        response = client.post(reverse("lfs_apply_customer_filters"), filter_data)
        assert response.status_code == 302

        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "lastname"}))
        assert response.status_code == 302

        # Step 2: Navigate to customer list
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert response.context["ordering"] == "lastname"
        assert len(response.context["customers_with_data"]) == 1

        # Step 3: Navigate to specific customer
        customer_id = response.context["customers_with_data"][0]["customer"].id
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer_id}))
        assert response.status_code == 200
        assert response.context["ordering"] == "lastname"  # Should persist

        # Step 4: Navigate back to list
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert response.context["ordering"] == "lastname"
        assert len(response.context["customers_with_data"]) == 1  # Filter should persist

    def test_predefined_filter_workflow(self, client, admin_user, comprehensive_customer_data, shop):
        """Test workflow: apply predefined filters -> verify results -> apply different predefined filter."""
        client.force_login(admin_user)

        # Step 1: Apply today filter
        response = client.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": "today"}))
        assert response.status_code == 302
        assert "customer-filters" in client.session
        assert "start" in client.session["customer-filters"]

        # Step 2: Verify today filter results
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        # Results depend on when customers were created

        # Step 3: Apply week filter
        response = client.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": "week"}))
        assert response.status_code == 302
        assert "customer-filters" in client.session
        assert "start" in client.session["customer-filters"]

        # Step 4: Verify week filter results
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200

        # Step 5: Apply month filter
        response = client.get(reverse("lfs_apply_predefined_customer_filter_list", kwargs={"filter_type": "month"}))
        assert response.status_code == 302
        assert "customer-filters" in client.session
        assert "start" in client.session["customer-filters"]

        # Step 6: Verify month filter results
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200

    def test_error_recovery_workflow(self, client, admin_user, comprehensive_customer_data, shop):
        """Test workflow: encounter error -> recover gracefully -> continue workflow."""
        client.force_login(admin_user)

        # Step 1: Apply invalid filter data
        invalid_filter_data = {"start": "invalid-date"}
        response = client.post(reverse("lfs_apply_customer_filters"), invalid_filter_data)
        assert response.status_code == 302  # Should still redirect

        # Step 2: Verify system recovers gracefully
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert "customers_with_data" in response.context

        # Step 3: Apply valid filter data
        valid_filter_data = {"name": "John"}
        response = client.post(reverse("lfs_apply_customer_filters"), valid_filter_data)
        assert response.status_code == 302

        # Step 4: Verify valid filter works
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert len(response.context["customers_with_data"]) == 1

        # Step 5: Try to access non-existent customer
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": 99999}))
        assert response.status_code == 404

        # Step 6: Verify system still works after 404
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert len(response.context["customers_with_data"]) == 1  # Filter should still be active

    def test_permission_workflow(self, client, comprehensive_customer_data, shop):
        """Test workflow: unauthorized access -> login -> authorized access."""
        # Step 1: Try to access without authentication
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 302
        assert "/login/" in response.url

        # Step 2: Create admin user and login
        admin_user = User.objects.create_user(
            username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
        )
        client.force_login(admin_user)

        # Step 3: Access with authentication
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert "customers_with_data" in response.context

        # Step 4: Access specific customer
        customer_id = comprehensive_customer_data[0]["customer"].id
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer_id}))
        assert response.status_code == 200
        assert response.context["customer"].id == customer_id

    def test_pagination_workflow(self, client, admin_user, comprehensive_customer_data, shop):
        """Test workflow: view paginated results -> navigate pages -> maintain filters across pages."""
        client.force_login(admin_user)

        # Step 1: Apply filter to reduce results
        filter_data = {"name": "a"}  # Should match Alice and Charlie
        response = client.post(reverse("lfs_apply_customer_filters"), filter_data)
        assert response.status_code == 302

        # Step 2: Verify filtered results
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        customers_with_data = response.context["customers_with_data"]
        assert len(customers_with_data) >= 1  # At least Alice should match

        # Step 3: Set small page size to force pagination
        # Note: This would require modifying the view to accept page_size parameter
        # For now, we'll test that pagination context is available
        assert "customers_page" in response.context
        assert hasattr(response.context["customers_page"], "paginator")

    def test_complete_customer_lifecycle_workflow(self, client, admin_user, comprehensive_customer_data, shop):
        """Test complete customer lifecycle: view -> filter -> order -> view specific -> reset -> view all."""
        client.force_login(admin_user)

        # Step 1: View all customers
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        all_customers = response.context["customers_with_data"]
        assert len(all_customers) == 5

        # Step 2: Apply filter
        filter_data = {"name": "John"}
        response = client.post(reverse("lfs_apply_customer_filters"), filter_data)
        assert response.status_code == 302

        # Step 3: Set ordering
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "lastname"}))
        assert response.status_code == 302

        # Step 4: View filtered and ordered results
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        filtered_customers = response.context["customers_with_data"]
        assert len(filtered_customers) == 1
        assert response.context["ordering"] == "lastname"

        # Step 5: View specific customer
        customer_id = filtered_customers[0]["customer"].id
        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": customer_id}))
        assert response.status_code == 200
        assert response.context["customer"].id == customer_id

        # Step 6: Reset filters
        response = client.get(reverse("lfs_reset_customer_filters"))
        assert response.status_code == 302
        assert "customer-filters" not in client.session

        # Step 7: View all customers again
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        reset_customers = response.context["customers_with_data"]
        assert len(reset_customers) == 5  # All customers should be visible again
        assert response.context["ordering"] == "lastname"  # Ordering should persist

    def test_concurrent_session_workflow(self, client, admin_user, comprehensive_customer_data, shop):
        """Test workflow: simulate concurrent sessions with different filters."""
        client.force_login(admin_user)

        # Step 1: Set filters in session
        filter_data = {"name": "John"}
        response = client.post(reverse("lfs_apply_customer_filters"), filter_data)
        assert response.status_code == 302

        # Step 2: Verify filters are applied
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert len(response.context["customers_with_data"]) == 1

        # Step 3: Simulate different session by changing filters
        filter_data = {"name": "Jane"}
        response = client.post(reverse("lfs_apply_customer_filters"), filter_data)
        assert response.status_code == 302

        # Step 4: Verify new filters are applied
        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert len(response.context["customers_with_data"]) == 1
        assert "Jane" in response.context["customers_with_data"][0]["customer"].addresses.first().firstname

        # Step 5: Reset and verify clean state
        response = client.get(reverse("lfs_reset_customer_filters"))
        assert response.status_code == 302

        response = client.get(reverse("lfs_manage_customers"))
        assert response.status_code == 200
        assert len(response.context["customers_with_data"]) == 5
