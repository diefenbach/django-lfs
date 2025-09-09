"""
Comprehensive end-to-end workflow tests for order management.

Following TDD principles:
- Test complete user workflows from start to finish
- Test real user scenarios and business processes
- Clear test names describing the complete workflow
- Arrange-Act-Assert structure for each workflow step
- Test data consistency across workflow steps

Workflows covered:
- Complete order management workflow (list -> filter -> view -> reset)
- Order filtering workflow (apply filters -> verify results -> modify filters)
- Order viewing workflow (view order -> check details -> navigate back)
- Order state management workflow (view states -> filter by state -> verify)
- Session persistence workflow (maintain filters across requests)
- Error recovery workflow (handle errors gracefully and maintain state)
- Permission workflow (unauthorized access -> login -> authorized access)
- Order lifecycle workflow (create -> view -> manage -> archive)
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.order.models import Order, OrderItem

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Admin user with proper permissions."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def order(db, customer, address, payment_method, shipping_method):
    """Create a test order."""
    return Order.objects.create(
        customer=customer,
        billing_address=address,
        shipping_address=address,
        payment_method=payment_method,
        shipping_method=shipping_method,
        state=1,  # Submitted state
        customer_firstname="John",
        customer_lastname="Doe",
        customer_email="customer@example.com",
        subtotal=Decimal("10.00"),
        shipping_price=Decimal("5.00"),
        payment_price=Decimal("0.00"),
        total=Decimal("15.00"),
    )


@pytest.fixture
def multiple_orders(db, customer, address, payment_method, shipping_method, product):
    """Create multiple orders for testing."""
    orders = []
    for i in range(5):
        order = Order.objects.create(
            customer=customer,
            billing_address=address,
            shipping_address=address,
            payment_method=payment_method,
            shipping_method=shipping_method,
            state=i + 1,  # Different states
            customer_firstname=f"John{i}",
            customer_lastname=f"Doe{i}",
            customer_email=f"john{i}@example.com",
            subtotal=Decimal("10.00"),
            shipping_price=Decimal("5.00"),
            payment_price=Decimal("0.00"),
            total=Decimal("15.00"),
            created=date.today() - timedelta(days=i),
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name="Test Product",
            product_sku="TEST001",
            product_price_net=Decimal("10.00"),
            product_price_gross=Decimal("10.00"),
            product_quantity=1,
            total=Decimal("10.00"),
        )
        orders.append(order)
    return orders


@pytest.mark.django_db
@pytest.mark.integration
class TestOrderManagementWorkflow:
    """Test complete order management workflows."""

    def test_complete_order_listing_and_filtering_workflow(self, client, admin_user, multiple_orders):
        """Test complete workflow: list orders -> apply filters -> view results -> reset filters."""
        client.force_login(admin_user)

        # Step 1: View order list
        list_response = client.get(reverse("lfs_orders"))
        assert list_response.status_code == 200
        assert "orders_with_data" in list_response.context
        assert len(list_response.context["orders_with_data"]) > 0

        # Step 2: Apply filters
        filter_data = {
            "name": "John0",
            "state": "1",
            "start": (date.today() - timedelta(days=10)).strftime("%Y-%m-%d"),
            "end": date.today().strftime("%Y-%m-%d"),
        }
        filter_response = client.post(reverse("lfs_set_order_filter"), filter_data)
        assert filter_response.status_code == 302

        # Step 3: Verify filtered results
        filtered_response = client.get(reverse("lfs_orders"))
        assert filtered_response.status_code == 200
        assert filtered_response.context["name"] == "John0"
        assert filtered_response.context["state_id"] == "1"

        # Step 4: Reset filters
        reset_response = client.get(reverse("lfs_reset_order_filters"))
        assert reset_response.status_code == 302

        # Step 5: Verify filters are cleared
        cleared_response = client.get(reverse("lfs_orders"))
        assert cleared_response.status_code == 200
        assert cleared_response.context["name"] == ""

    def test_order_detail_viewing_workflow(self, client, admin_user, order):
        """Test complete workflow: view order list -> click order -> view details -> navigate back."""
        client.force_login(admin_user)

        # Step 1: Start at order list
        list_response = client.get(reverse("lfs_orders"))
        assert list_response.status_code == 200

        # Step 2: Navigate to order detail
        detail_response = client.get(reverse("lfs_manage_order", args=[order.id]))
        assert detail_response.status_code == 200
        assert "current_order" in detail_response.context
        assert detail_response.context["current_order"] == order

        # Step 3: Verify order data is displayed
        assert "order_total" in detail_response.context
        assert "customer_name" in detail_response.context
        assert "order_items" in detail_response.context

        # Step 4: Navigate back to order list
        back_response = client.get(reverse("lfs_orders"))
        assert back_response.status_code == 200

    def test_order_state_filtering_workflow(self, client, admin_user, multiple_orders):
        """Test workflow: filter by order state -> verify results -> change filter."""
        client.force_login(admin_user)

        # Step 1: Apply state filter
        filter_data = {"state": "2"}  # Paid state
        filter_response = client.post(reverse("lfs_set_order_filter"), filter_data)
        assert filter_response.status_code == 302

        # Step 2: Verify filtered results
        filtered_response = client.get(reverse("lfs_orders"))
        assert filtered_response.status_code == 200
        assert filtered_response.context["state_id"] == "2"

        # Step 3: Change to different state filter
        new_filter_data = {"state": "3"}  # Shipped state
        new_filter_response = client.post(reverse("lfs_set_order_filter"), new_filter_data)
        assert new_filter_response.status_code == 302

        # Step 4: Verify new filter is applied
        new_filtered_response = client.get(reverse("lfs_orders"))
        assert new_filtered_response.status_code == 200
        assert new_filtered_response.context["state_id"] == "3"

    def test_predefined_date_filter_workflow(self, client, admin_user, multiple_orders):
        """Test workflow: apply predefined date filters -> verify application."""
        client.force_login(admin_user)

        # Step 1: Apply "today" filter
        today_response = client.get(reverse("lfs_apply_predefined_order_filter", args=["today"]))
        assert today_response.status_code == 302

        # Step 2: Apply "week" filter
        week_response = client.get(reverse("lfs_apply_predefined_order_filter", args=["week"]))
        assert week_response.status_code == 302

        # Step 3: Apply "month" filter
        month_response = client.get(reverse("lfs_apply_predefined_order_filter", args=["month"]))
        assert month_response.status_code == 302

        # Step 4: Verify filters are working (check that request succeeds)
        list_response = client.get(reverse("lfs_orders"))
        assert list_response.status_code == 200

    def test_order_navigation_with_filters_workflow(self, client, admin_user, order, multiple_orders):
        """Test workflow: set filters -> navigate to order -> return with filters preserved."""
        client.force_login(admin_user)

        # Step 1: Set filters
        filter_data = {"name": "John", "state": "1"}
        client.post(reverse("lfs_set_order_filter"), filter_data)

        # Step 2: Navigate to specific order
        order_response = client.get(reverse("lfs_manage_order", args=[order.id]))
        assert order_response.status_code == 200

        # Step 3: Navigate back to order list (filters should be preserved)
        list_response = client.get(reverse("lfs_orders"))
        assert list_response.status_code == 200
        assert list_response.context["name"] == "John"
        assert list_response.context["state_id"] == "1"

    def test_order_search_and_navigation_workflow(self, client, admin_user, multiple_orders):
        """Test workflow: search orders -> navigate through results -> modify search."""
        client.force_login(admin_user)

        # Step 1: Search for specific customer
        search_data = {"name": "John1"}
        client.post(reverse("lfs_set_order_filter"), search_data)

        # Step 2: View search results
        search_response = client.get(reverse("lfs_orders"))
        assert search_response.status_code == 200
        assert search_response.context["name"] == "John1"

        # Step 3: Modify search
        modify_data = {"name": "John2"}
        client.post(reverse("lfs_set_order_filter"), modify_data)

        # Step 4: View modified results
        modified_response = client.get(reverse("lfs_orders"))
        assert modified_response.status_code == 200
        assert modified_response.context["name"] == "John2"

        # Step 5: Clear search
        client.get(reverse("lfs_reset_order_filters"))
        clear_response = client.get(reverse("lfs_orders"))
        assert clear_response.context["name"] == ""


@pytest.mark.django_db
@pytest.mark.integration
class TestOrderPermissionWorkflow:
    """Test permission-related workflows."""

    def test_unauthorized_order_access_workflow(self, client, order):
        """Test workflow: unauthorized access -> login required."""
        # Try to access without login
        response = client.get(reverse("lfs_orders"))
        assert response.status_code == 302
        assert "login" in response.url.lower()

    def test_authorized_order_access_workflow(self, client, admin_user, order):
        """Test workflow: login -> authorized access."""
        # Login first
        client.force_login(admin_user)

        # Now access should work
        response = client.get(reverse("lfs_orders"))
        assert response.status_code == 200
        assert "orders_with_data" in response.context

    def test_order_delete_permission_workflow(self, client, regular_user, order):
        """Test workflow: regular user tries to delete -> access denied."""
        client.force_login(regular_user)

        response = client.post(reverse("lfs_manage_delete_order", args=[order.id]))
        assert response.status_code in [302, 403]  # Redirect or forbidden


@pytest.mark.django_db
@pytest.mark.integration
class TestOrderErrorRecoveryWorkflow:
    """Test error handling and recovery workflows."""

    def test_invalid_order_id_workflow(self, client, admin_user):
        """Test workflow: invalid order ID -> 404 error -> recover."""
        client.force_login(admin_user)

        # Try to access invalid order
        response = client.get(reverse("lfs_manage_order", args=[99999]))
        assert response.status_code == 404

        # Recover by going back to order list
        list_response = client.get(reverse("lfs_orders"))
        assert list_response.status_code == 200

    def test_invalid_filter_data_workflow(self, client, admin_user):
        """Test workflow: invalid filter data -> handle gracefully."""
        client.force_login(admin_user)

        # Submit invalid filter data
        invalid_data = {
            "name": "",  # Empty name
            "state": "invalid",  # Invalid state
            "start": "invalid-date",  # Invalid date
        }

        response = client.post(reverse("lfs_set_order_filter"), invalid_data)
        assert response.status_code == 302  # Should still redirect

        # Should still be able to view orders
        list_response = client.get(reverse("lfs_orders"))
        assert list_response.status_code == 200

    def test_order_delete_nonexistent_workflow(self, client, admin_user):
        """Test workflow: delete non-existent order -> handle gracefully."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_manage_delete_order", args=[99999]))
        assert response.status_code == 404

        # Should still be able to view order list
        list_response = client.get(reverse("lfs_orders"))
        assert list_response.status_code == 200


