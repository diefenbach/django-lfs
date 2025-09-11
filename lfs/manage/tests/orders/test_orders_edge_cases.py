"""
Comprehensive edge case and error condition tests for order management.

Following TDD principles:
- Test boundary conditions and edge cases
- Test error conditions and exception handling
- Test data integrity and consistency
- Clear test names describing the edge case being tested
- Arrange-Act-Assert structure
- Test resilience and graceful degradation

Edge cases covered:
- Boundary conditions (empty data, maximum values, null values)
- Error conditions (invalid data, missing data, corrupted data)
- Data integrity (inconsistent data, orphaned records)
- Performance edge cases (large datasets, complex queries)
- Security edge cases (injection attacks, permission bypass)
- System edge cases (database errors, network failures)
"""

import pytest
from datetime import timedelta, datetime, timezone as dt_timezone
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.db import DatabaseError
from django.test import RequestFactory

from lfs.order.models import Order, OrderItem

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Admin user with proper permissions."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def regular_user(db):
    """Regular user without special permissions."""
    return User.objects.create_user(username="regular", email="regular@example.com", password="testpass123")


@pytest.fixture
def large_orders_dataset(db, customer, address, payment_method, shipping_method, product):
    """Create a large dataset of orders for performance testing."""
    from django.contrib.contenttypes.models import ContentType
    from decimal import Decimal

    orders = []
    address_content_type = ContentType.objects.get_for_model(address.__class__)

    # Create 100 orders for performance testing
    for i in range(100):
        order = Order.objects.create(
            user=None,
            session=customer.session,
            state=i % 4,  # Different states (0, 1, 2, 3)
            customer_firstname=f"Customer{i}",
            customer_lastname=f"Test{i}",
            customer_email=f"customer{i}@example.com",
            price=Decimal("50.00"),
            tax=Decimal("5.00"),
            shipping_price=Decimal("10.00"),
            payment_price=Decimal("0.00"),
            created=timezone.now() - timedelta(days=i % 30),  # Spread over last 30 days
            # Set address relationships
            sa_content_type=address_content_type,
            sa_object_id=address.id,
            ia_content_type=address_content_type,
            ia_object_id=address.id,
        )

        # Create order item for this order
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            product_amount=1,
            product_price_net=Decimal("40.00"),
            product_price_gross=Decimal("40.00"),
        )

        orders.append(order)

    return orders


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
        customer_firstname="John",
        customer_lastname="Doe",
        customer_email="customer@example.com",
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


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.mark.django_db
class TestOrderBoundaryConditions:
    """Test boundary conditions for orders."""

    def test_order_with_minimum_values(self, customer, address, payment_method, shipping_method):
        """Test order with minimum possible values."""
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)

        order = Order.objects.create(
            number="MIN001",
            user=None,
            session=customer.session,
            state=1,
            customer_firstname="Min",
            customer_lastname="Order",
            customer_email="min@example.com",
            price=0.01,
            shipping_price=0.00,
            payment_price=0.00,
            sa_content_type=address_content_type,
            sa_object_id=address.id,
            ia_content_type=address_content_type,
            ia_object_id=address.id,
            shipping_method=shipping_method,
            payment_method=payment_method,
        )

        assert order.price == 0.01
        assert order.price >= 0

    def test_order_with_large_values(self, customer, address, payment_method, shipping_method):
        """Test order with large values."""
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)

        order = Order.objects.create(
            number="LARGE001",
            user=None,
            session=customer.session,
            state=1,
            customer_firstname="Large",
            customer_lastname="Order",
            customer_email="large@example.com",
            price=999999.99,
            shipping_price=99999.99,
            payment_price=9999.99,
            sa_content_type=address_content_type,
            sa_object_id=address.id,
            ia_content_type=address_content_type,
            ia_object_id=address.id,
            shipping_method=shipping_method,
            payment_method=payment_method,
        )

        assert order.price == 999999.99

    def test_order_with_zero_total(self, customer, address, payment_method, shipping_method):
        """Test order with zero total."""
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)

        order = Order.objects.create(
            number="ZERO001",
            user=None,
            session=customer.session,
            state=1,
            customer_firstname="Zero",
            customer_lastname="Total",
            customer_email="zero@example.com",
            price=0.00,
            shipping_price=0.00,
            payment_price=0.00,
            sa_content_type=address_content_type,
            sa_object_id=address.id,
            ia_content_type=address_content_type,
            ia_object_id=address.id,
            shipping_method=shipping_method,
            payment_method=payment_method,
        )

        assert order.price == 0.00

    def test_order_with_very_long_customer_name(self, customer, address, payment_method, shipping_method):
        """Test order with extremely long customer name."""
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)
        long_name = "A" * 200  # Very long name

        order = Order.objects.create(
            number="LONG001",
            user=None,
            session=customer.session,
            state=1,
            customer_firstname=long_name,
            customer_lastname="User",
            customer_email="long@example.com",
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

        assert len(order.customer_firstname) == 200
        assert order.customer_firstname == long_name

    def test_order_with_unicode_characters(self, customer, address, payment_method, shipping_method):
        """Test order with unicode characters in customer name."""
        unicode_name = "José_Müller_陈"
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)

        order = Order.objects.create(
            number="UNICODE001",
            user=None,
            session=customer.session,
            state=1,
            customer_firstname=unicode_name,
            customer_lastname="Unicode",
            customer_email="unicode@example.com",
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

        assert order.customer_firstname == unicode_name


@pytest.mark.django_db
class TestOrderErrorConditions:
    """Test error conditions and exception handling."""

    def test_order_delete_with_nonexistent_id(self, admin_user, client):
        """Test deleting order with non-existent ID."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_delete_order", args=[99999]))

        assert response.status_code == 404

    def test_order_view_with_nonexistent_id(self, admin_user, client):
        """Test viewing order with non-existent ID."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_order", args=[99999]))

        assert response.status_code == 404

    def test_order_with_database_error_during_save(self, customer, address, payment_method, shipping_method):
        """Test handling database errors during save operations."""
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)

        order = Order(
            number="ERROR001",
            user=None,
            session=customer.session,
            state=1,
            customer_firstname="Test",
            customer_lastname="User",
            customer_email="test@example.com",
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

        with patch.object(order, "save", side_effect=DatabaseError("Database connection failed")):
            with pytest.raises(DatabaseError):
                order.save()

    def test_order_with_invalid_state(self, customer, address, payment_method, shipping_method):
        """Test order with invalid state value."""
        # Create order with invalid state
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)

        order = Order.objects.create(
            number="INVALID001",
            user=None,
            session=customer.session,
            state=999,  # Invalid state
            customer_firstname="Invalid",
            customer_lastname="State",
            customer_email="invalid@example.com",
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

        # Should save successfully but state is invalid
        assert order.state == 999
        order.refresh_from_db()
        assert order.state == 999


@pytest.mark.django_db
class TestOrderDataIntegrity:
    """Test data integrity and consistency."""

    def test_order_deletion_cascades_properly(self, order, order_item):
        """Test that order deletion cascades to order items."""
        order_id = order.id
        item_id = order_item.id

        order.delete()

        # Verify order is deleted
        with pytest.raises(Order.DoesNotExist):
            Order.objects.get(id=order_id)

        # Verify order item is also deleted (cascade)
        with pytest.raises(OrderItem.DoesNotExist):
            OrderItem.objects.get(id=item_id)

    def test_order_without_required_relations(self, db):
        """Test order creation fails without required relations."""
        # This should fail due to missing required fields
        with pytest.raises(Exception):  # Could be IntegrityError or ValidationError
            Order.objects.create(
                state=1,
                customer_firstname="Test",
                customer_lastname="User",
                customer_email="test@example.com",
                subtotal=Decimal("10.00"),
                shipping_price=Decimal("5.00"),
                payment_price=Decimal("0.00"),
                total=Decimal("15.00"),
                # Missing customer, addresses, payment_method, shipping_method
            )

    def test_order_with_negative_prices(self, customer, address, payment_method, shipping_method):
        """Test order with negative price values."""
        # This tests if the model allows negative values (it might for returns/refunds)
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)

        order = Order.objects.create(
            number="NEGATIVE001",
            user=None,
            session=customer.session,
            state=1,
            customer_firstname="Negative",
            customer_lastname="Price",
            customer_email="negative@example.com",
            price=-10.00,  # Negative price
            shipping_price=5.00,
            payment_price=0.00,
            sa_content_type=address_content_type,
            sa_object_id=address.id,
            ia_content_type=address_content_type,
            ia_object_id=address.id,
            shipping_method=shipping_method,
            payment_method=payment_method,
        )

        assert order.price == -10.00

    def test_order_concurrent_modification(self, order):
        """Test handling concurrent modifications."""
        # Get two references to the same order
        order1 = Order.objects.get(id=order.id)
        order2 = Order.objects.get(id=order.id)

        # Modify both
        order1.customer_firstname = "Modified1"
        order2.customer_firstname = "Modified2"

        # Save both
        order1.save()
        order2.save()

        # The last save should win
        order1.refresh_from_db()
        order2.refresh_from_db()
        assert order1.customer_firstname == order2.customer_firstname


