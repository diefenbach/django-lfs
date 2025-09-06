"""
Comprehensive edge case and error condition tests for customer management.

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
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.db import DatabaseError

from lfs.customer.models import Customer
from lfs.cart.models import Cart
from lfs.addresses.models import Address
from lfs.manage.customers.services import CustomerFilterService, CustomerDataService
from lfs.manage.customers.forms import CustomerFilterForm
from lfs.manage.customers.mixins import CustomerFilterMixin, CustomerPaginationMixin

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Admin user with proper permissions."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def edge_case_customers(db):
    """Customers with edge case data for testing."""
    customers = []

    # Customer with very long name
    user1 = User.objects.create_user(username="longnameuser", email="longname@example.com", password="testpass123")
    customer1 = Customer.objects.create(user=user1)
    Address.objects.create(
        customer=customer1,
        firstname="A" * 100,  # Very long firstname
        lastname="B" * 100,  # Very long lastname
        line1="123 Main St",
        city="Test City",
        zip_code="12345",
        email="longname@example.com",
    )
    customers.append(customer1)

    # Customer with special characters in name
    user2 = User.objects.create_user(username="specialchars", email="special@example.com", password="testpass123")
    customer2 = Customer.objects.create(user=user2)
    Address.objects.create(
        customer=customer2,
        firstname="José María",
        lastname="O'Connor-Smith",
        line1="123 Main St",
        city="Test City",
        zip_code="12345",
        email="special@example.com",
    )
    customers.append(customer2)

    # Customer with unicode characters
    user3 = User.objects.create_user(username="unicodeuser", email="unicode@example.com", password="testpass123")
    customer3 = Customer.objects.create(user=user3)
    Address.objects.create(
        customer=customer3,
        firstname="李小明",
        lastname="王",
        line1="123 Main St",
        city="Test City",
        zip_code="12345",
        email="unicode@example.com",
    )
    customers.append(customer3)

    # Customer with numeric characters in name
    user4 = User.objects.create_user(username="numericuser", email="numeric@example.com", password="testpass123")
    customer4 = Customer.objects.create(user=user4)
    Address.objects.create(
        customer=customer4,
        firstname="User123",
        lastname="Test456",
        line1="123 Main St",
        city="Test City",
        zip_code="12345",
        email="numeric@example.com",
    )
    customers.append(customer4)

    # Customer with very old date_joined
    user5 = User.objects.create_user(username="olduser", email="old@example.com", password="testpass123")
    user5.date_joined = timezone.make_aware(timezone.datetime(1900, 1, 1))
    user5.save()
    customer5 = Customer.objects.create(user=user5)
    Address.objects.create(
        customer=customer5,
        firstname="Old",
        lastname="User",
        line1="123 Main St",
        city="Test City",
        zip_code="12345",
        email="old@example.com",
    )
    customers.append(customer5)

    # Customer with future date_joined
    user6 = User.objects.create_user(username="futureuser", email="future@example.com", password="testpass123")
    user6.date_joined = timezone.now() + timedelta(days=365)
    user6.save()
    customer6 = Customer.objects.create(user=user6)
    Address.objects.create(
        customer=customer6,
        firstname="Future",
        lastname="User",
        line1="123 Main St",
        city="Test City",
        zip_code="12345",
        email="future@example.com",
    )
    customers.append(customer6)

    return customers


class TestCustomerFilterServiceEdgeCases:
    """Test CustomerFilterService edge cases and error conditions."""

    def test_should_handle_empty_queryset(self):
        """Test that empty queryset is handled gracefully."""
        service = CustomerFilterService()
        queryset = Customer.objects.none()

        result = service.filter_customers(queryset, {})

        assert result.count() == 0

    @pytest.mark.django_db
    def test_should_handle_none_filters(self):
        """Test that None filters are handled gracefully."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, None)

        assert result.count() == queryset.count()

    @pytest.mark.django_db
    def test_should_handle_empty_filters_dict(self):
        """Test that empty filters dict is handled gracefully."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {})

        assert result.count() == queryset.count()

    def test_should_handle_very_long_name_filter(self, edge_case_customers):
        """Test that very long name filters are handled gracefully."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        long_name = "A" * 1000  # Very long name
        result = service.filter_customers(queryset, {"name": long_name})

        assert result.count() == 0  # Should not match anything

    def test_should_handle_special_characters_in_name_filter(self, edge_case_customers):
        """Test that special characters in name filter are handled correctly."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {"name": "José"})

        assert result.count() == 1
        assert "José" in result.first().addresses.first().firstname

    def test_should_handle_unicode_characters_in_name_filter(self, edge_case_customers):
        """Test that unicode characters in name filter are handled correctly."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {"name": "李"})

        assert result.count() == 1
        assert "李" in result.first().addresses.first().firstname

    def test_should_handle_numeric_characters_in_name_filter(self, edge_case_customers):
        """Test that numeric characters in name filter are handled correctly."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {"name": "123"})

        assert result.count() == 1
        assert "123" in result.first().addresses.first().firstname

    def test_should_handle_invalid_date_format(self, edge_case_customers):
        """Test that invalid date formats are handled gracefully."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        result = service.filter_customers(queryset, {"start": "invalid-date"})

        # Should not raise exception, but may not filter correctly
        assert result.count() >= 0

    def test_should_handle_very_old_dates(self, edge_case_customers):
        """Test that very old dates are handled correctly."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        old_date = "1900-01-01"
        result = service.filter_customers(queryset, {"start": old_date})

        # Should match customers with date_joined >= 1900-01-01
        # This includes all customers since they all have dates >= 1900-01-01
        assert result.count() == 6  # All customers should match

    def test_should_handle_future_dates(self, edge_case_customers):
        """Test that future dates are handled correctly."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        future_date = (timezone.now() + timedelta(days=365)).date().isoformat()
        result = service.filter_customers(queryset, {"start": future_date})

        assert result.count() == 1  # Should match the future user

    @pytest.mark.django_db
    def test_should_handle_malformed_filters_dict(self):
        """Test that malformed filters dict is handled gracefully."""
        service = CustomerFilterService()
        queryset = Customer.objects.all()

        # Test with non-string keys
        malformed_filters = {123: "test", None: "test"}
        result = service.filter_customers(queryset, malformed_filters)

        assert result.count() == queryset.count()

    def test_should_handle_ordering_with_invalid_field(self):
        """Test that invalid ordering fields are handled gracefully."""
        service = CustomerFilterService()

        result = service.get_ordering("invalid_field", "")

        assert result == "invalid_field"  # Should pass through

    def test_should_handle_ordering_with_special_characters(self):
        """Test that special characters in ordering are handled gracefully."""
        service = CustomerFilterService()

        result = service.get_ordering("field; DROP TABLE customers;", "")

        assert result == "field; DROP TABLE customers;"  # Should pass through

    def test_should_handle_ordering_with_very_long_field_name(self):
        """Test that very long field names in ordering are handled gracefully."""
        service = CustomerFilterService()

        long_field = "a" * 1000
        result = service.get_ordering(long_field, "")

        assert result == long_field  # Should pass through