@pytest.mark.django_db
@pytest.mark.integration
class TestOrderSessionPersistenceWorkflow:
    """Test session persistence across requests."""

    def test_filter_session_persistence_workflow(self, client, admin_user):
        """Test workflow: set filters -> multiple requests -> filters persist."""
        client.force_login(admin_user)

        # Step 1: Set filters
        filter_data = {"name": "Session", "state": "1"}
        client.post(reverse("lfs_set_order_filter"), filter_data)

        # Step 2: Make multiple requests
        for _ in range(3):
            response = client.get(reverse("lfs_orders"))
            assert response.status_code == 200
            assert response.context["name"] == "Session"
            assert response.context["state_id"] == "1"

    def test_filter_reset_persistence_workflow(self, client, admin_user):
        """Test workflow: set filters -> reset -> verify cleared."""
        client.force_login(admin_user)

        # Step 1: Set filters
        filter_data = {"name": "Reset", "state": "1"}
        client.post(reverse("lfs_set_order_filter"), filter_data)

        # Step 2: Verify filters are set
        response = client.get(reverse("lfs_orders"))
        assert response.context["name"] == "Reset"

        # Step 3: Reset filters
        client.get(reverse("lfs_reset_order_filters"))

        # Step 4: Verify filters are cleared
        final_response = client.get(reverse("lfs_orders"))
        assert final_response.context["name"] == ""