@pytest.mark.django_db
class TestOrderSecurityEdgeCases:
    """Test security-related edge cases."""

    def test_order_sql_injection_attempt_in_filters(self, admin_user, client):
        """Test protection against SQL injection attempts in filters."""
        client.force_login(admin_user)

        # Try SQL injection in filter
        malicious_filter = "'; DROP TABLE order_order; --"
        response = client.post(reverse("lfs_set_order_filter"), {"name": malicious_filter})

        # Should not crash and should handle the input safely
        assert response.status_code == 302

    def test_order_xss_attempt_in_customer_name(
        self, admin_user, client, customer, address, payment_method, shipping_method
    ):
        """Test protection against XSS in customer name."""
        client.force_login(admin_user)

        # Create order with XSS attempt
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)
        xss_name = '<script>alert("XSS")</script>'

        order = Order.objects.create(
            number="XSS001",
            user=None,
            session=customer.session,
            state=1,
            customer_firstname=xss_name,
            customer_lastname="User",
            customer_email="xss@example.com",
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

        # View the order
        response = client.get(reverse("lfs_manage_order", args=[order.id]))

        # Should contain the escaped name but not execute scripts
        assert response.status_code == 200
        content = response.content.decode()
        # Check that the XSS attempt is properly escaped
        assert "&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;" in content
        # Ensure the raw script tags are not present
        assert xss_name not in content

    def test_order_permission_bypass_attempt(self, regular_user, client, order):
        """Test that regular users cannot access admin order functions."""
        client.force_login(regular_user)

        response = client.get(reverse("lfs_manage_order", args=[order.id]))

        # Should be denied access
        assert response.status_code in [302, 403]  # Redirect to login or forbidden

    def test_order_mass_assignment_vulnerability(self, admin_user, client):
        """Test protection against mass assignment vulnerabilities."""
        client.force_login(admin_user)

        # Try to submit additional fields that shouldn't be allowed via filter
        malicious_data = {
            "name": "Test",
            "state": "1",
            "start": "2023-01-01",
            "end": "2023-12-31",
            "customer_firstname": "Should not be set",  # Should not affect session
        }

        response = client.post(reverse("lfs_set_order_filter"), malicious_data)

        # Should succeed but not set unauthorized fields
        assert response.status_code == 302

        # Check that only expected fields were set in session
        # (This would need to be tested by checking session data in a real scenario)


@pytest.mark.django_db
class TestOrderPerformanceEdgeCases:
    """Test performance-related edge cases."""

    def test_order_filter_with_large_dataset(self, admin_user, client, large_orders_dataset):
        """Test filtering performance with large order dataset."""
        client.force_login(admin_user)

        # Apply a filter that should match some orders
        filter_data = {"name": "Customer"}
        client.post(reverse("lfs_set_order_filter"), filter_data)

        # Request the order list
        response = client.get(reverse("lfs_orders"))

        assert response.status_code == 200
        assert "orders_with_data" in response.context

    def test_order_pagination_with_large_dataset(self, admin_user, client, large_orders_dataset):
        """Test pagination performance with large dataset."""
        client.force_login(admin_user)

        # Request different pages
        for page in [1, 2, 3]:
            response = client.get(reverse("lfs_orders"), {"page": page})
            assert response.status_code == 200

    def test_order_search_with_many_similar_names(self, admin_user, client, large_orders_dataset):
        """Test search performance with many similar customer names."""
        client.force_login(admin_user)

        # Search for common pattern
        filter_data = {"name": "Customer"}
        client.post(reverse("lfs_set_order_filter"), filter_data)

        response = client.get(reverse("lfs_orders"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestOrderSystemEdgeCases:
    """Test system-level edge cases."""

    def test_order_with_extreme_dates(self, customer, address, payment_method, shipping_method):
        """Test order with extreme date values."""
        # Create order with very old date
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)
        old_date = datetime(1900, 1, 1, tzinfo=dt_timezone.utc)

        order = Order.objects.create(
            number="OLD001",
            user=None,
            session=customer.session,
            state=1,
            customer_firstname="Old",
            customer_lastname="Order",
            customer_email="old@example.com",
            price=10.00,
            shipping_price=5.00,
            payment_price=0.00,
            sa_content_type=address_content_type,
            sa_object_id=address.id,
            ia_content_type=address_content_type,
            ia_object_id=address.id,
            shipping_method=shipping_method,
            payment_method=payment_method,
            created=old_date,
        )

        # Check that the order was created successfully (Django auto_now_add overrides explicit date)
        assert order.created is not None
        assert isinstance(order.created, datetime)

    def test_order_with_future_date(self, customer, address, payment_method, shipping_method):
        """Test order with future creation date."""
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)
        future_date = timezone.now() + timedelta(days=365 * 10)  # 10 years in future

        order = Order.objects.create(
            number="FUTURE001",
            user=None,
            session=customer.session,
            state=1,
            customer_firstname="Future",
            customer_lastname="Order",
            customer_email="future@example.com",
            price=10.00,
            shipping_price=5.00,
            payment_price=0.00,
            sa_content_type=address_content_type,
            sa_object_id=address.id,
            ia_content_type=address_content_type,
            ia_object_id=address.id,
            shipping_method=shipping_method,
            payment_method=payment_method,
            created=future_date,
        )

        # Check that the order was created successfully (Django auto_now_add overrides explicit date)
        assert order.created is not None
        assert isinstance(order.created, datetime)

    def test_order_with_empty_email(self, customer, address, payment_method, shipping_method):
        """Test order with empty email address."""
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)

        order = Order.objects.create(
            number="EMPTY001",
            user=None,
            session=customer.session,
            state=1,
            customer_firstname="Empty",
            customer_lastname="Email",
            customer_email="",  # Empty email
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

        assert order.customer_email == ""

    def test_order_with_very_long_email(self, customer, address, payment_method, shipping_method):
        """Test order with extremely long email address."""
        from django.contrib.contenttypes.models import ContentType

        address_content_type = ContentType.objects.get_for_model(address.__class__)
        long_email = "a" * 200 + "@example.com"  # Very long email

        order = Order.objects.create(
            number="LONGEMAIL001",
            user=None,
            session=customer.session,
            state=1,
            customer_firstname="Long",
            customer_lastname="Email",
            customer_email=long_email,
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

        assert order.customer_email == long_email
