"""
Integration tests for order views with real database and HTTP requests.

Following TDD principles:
- Test real HTTP requests and responses
- Test complete request-response cycles
- Test template rendering with real context
- Test database operations in integration
- Clear test names describing the integration scenario
- Arrange-Act-Assert structure

Integration tests cover:
- Complete HTTP request/response cycles
- Template rendering with real data
- Form submission and validation
- Database persistence and retrieval
- Session and cookie handling
- Authentication and authorization
"""

import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.order.models import Order, OrderItem
from lfs.core.models import Shop

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
    from django.contrib.contenttypes.models import ContentType

    address_content_type = ContentType.objects.get_for_model(address.__class__)

    return Order.objects.create(
        number="TEST001",
        user=None,
        session=customer.session,
        state=1,  # Submitted state
        customer_firstname="Test",
        customer_lastname="Customer",
        customer_email="test@example.com",
        price=100.00,
        sa_content_type=address_content_type,
        sa_object_id=address.id,
        ia_content_type=address_content_type,
        ia_object_id=address.id,
        shipping_method=shipping_method,
        payment_method=payment_method,
    )


@pytest.fixture
def order_item(db, order, product):
    """Create a test order item."""
    return OrderItem.objects.create(
        order=order,
        product=product,
        product_name="Test Product",
        product_sku="TEST001",
        product_price_net=10.00,
        product_price_gross=10.00,
        product_amount=1,
        price_net=10.00,
        price_gross=10.00,
        tax=0.00,
    )


@pytest.fixture
def multiple_orders(db, customer, address, payment_method, shipping_method, product):
    """Create multiple orders for testing."""
    from django.contrib.contenttypes.models import ContentType

    address_content_type = ContentType.objects.get_for_model(address.__class__)
    orders = []

    for i in range(5):
        order = Order.objects.create(
            number=f"MULTI{i:03d}",
            user=None,
            session=customer.session,
            state=i + 1,  # Different states
            customer_firstname=f"John{i}",
            customer_lastname=f"Doe{i}",
            customer_email=f"john{i}@example.com",
            price=10.00,
            shipping_price=5.00,
            payment_price=0.00,
            sa_content_type=address_content_type,
            sa_object_id=address.id,
            ia_content_type=address_content_type,
            ia_object_id=address.id,
            shipping_method=shipping_method,
            payment_method=payment_method,
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name="Test Product",
            product_sku="TEST001",
            product_price_net=10.00,
            product_price_gross=10.00,
            product_amount=1,
            price_net=10.00,
            price_gross=10.00,
            tax=0.00,
        )
        orders.append(order)
    return orders


@pytest.fixture
def shop(db):
    """Create a test shop for individual tests."""
    return Shop.objects.create(
        name="Test Shop",
        shop_owner="Test Owner",
        from_email="test@example.com",
        notification_emails="test@example.com",
        description="Test shop description",
    )