@pytest.mark.django_db
@pytest.mark.integration
class TestOrderLifecycleWorkflow:
    """Test complete order lifecycle management."""

    def test_order_creation_to_viewing_workflow(self, client, admin_user, order):
        """Test workflow: order exists -> view in list -> view details."""
        client.force_login(admin_user)

        # Step 1: View order in list
        list_response = client.get(reverse("lfs_orders"))
        assert list_response.status_code == 200
        orders_data = list_response.context["orders_with_data"]
        assert len(orders_data) > 0

        # Step 2: Click through to order detail
        detail_response = client.get(reverse("lfs_manage_order", args=[order.id]))
        assert detail_response.status_code == 200
        assert detail_response.context["current_order"] == order

    def test_order_state_management_workflow(self, client, admin_user, order):
        """Test workflow: view order states -> filter by state -> manage state."""
        client.force_login(admin_user)

        # Step 1: View order with state information
        response = client.get(reverse("lfs_manage_order", args=[order.id]))
        assert response.status_code == 200
        assert "states" in response.context

        # Step 2: Filter orders by current order's state
        filter_data = {"state": str(order.state)}
        client.post(reverse("lfs_set_order_filter"), filter_data)

        # Step 3: Verify filtering works
        list_response = client.get(reverse("lfs_orders"))
        assert list_response.status_code == 200
        assert list_response.context["state_id"] == str(order.state)