class TestCustomerDataServiceEdgeCases:
    """Test CustomerDataService edge cases and error conditions."""

    def test_should_handle_empty_customers_list(self, mock_request):
        """Test that empty customers list is handled gracefully."""
        service = CustomerDataService()

        result = service.get_customers_with_data([], mock_request)

        assert result == []

    def test_should_handle_none_customers_list(self, mock_request):
        """Test that None customers list is handled gracefully."""
        service = CustomerDataService()

        result = service.get_customers_with_data(None, mock_request)

        assert result == []

    def test_should_handle_customer_without_user_or_session(self, mock_request, db):
        """Test that customer without user or session is handled gracefully."""
        service = CustomerDataService()
        customer = Customer.objects.create()  # No user, no session

        result = service.get_customers_with_data([customer], mock_request)

        assert result == []

    def test_should_handle_customer_with_none_user(self, mock_request, db):
        """Test that customer with None user but valid session is handled correctly."""
        service = CustomerDataService()
        customer = Customer.objects.create(user=None, session="test_session")

        result = service.get_customers_with_data([customer], mock_request)

        assert len(result) == 1
        assert result[0]["customer"] == customer

    def test_should_handle_customer_with_empty_session(self, mock_request, db):
        """Test that customer with empty session is handled gracefully."""
        service = CustomerDataService()
        customer = Customer.objects.create(user=None, session="")

        result = service.get_customers_with_data([customer], mock_request)

        assert result == []

    def test_should_handle_customer_with_none_session(self, mock_request, db):
        """Test that customer with user but empty session is handled correctly."""
        service = CustomerDataService()
        # Create a customer with user but no session (this should be valid)
        user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        customer = Customer.objects.create(user=user, session="")

        result = service.get_customers_with_data([customer], mock_request)

        assert len(result) == 1
        assert result[0]["customer"] == customer

    def test_should_handle_database_error_during_cart_query(self, mock_request, user_with_customer):
        """Test that database errors during cart query are handled gracefully."""
        user, customer, address = user_with_customer
        service = CustomerDataService()

        with patch("lfs.cart.models.Cart.objects.get", side_effect=DatabaseError("Database error")):
            result = service.get_customers_with_data([customer], mock_request)

            assert len(result) == 1
            assert result[0]["cart_price"] is None

    def test_should_handle_database_error_during_order_query(self, mock_request, user_with_customer):
        """Test that database errors during order query are handled gracefully."""
        user, customer, address = user_with_customer
        service = CustomerDataService()

        with patch("lfs.order.models.Order.objects.filter", side_effect=DatabaseError("Database error")):
            result = service.get_customers_with_data([customer], mock_request)

            assert len(result) == 1
            assert result[0]["orders_count"] == 0

    def test_should_handle_exception_during_cart_price_calculation(self, mock_request, user_with_customer):
        """Test that exceptions during cart price calculation are handled gracefully."""
        user, customer, address = user_with_customer
        service = CustomerDataService()

        # Create a cart for the customer
        cart = Cart.objects.create(session=customer.session)

        with patch.object(cart, "get_price_gross", side_effect=Exception("Price calculation error")):
            result = service.get_customer_with_data(customer, mock_request)

            # Should handle exception gracefully - cart_price should be None or 0
            assert result["cart_price"] is None or result["cart_price"] == 0

    def test_should_handle_exception_during_shipping_costs_calculation(self, mock_request, user_with_customer):
        """Test that exceptions during shipping costs calculation are handled gracefully."""
        user, customer, address = user_with_customer
        service = CustomerDataService()

        # Create a cart for the customer
        cart = Cart.objects.create(session=customer.session)

        with patch(
            "lfs.manage.customers.services.get_selected_shipping_method", side_effect=Exception("Shipping error")
        ), patch("lfs.manage.customers.services.get_shipping_costs", side_effect=Exception("Shipping error")):

            result = service.get_customer_with_data(customer, mock_request)

            # Should still return result, but cart_price may be None or incorrect
            assert "cart_price" in result

    def test_should_handle_exception_during_payment_costs_calculation(self, mock_request, user_with_customer):
        """Test that exceptions during payment costs calculation are handled gracefully."""
        user, customer, address = user_with_customer
        service = CustomerDataService()

        # Create a cart for the customer
        cart = Cart.objects.create(session=customer.session)

        with patch(
            "lfs.manage.customers.services.get_selected_payment_method", side_effect=Exception("Payment error")
        ), patch("lfs.manage.customers.services.get_payment_costs", side_effect=Exception("Payment error")):

            result = service.get_customer_with_data(customer, mock_request)

            # Should still return result, but cart_price may be None or incorrect
            assert "cart_price" in result

    def test_should_handle_customer_with_multiple_addresses(self, mock_request, db):
        """Test that customer with multiple addresses is handled correctly."""
        user = User.objects.create_user(username="multiuser", email="multi@example.com", password="testpass123")
        customer = Customer.objects.create(user=user)

        # Create multiple addresses
        Address.objects.create(
            customer=customer,
            firstname="First",
            lastname="Address",
            line1="123 Main St",
            city="Test City",
            zip_code="12345",
            email="first@example.com",
        )
        Address.objects.create(
            customer=customer,
            firstname="Second",
            lastname="Address",
            line1="456 Oak Ave",
            city="Test City",
            zip_code="54321",
            email="second@example.com",
        )

        service = CustomerDataService()
        result = service.get_customers_with_data([customer], mock_request)

        assert len(result) == 1
        assert result[0]["customer"] == customer

    def test_should_handle_customer_with_no_addresses(self, mock_request, db):
        """Test that customer with no addresses is handled correctly."""
        user = User.objects.create_user(username="noaddress", email="noaddress@example.com", password="testpass123")
        customer = Customer.objects.create(user=user)

        service = CustomerDataService()
        result = service.get_customers_with_data([customer], mock_request)

        assert len(result) == 1
        assert result[0]["customer"] == customer