@pytest.mark.django_db
@pytest.mark.integration
class TestOrderViewsIntegration:
    """Integration tests for order views."""

    def test_order_list_view_renders_correctly(self, client, admin_user, multiple_orders, shop):
        """Should render order list view correctly."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_orders"))

        assert response.status_code == 200
        assert "orders_with_data" in response.context
        assert "states" in response.context
        assert "page" in response.context
        assert len(response.context["orders_with_data"]) > 0

    def test_order_list_view_with_filters(self, client, admin_user, multiple_orders, shop):
        """Should render order list view with applied filters."""
        client.force_login(admin_user)

        # First apply filters
        filter_data = {
            "name": "John0",
            "state": "1",
        }
        client.post(reverse("lfs_set_order_filter"), filter_data)

        # Now check that the order list view shows the filters
        response = client.get(reverse("lfs_orders"))

        assert response.status_code == 200
        assert response.context["name"] == "John0"
        assert response.context["state_id"] == "1"

    def test_order_list_view_pagination(self, client, admin_user, multiple_orders, shop):
        """Should render order list view with pagination."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_orders"), {"page": 1})

        assert response.status_code == 200
        assert "page" in response.context
        assert hasattr(response.context["page"], "object_list")

    def test_order_data_view_renders_correctly(self, client, admin_user, order, order_item, shop):
        """Should render order data view correctly."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_order", args=[order.id]))

        assert response.status_code == 200
        assert "current_order" in response.context
        assert response.context["current_order"] == order
        assert "order_total" in response.context
        assert "customer_name" in response.context

    def test_order_data_view_with_sidebar_navigation(self, client, admin_user, multiple_orders, shop):
        """Should render order data view with sidebar navigation."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_order", args=[multiple_orders[0].id]))

        assert response.status_code == 200
        assert "orders_page" in response.context
        assert "states" in response.context
        assert len(response.context["states"]) > 0

    def test_apply_order_filters_view_success(self, client, admin_user, shop):
        """Should successfully apply order filters."""
        client.force_login(admin_user)

        filter_data = {
            "name": "Test Customer",
            "state": "1",
            "start": "2023-01-01",
            "end": "2023-12-31",
        }

        response = client.post(reverse("lfs_set_order_filter"), filter_data)

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

    def test_apply_order_filters_view_with_order_id(self, client, admin_user, order, shop):
        """Should apply filters and redirect to specific order."""
        client.force_login(admin_user)

        filter_data = {
            "name": "Test Customer",
            "state": "1",
            "order-id": order.id,
        }

        response = client.post(reverse("lfs_set_order_filter"), filter_data)

        assert response.status_code == 302
        assert f"/manage/order/{order.id}" in response.url

    def test_reset_order_filters_view_success(self, client, admin_user, shop):
        """Should successfully reset order filters."""
        client.force_login(admin_user)

        # First set some filters
        filter_data = {"name": "Test", "state": "1"}
        client.post(reverse("lfs_set_order_filter"), filter_data)

        # Now reset them
        response = client.get(reverse("lfs_reset_order_filters"))

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

    def test_apply_predefined_filter_today(self, client, admin_user, shop):
        """Should apply today filter successfully."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_apply_predefined_order_filter", kwargs={"filter_type": "today"}))

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

    def test_apply_predefined_filter_week(self, client, admin_user, shop):
        """Should apply week filter successfully."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_apply_predefined_order_filter", kwargs={"filter_type": "week"}))

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

    def test_apply_predefined_filter_month(self, client, admin_user, shop):
        """Should apply month filter successfully."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_apply_predefined_order_filter", kwargs={"filter_type": "month"}))

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

    def test_apply_predefined_filter_with_order_id(self, client, admin_user, order, shop):
        """Should apply predefined filter and redirect to specific order."""
        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_apply_predefined_order_filter", kwargs={"filter_type": "today"}), {"order_id": order.id}
        )

        assert response.status_code == 302
        assert f"/manage/order/{order.id}" in response.url

    def test_apply_predefined_filter_invalid_type(self, client, admin_user, shop):
        """Should handle invalid filter type gracefully."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_apply_predefined_order_filter", kwargs={"filter_type": "invalid"}))

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

    def test_order_delete_view_success(self, client, admin_user, order, shop):
        """Should successfully delete order."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_delete_order", args=[order.id]))

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

        # Verify order was deleted
        with pytest.raises(Order.DoesNotExist):
            Order.objects.get(id=order.id)

    def test_manage_orders_view_redirects_to_first_order(self, client, admin_user, order, shop):
        """Should redirect to first order when orders exist."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_orders"))

        assert response.status_code == 302
        assert f"/manage/order/{order.id}" in response.url

    def test_manage_orders_view_redirects_to_order_list_when_no_orders(self, client, admin_user, shop):
        """Should redirect to order list when no orders exist."""
        client.force_login(admin_user)

        # Delete all orders
        Order.objects.all().delete()

        response = client.get(reverse("lfs_manage_orders"))

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

    def test_orders_view_function_delegates_correctly(self, client, admin_user, multiple_orders, shop):
        """Should delegate orders_view function to OrderListView (redirects to first order if orders exist)."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_orders"))

        # Should redirect to the first order since multiple_orders exist
        assert response.status_code == 302
        # Check that it redirects to some order page (don't hardcode the ID since it may vary)
        assert "/manage/order/" in response.url

    def test_order_view_function_delegates_correctly(self, client, admin_user, order, shop):
        """Should delegate order_view function to OrderDataView."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_order", args=[order.id]))

        assert response.status_code == 200
        assert "current_order" in response.context
        assert response.context["current_order"] == order

    def test_order_views_permission_denied(self, client, order):
        """Should deny access to unauthorized users."""
        response = client.get(reverse("lfs_orders"))

        assert response.status_code == 302
        assert "login" in response.url.lower()

    def test_order_delete_view_permission_denied(self, client, order):
        """Should deny delete access to unauthorized users."""
        response = client.post(reverse("lfs_delete_order", args=[order.id]))

        assert response.status_code == 302
        assert "login" in response.url.lower()

    def test_order_filters_persist_across_requests(self, client, admin_user, shop):
        """Should persist filters across multiple requests."""
        client.force_login(admin_user)

        # Set filters
        filter_data = {"name": "Persistent", "state": "1"}
        client.post(reverse("lfs_set_order_filter"), filter_data)

        # Check first request
        response1 = client.get(reverse("lfs_orders"))
        assert response1.context["name"] == "Persistent"

        # Check second request (should still have filters)
        response2 = client.get(reverse("lfs_orders"))
        assert response2.context["name"] == "Persistent"

        # Reset filters
        client.get(reverse("lfs_reset_order_filters"))

        # Check filters are gone
        response3 = client.get(reverse("lfs_orders"))
        assert response3.context["name"] == ""

    def test_order_context_includes_filter_form(self, client, admin_user, shop):
        """Should include filter form in order context."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_orders"))

        assert response.status_code == 200
        assert "filter_form" in response.context
        form = response.context["filter_form"]
        assert hasattr(form, "fields")
        assert "name" in form.fields