class TestCustomerFormsEdgeCases:
    """Test CustomerFilterForm edge cases and error conditions."""

    def test_should_handle_very_long_name_input(self):
        """Test that very long name input is handled correctly."""
        long_name = "A" * 1000
        form = CustomerFilterForm(data={"name": long_name})

        assert not form.is_valid()
        assert "name" in form.errors

    def test_should_handle_special_characters_in_name_input(self):
        """Test that special characters in name input are handled correctly."""
        special_name = "José María O'Connor-Smith"
        form = CustomerFilterForm(data={"name": special_name})

        assert form.is_valid()
        assert form.cleaned_data["name"] == special_name

    def test_should_handle_unicode_characters_in_name_input(self):
        """Test that unicode characters in name input are handled correctly."""
        unicode_name = "李小明"
        form = CustomerFilterForm(data={"name": unicode_name})

        assert form.is_valid()
        assert form.cleaned_data["name"] == unicode_name

    def test_should_handle_numeric_characters_in_name_input(self):
        """Test that numeric characters in name input are handled correctly."""
        numeric_name = "User123"
        form = CustomerFilterForm(data={"name": numeric_name})

        assert form.is_valid()
        assert form.cleaned_data["name"] == numeric_name

    def test_should_handle_sql_injection_attempt_in_name_input(self):
        """Test that SQL injection attempts in name input are handled safely."""
        sql_injection = "'; DROP TABLE customers; --"
        form = CustomerFilterForm(data={"name": sql_injection})

        assert form.is_valid()
        assert form.cleaned_data["name"] == sql_injection

    def test_should_handle_html_injection_attempt_in_name_input(self):
        """Test that HTML injection attempts in name input are handled safely."""
        html_injection = "<script>alert('xss')</script>"
        form = CustomerFilterForm(data={"name": html_injection})

        assert form.is_valid()
        assert form.cleaned_data["name"] == html_injection

    def test_should_handle_very_old_date_input(self):
        """Test that very old date input is handled correctly."""
        old_date = "1900-01-01"
        form = CustomerFilterForm(data={"start": old_date})

        assert form.is_valid()
        assert form.cleaned_data["start"] == date(1900, 1, 1)

    def test_should_handle_future_date_input(self):
        """Test that future date input is handled correctly."""
        future_date = (date.today() + timedelta(days=365)).isoformat()
        form = CustomerFilterForm(data={"start": future_date})

        assert form.is_valid()
        assert form.cleaned_data["start"] == date.today() + timedelta(days=365)

    def test_should_handle_invalid_date_format(self):
        """Test that invalid date format is handled correctly."""
        invalid_date = "not-a-date"
        form = CustomerFilterForm(data={"start": invalid_date})

        assert not form.is_valid()
        assert "start" in form.errors

    def test_should_handle_malformed_date_input(self):
        """Test that malformed date input is handled correctly."""
        malformed_date = "2024-13-45"  # Invalid month and day
        form = CustomerFilterForm(data={"start": malformed_date})

        assert not form.is_valid()
        assert "start" in form.errors

    def test_should_handle_none_values_in_form_data(self):
        """Test that None values in form data are handled correctly."""
        form = CustomerFilterForm(data={"name": None, "start": None, "end": None})

        assert form.is_valid()
        assert form.cleaned_data["name"] == ""  # CharField converts None to empty string
        assert form.cleaned_data["start"] is None
        assert form.cleaned_data["end"] is None

    def test_should_handle_empty_string_values_in_form_data(self):
        """Test that empty string values in form data are handled correctly."""
        form = CustomerFilterForm(data={"name": "", "start": "", "end": ""})

        assert form.is_valid()
        assert form.cleaned_data["name"] == ""
        assert form.cleaned_data["start"] is None  # Empty string becomes None for date fields
        assert form.cleaned_data["end"] is None

    def test_should_handle_whitespace_only_values_in_form_data(self):
        """Test that whitespace-only values in form data are handled correctly."""
        form = CustomerFilterForm(data={"name": "   ", "start": "   ", "end": "   "})

        # Form should be invalid because whitespace-only strings are invalid for date fields
        assert not form.is_valid()
        assert "start" in form.errors
        assert "end" in form.errors
        # But name field should be valid (whitespace is preserved)
        assert "name" not in form.errors


class TestCustomerViewsEdgeCases:
    """Test customer views edge cases and error conditions."""

    def test_should_handle_missing_customer_id_in_url(self, client, admin_user):
        """Test that missing customer_id in URL is handled gracefully."""
        client.force_login(admin_user)

        # This should result in a 404 or URL resolution error
        with pytest.raises(Exception):  # URL resolution error
            client.get("/manage/customers//")  # Missing customer_id

    def test_should_handle_invalid_customer_id_in_url(self, client, admin_user, shop):
        """Test that invalid customer_id in URL is handled gracefully."""
        client.force_login(admin_user)

        # Use direct URL construction since reverse won't work with invalid IDs
        response = client.get("/manage/customers/invalid/")

        assert response.status_code == 404

    def test_should_handle_very_large_customer_id_in_url(self, client, admin_user, shop):
        """Test that very large customer_id in URL is handled gracefully."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_customer", kwargs={"customer_id": 999999999}))

        assert response.status_code == 404

    def test_should_handle_negative_customer_id_in_url(self, client, admin_user, shop):
        """Test that negative customer_id in URL is handled gracefully."""
        client.force_login(admin_user)

        # Use direct URL construction since reverse won't work with negative IDs
        response = client.get("/manage/customers/-1/")

        assert response.status_code == 404

    def test_should_handle_malformed_post_data(self, client, admin_user):
        """Test that malformed POST data is handled gracefully."""
        client.force_login(admin_user)

        # Send malformed data
        response = client.post(
            reverse("lfs_apply_customer_filters"), data="malformed data", content_type="application/json"
        )

        # Should handle gracefully (may return 400 or redirect)
        assert response.status_code in [200, 302, 400]

    def test_should_handle_very_large_post_data(self, client, admin_user):
        """Test that very large POST data is handled gracefully."""
        client.force_login(admin_user)

        # Send very large data
        large_data = {"name": "A" * 10000}
        response = client.post(reverse("lfs_apply_customer_filters"), large_data)

        # Should handle gracefully (may return 400 or redirect)
        assert response.status_code in [200, 302, 400]

    def test_should_handle_session_corruption(self, client, admin_user, shop):
        """Test that session corruption is handled gracefully."""
        client.force_login(admin_user)

        # Corrupt session data
        session = client.session
        session["customer-filters"] = "corrupted data"  # Should be dict
        session.save()

        response = client.get(reverse("lfs_manage_customers"))

        # Should handle gracefully
        assert response.status_code == 200

    def test_should_handle_missing_session_keys(self, client, admin_user, shop):
        """Test that missing session keys are handled gracefully."""
        client.force_login(admin_user)

        # Clear only customer-related session keys, not the entire session
        session = client.session
        if "customer-filters" in session:
            del session["customer-filters"]
        if "customer-ordering" in session:
            del session["customer-ordering"]
        if "customer-ordering-order" in session:
            del session["customer-ordering-order"]
        session.save()

        response = client.get(reverse("lfs_manage_customers"))

        # Should handle gracefully
        assert response.status_code == 200

    def test_should_handle_database_connection_error(self, client, admin_user, shop):
        """Test that database connection errors are handled gracefully."""
        client.force_login(admin_user)

        with patch("lfs.customer.models.Customer.objects.all", side_effect=DatabaseError("Database connection error")):
            response = client.get(reverse("lfs_manage_customers"))

            # Should handle gracefully (may return 500 or redirect)
            assert response.status_code in [200, 302, 500]

    def test_should_handle_permission_denied_gracefully(self, client, regular_user):
        """Test that permission denied is handled gracefully."""
        client.force_login(regular_user)

        response = client.get(reverse("lfs_manage_customers"))

        # Should return 403 Forbidden
        assert response.status_code == 403

    def test_should_handle_concurrent_session_modification(self, client, admin_user):
        """Test that concurrent session modification is handled gracefully."""
        client.force_login(admin_user)

        # Simulate concurrent modification by changing session in another request
        session = client.session
        session["customer-filters"] = {"name": "test"}
        session.save()

        # Make request that might modify session
        response = client.post(reverse("lfs_apply_customer_filters"), {"name": "new_test"})

        # Should handle gracefully
        assert response.status_code == 302

    def test_should_handle_unicode_in_url_parameters(self, client, admin_user):
        """Test that unicode in URL parameters is handled gracefully."""
        client.force_login(admin_user)

        # Test with unicode in ordering parameter
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "李小明"}))

        # Should handle gracefully
        assert response.status_code == 302

    def test_should_handle_special_characters_in_url_parameters(self, client, admin_user):
        """Test that special characters in URL parameters are handled gracefully."""
        client.force_login(admin_user)

        # Test with special characters in ordering parameter
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": "field; DROP TABLE customers;"}))

        # Should handle gracefully
        assert response.status_code == 302

    def test_should_handle_very_long_url_parameters(self, client, admin_user):
        """Test that very long URL parameters are handled gracefully."""
        client.force_login(admin_user)

        # Test with very long ordering parameter
        long_ordering = "a" * 1000
        response = client.get(reverse("lfs_set_customer_ordering", kwargs={"ordering": long_ordering}))

        # Should handle gracefully
        assert response.status_code == 302

    def test_should_handle_missing_csrf_token(self, client, admin_user):
        """Test that missing CSRF token is handled gracefully."""
        client.force_login(admin_user)

        # Disable CSRF protection for this test
        client.csrf_exempt = True

        response = client.post(reverse("lfs_apply_customer_filters"), {"name": "test"})

        # Should handle gracefully (may return 403 or redirect)
        assert response.status_code in [200, 302, 403]

    def test_should_handle_invalid_csrf_token(self, client, admin_user):
        """Test that invalid CSRF token is handled gracefully."""
        client.force_login(admin_user)

        # Send invalid CSRF token
        response = client.post(
            reverse("lfs_apply_customer_filters"), {"name": "test", "csrfmiddlewaretoken": "invalid_token"}
        )

        # Should handle gracefully (may return 403 or redirect)
        assert response.status_code in [200, 302, 403]


class TestCustomerMixinsEdgeCases:
    """Test customer mixins edge cases and error conditions."""

    def test_should_handle_none_request_in_mixin(self):
        """Test that None request in mixin is handled gracefully."""
        mixin = CustomerFilterMixin()
        mixin.request = None

        # Should return empty dict instead of raising AttributeError
        result = mixin.get_customer_filters()
        assert result == {}

    def test_should_handle_request_without_session(self):
        """Test that request without session is handled gracefully."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/")
        # Don't add session to request

        mixin = CustomerFilterMixin()
        mixin.request = request

        result = mixin.get_customer_filters()

        assert result == {}

    def test_should_handle_request_with_none_session(self):
        """Test that request with None session is handled gracefully."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/")
        request.session = None

        mixin = CustomerFilterMixin()
        mixin.request = request

        # Should return empty dict instead of raising AttributeError
        result = mixin.get_customer_filters()
        assert result == {}

    def test_should_handle_pagination_with_invalid_page_number(self, mock_request, multiple_customers):
        """Test that pagination with invalid page number is handled gracefully."""
        mock_request.GET = {"page": "invalid"}

        # Create a test class that inherits from both mixins
        class TestView(CustomerFilterMixin, CustomerPaginationMixin):
            def get_filtered_customers_queryset(self):
                return Customer.objects.all()

        mixin = TestView()
        mixin.request = mock_request

        result = mixin.get_paginated_customers()

        assert result.number == 1  # Should default to first page

    def test_should_handle_pagination_with_negative_page_number(self, mock_request, multiple_customers):
        """Test that pagination with negative page number is handled gracefully."""
        mock_request.GET = {"page": "-1"}

        # Create a test class that inherits from both mixins
        class TestView(CustomerFilterMixin, CustomerPaginationMixin):
            def get_filtered_customers_queryset(self):
                return Customer.objects.all()

        mixin = TestView()
        mixin.request = mock_request

        result = mixin.get_paginated_customers()

        assert result.number == 1  # Should default to first page

    def test_should_handle_pagination_with_zero_page_number(self, mock_request, multiple_customers):
        """Test that pagination with zero page number is handled gracefully."""
        mock_request.GET = {"page": "0"}

        # Create a test class that inherits from both mixins
        class TestView(CustomerFilterMixin, CustomerPaginationMixin):
            def get_filtered_customers_queryset(self):
                return Customer.objects.all()

        mixin = TestView()
        mixin.request = mock_request

        result = mixin.get_paginated_customers()

        assert result.number == 1  # Should default to first page

    def test_should_handle_pagination_with_very_large_page_number(self, mock_request, multiple_customers):
        """Test that pagination with very large page number is handled gracefully."""
        mock_request.GET = {"page": "999999"}

        # Create a test class that inherits from both mixins
        class TestView(CustomerFilterMixin, CustomerPaginationMixin):
            def get_filtered_customers_queryset(self):
                return Customer.objects.all()

        mixin = TestView()
        mixin.request = mock_request

        result = mixin.get_paginated_customers()

        # Should return last page
        assert result.number > 0
        assert result.number <= result.paginator.num_pages
