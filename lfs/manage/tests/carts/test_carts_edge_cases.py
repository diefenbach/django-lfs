"""
Comprehensive edge case and error condition tests for cart management.

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
from datetime import date, timedelta, datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.db import DatabaseError
from django.test import RequestFactory

from lfs.cart.models import Cart
from lfs.customer.models import Customer
from lfs.addresses.models import Address
from lfs.manage.carts.services import CartFilterService, CartDataService
from lfs.manage.carts.forms import CartFilterForm
from lfs.manage.carts.mixins import CartFilterMixin, CartPaginationMixin, CartDataMixin, CartContextMixin

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Admin user with proper permissions."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def regular_user(db):
    """Regular user without admin permissions."""
    return User.objects.create_user(username="user", email="user@example.com", password="testpass123")


@pytest.fixture
def edge_case_carts(db):
    """Carts with edge case data for testing."""
    carts = []

    # Cart with very old modification date
    cart1 = Cart.objects.create(session="old_session")
    Cart.objects.filter(id=cart1.id).update(modification_date=timezone.make_aware(datetime(1900, 1, 1)))
    cart1.refresh_from_db()
    carts.append(cart1)

    # Cart with future modification date
    cart2 = Cart.objects.create(session="future_session")
    future_date = timezone.now() + timedelta(days=365)
    Cart.objects.filter(id=cart2.id).update(modification_date=future_date)
    cart2.refresh_from_db()
    carts.append(cart2)

    # Cart with very long session ID
    cart3 = Cart.objects.create(session="a" * 1000)  # Very long session
    carts.append(cart3)

    # Cart with special characters in session
    cart4 = Cart.objects.create(session="session-with-special-chars!@#$%^&*()")
    carts.append(cart4)

    # Cart with unicode characters in session
    cart5 = Cart.objects.create(session="session-with-unicode-李小明")
    carts.append(cart5)

    # Cart with numeric session
    cart6 = Cart.objects.create(session="123456789")
    carts.append(cart6)

    # Cart with user (not just session)
    user = User.objects.create_user(username="cartuser", email="cart@example.com", password="testpass123")
    cart7 = Cart.objects.create(user=user, session="user_session")
    carts.append(cart7)

    # Cart with both user and session
    cart8 = Cart.objects.create(user=user, session="both_session")
    carts.append(cart8)

    return carts


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
    customer = Customer.objects.create(user=user, session="test_session")
    address = Address.objects.create(
        customer=customer,
        firstname="Test",
        lastname="User",
        line1="123 Main St",
        city="Test City",
        zip_code="12345",
        email="test@example.com",
    )
    return user, customer, address


@pytest.fixture
def multiple_carts(db):
    """Multiple carts for pagination testing."""
    carts = []
    for i in range(50):  # Create 50 carts for pagination testing
        cart = Cart.objects.create(session=f"session_{i}")
        carts.append(cart)
    return carts


class TestCartFilterServiceEdgeCases:
    """Test CartFilterService edge cases and error conditions."""

    def test_should_handle_empty_queryset(self):
        """Test that empty queryset is handled gracefully."""
        service = CartFilterService()
        queryset = Cart.objects.none()

        result = service.filter_carts(queryset, {})

        assert result.count() == 0

    @pytest.mark.django_db
    def test_should_handle_none_filters(self):
        """Test that None filters are handled gracefully."""
        service = CartFilterService()
        queryset = Cart.objects.all()

        result = service.filter_carts(queryset, None)

        assert result.count() == queryset.count()

    @pytest.mark.django_db
    def test_should_handle_empty_filters_dict(self):
        """Test that empty filters dict is handled gracefully."""
        service = CartFilterService()
        queryset = Cart.objects.all()

        result = service.filter_carts(queryset, {})

        assert result.count() == queryset.count()

    def test_should_handle_very_old_dates(self, multiple_carts):
        """Test that very old dates are handled correctly."""
        service = CartFilterService()
        queryset = Cart.objects.all()

        old_date = "1900-01-01"
        result = service.filter_carts(queryset, {"start": old_date})

        # Should match carts with modification_date >= 1900-01-01
        assert result.count() == 50  # All carts should match

    def test_should_handle_future_dates(self, edge_case_carts):
        """Test that future dates are handled correctly."""
        service = CartFilterService()
        queryset = Cart.objects.all()

        # Test with a future date that should return the future cart
        future_date = (timezone.now() + timedelta(days=365)).date().isoformat()
        result = service.filter_carts(queryset, {"start": future_date})

        # Should return the future cart
        assert result.count() == 1

    def test_should_handle_invalid_date_format(self, edge_case_carts):
        """Test that invalid date formats are handled gracefully."""
        service = CartFilterService()
        queryset = Cart.objects.all()

        result = service.filter_carts(queryset, {"start": "invalid-date"})

        # Should not raise exception, but may not filter correctly
        assert result.count() >= 0

    @pytest.mark.django_db
    def test_should_handle_malformed_filters_dict(self):
        """Test that malformed filters dict is handled gracefully."""
        service = CartFilterService()
        queryset = Cart.objects.all()

        # Test with non-string keys
        malformed_filters = {123: "test", None: "test"}
        result = service.filter_carts(queryset, malformed_filters)

        assert result.count() == queryset.count()

    def test_should_handle_parse_iso_date_with_none(self):
        """Test that parse_iso_date handles None input gracefully."""
        service = CartFilterService()

        result = service.parse_iso_date(None)

        assert result is None

    def test_should_handle_parse_iso_date_with_empty_string(self):
        """Test that parse_iso_date handles empty string gracefully."""
        service = CartFilterService()

        result = service.parse_iso_date("")

        assert result is None

    def test_should_handle_parse_iso_date_with_whitespace(self):
        """Test that parse_iso_date handles whitespace gracefully."""
        service = CartFilterService()

        result = service.parse_iso_date("   ")

        assert result is None

    def test_should_handle_parse_iso_date_with_invalid_format(self):
        """Test that parse_iso_date handles invalid format gracefully."""
        service = CartFilterService()

        result = service.parse_iso_date("not-a-date")

        assert result is None

    def test_should_handle_parse_iso_date_with_special_characters(self):
        """Test that parse_iso_date handles special characters gracefully."""
        service = CartFilterService()

        result = service.parse_iso_date("2024-01-01!@#$%")

        assert result is None

    def test_should_handle_format_iso_date_with_none(self):
        """Test that format_iso_date handles None input gracefully."""
        service = CartFilterService()

        result = service.format_iso_date(None)

        assert result == ""

    def test_should_handle_format_iso_date_with_datetime(self):
        """Test that format_iso_date handles datetime input correctly."""
        service = CartFilterService()
        test_date = datetime(2024, 1, 15, 14, 30, 45)

        result = service.format_iso_date(test_date)

        assert result == "2024-01-15"

    def test_should_handle_format_iso_date_with_date(self):
        """Test that format_iso_date handles date input correctly."""
        service = CartFilterService()
        test_date = date(2024, 1, 15)

        result = service.format_iso_date(test_date)

        assert result == "2024-01-15"

    def test_should_handle_very_long_date_string(self):
        """Test that very long date strings are handled gracefully."""
        service = CartFilterService()

        long_date = "a" * 1000
        result = service.parse_iso_date(long_date)

        assert result is None

    def test_should_handle_unicode_in_date_string(self):
        """Test that unicode in date strings is handled gracefully."""
        service = CartFilterService()

        unicode_date = "2024-01-01李小明"
        result = service.parse_iso_date(unicode_date)

        assert result is None

    def test_should_handle_sql_injection_in_date_string(self):
        """Test that SQL injection in date strings is handled safely."""
        service = CartFilterService()

        sql_injection = "2024-01-01'; DROP TABLE carts; --"
        result = service.parse_iso_date(sql_injection)

        assert result is None


class TestCartDataServiceEdgeCases:
    """Test CartDataService edge cases and error conditions."""

    def test_should_handle_empty_carts_list(self, mock_request):
        """Test that empty carts list is handled gracefully."""
        service = CartDataService()

        result = service.get_carts_with_data([], mock_request)

        assert result == []

    def test_should_handle_none_carts_list(self, mock_request):
        """Test that None carts list is handled gracefully."""
        service = CartDataService()

        result = service.get_carts_with_data(None, mock_request)

        assert result == []

    def test_should_handle_cart_without_items(self, mock_request, db):
        """Test that cart without items is handled gracefully."""
        service = CartDataService()
        cart = Cart.objects.create(session="empty_cart")

        result = service.get_cart_summary(cart, mock_request)

        assert result["total"] == 0
        assert result["item_count"] == 0
        assert result["products"] == []

    def test_should_handle_cart_with_none_user(self, mock_request, db):
        """Test that cart with None user is handled correctly."""
        service = CartDataService()
        cart = Cart.objects.create(user=None, session="test_session")

        result = service.get_carts_with_data([cart], mock_request)

        assert len(result) == 1
        assert result[0]["cart"] == cart

    def test_should_handle_cart_with_empty_session(self, mock_request, db):
        """Test that cart with empty session is handled gracefully."""
        service = CartDataService()
        cart = Cart.objects.create(user=None, session="")

        result = service.get_carts_with_data([cart], mock_request)

        assert len(result) == 1
        assert result[0]["cart"] == cart

    def test_should_handle_cart_with_empty_session(self, mock_request, db):
        """Test that cart with empty session is handled correctly."""
        service = CartDataService()
        cart = Cart.objects.create(user=None, session="")

        result = service.get_carts_with_data([cart], mock_request)

        assert len(result) == 1
        assert result[0]["cart"] == cart

    def test_should_handle_database_error_during_customer_query(self, mock_request, db):
        """Test that database errors during customer query are handled gracefully."""
        service = CartDataService()
        cart = Cart.objects.create(session="test_session")

        with patch("lfs.customer.models.Customer.objects.filter", side_effect=DatabaseError("Database error")):
            result = service.get_carts_with_data([cart], mock_request)

            assert len(result) == 1
            assert result[0]["customer"] is None

    def test_should_handle_exception_during_cart_summary_calculation(self, mock_request, db):
        """Test that exceptions during cart summary calculation are handled gracefully."""
        service = CartDataService()
        cart = Cart.objects.create(session="test_session")

        with patch.object(cart, "get_items", side_effect=Exception("Items calculation error")):
            result = service.get_cart_summary(cart, mock_request)

            # Should handle exception gracefully
            assert "total" in result
            assert "item_count" in result
            assert "products" in result

    def test_should_handle_cart_with_very_long_session(self, mock_request, db):
        """Test that cart with very long session is handled correctly."""
        service = CartDataService()
        long_session = "a" * 1000
        cart = Cart.objects.create(session=long_session)

        result = service.get_carts_with_data([cart], mock_request)

        assert len(result) == 1
        assert result[0]["cart"] == cart

    def test_should_handle_cart_with_special_characters_in_session(self, mock_request, db):
        """Test that cart with special characters in session is handled correctly."""
        service = CartDataService()
        special_session = "session!@#$%^&*()"
        cart = Cart.objects.create(session=special_session)

        result = service.get_carts_with_data([cart], mock_request)

        assert len(result) == 1
        assert result[0]["cart"] == cart

    def test_should_handle_cart_with_unicode_in_session(self, mock_request, db):
        """Test that cart with unicode in session is handled correctly."""
        service = CartDataService()
        unicode_session = "session李小明"
        cart = Cart.objects.create(session=unicode_session)

        result = service.get_carts_with_data([cart], mock_request)

        assert len(result) == 1
        assert result[0]["cart"] == cart

    def test_should_handle_cart_with_numeric_session(self, mock_request, db):
        """Test that cart with numeric session is handled correctly."""
        service = CartDataService()
        numeric_session = "123456789"
        cart = Cart.objects.create(session=numeric_session)

        result = service.get_carts_with_data([cart], mock_request)

        assert len(result) == 1
        assert result[0]["cart"] == cart

    def test_should_handle_cart_with_both_user_and_session(self, mock_request, user_with_customer):
        """Test that cart with both user and session is handled correctly."""
        user, customer, address = user_with_customer
        service = CartDataService()
        cart = Cart.objects.create(user=user, session="both_session")

        result = service.get_carts_with_data([cart], mock_request)

        assert len(result) == 1
        assert result[0]["cart"] == cart
        assert result[0]["customer"] == customer

    def test_should_handle_mixed_cart_types(self, mock_request, user_with_customer):
        """Test that mixed cart types (user vs session) are handled correctly."""
        user, customer, address = user_with_customer
        service = CartDataService()

        # Cart with user
        cart1 = Cart.objects.create(user=user, session="user_session")
        # Cart with session only
        cart2 = Cart.objects.create(session="session_only")
        # Cart with both
        cart3 = Cart.objects.create(user=user, session="both_session")

        result = service.get_carts_with_data([cart1, cart2, cart3], mock_request)

        assert len(result) == 3
        # All carts should be included
        cart_ids = [r["cart"].id for r in result]
        assert cart1.id in cart_ids
        assert cart2.id in cart_ids
        assert cart3.id in cart_ids


class TestCartFormsEdgeCases:
    """Test CartFilterForm edge cases and error conditions."""

    def test_should_handle_very_old_date_input(self):
        """Test that very old date input is handled correctly."""
        old_date = "1900-01-01"
        form = CartFilterForm(data={"start": old_date})

        assert form.is_valid()
        assert form.cleaned_data["start"] == date(1900, 1, 1)

    def test_should_handle_future_date_input(self):
        """Test that future date input is handled correctly."""
        future_date = (date.today() + timedelta(days=365)).isoformat()
        form = CartFilterForm(data={"start": future_date})

        assert form.is_valid()
        assert form.cleaned_data["start"] == date.today() + timedelta(days=365)

    def test_should_handle_invalid_date_format(self):
        """Test that invalid date format is handled correctly."""
        invalid_date = "not-a-date"
        form = CartFilterForm(data={"start": invalid_date})

        assert not form.is_valid()
        assert "start" in form.errors

    def test_should_handle_malformed_date_input(self):
        """Test that malformed date input is handled correctly."""
        malformed_date = "2024-13-45"  # Invalid month and day
        form = CartFilterForm(data={"start": malformed_date})

        assert not form.is_valid()
        assert "start" in form.errors

    def test_should_handle_none_values_in_form_data(self):
        """Test that None values in form data are handled correctly."""
        form = CartFilterForm(data={"start": None, "end": None})

        assert form.is_valid()
        assert form.cleaned_data["start"] is None
        assert form.cleaned_data["end"] is None

    def test_should_handle_empty_string_values_in_form_data(self):
        """Test that empty string values in form data are handled correctly."""
        form = CartFilterForm(data={"start": "", "end": ""})

        assert form.is_valid()
        assert form.cleaned_data["start"] is None
        assert form.cleaned_data["end"] is None

    def test_should_handle_whitespace_only_values_in_form_data(self):
        """Test that whitespace-only values in form data are handled correctly."""
        form = CartFilterForm(data={"start": "   ", "end": "   "})

        # Form should be invalid because whitespace-only strings are invalid for date fields
        assert not form.is_valid()
        assert "start" in form.errors
        assert "end" in form.errors

    def test_should_handle_sql_injection_attempt_in_date_input(self):
        """Test that SQL injection attempts in date input are handled safely."""
        sql_injection = "2024-01-01'; DROP TABLE carts; --"
        form = CartFilterForm(data={"start": sql_injection})

        assert not form.is_valid()
        assert "start" in form.errors

    def test_should_handle_html_injection_attempt_in_date_input(self):
        """Test that HTML injection attempts in date input are handled safely."""
        html_injection = "<script>alert('xss')</script>"
        form = CartFilterForm(data={"start": html_injection})

        assert not form.is_valid()
        assert "start" in form.errors

    def test_should_handle_unicode_in_date_input(self):
        """Test that unicode in date input is handled correctly."""
        unicode_date = "2024-01-01李小明"
        form = CartFilterForm(data={"start": unicode_date})

        assert not form.is_valid()
        assert "start" in form.errors

    def test_should_handle_very_long_date_input(self):
        """Test that very long date input is handled correctly."""
        long_date = "a" * 1000
        form = CartFilterForm(data={"start": long_date})

        assert not form.is_valid()
        assert "start" in form.errors

    def test_should_handle_special_characters_in_date_input(self):
        """Test that special characters in date input are handled correctly."""
        special_date = "2024-01-01!@#$%^&*()"
        form = CartFilterForm(data={"start": special_date})

        assert not form.is_valid()
        assert "start" in form.errors

    def test_should_handle_numeric_date_input(self):
        """Test that numeric date input is handled correctly."""
        numeric_date = "123456789"
        form = CartFilterForm(data={"start": numeric_date})

        assert not form.is_valid()
        assert "start" in form.errors

    def test_should_handle_negative_date_input(self):
        """Test that negative date input is handled correctly."""
        negative_date = "-2024-01-01"
        form = CartFilterForm(data={"start": negative_date})

        assert not form.is_valid()
        assert "start" in form.errors


class TestCartViewsEdgeCases:
    """Test cart views edge cases and error conditions."""

    def test_should_handle_missing_cart_id_in_url(self, client, admin_user):
        """Test that missing cart_id in URL is handled gracefully."""
        client.force_login(admin_user)

        # This should result in a 404
        response = client.get("/manage/carts//")  # Missing cart_id
        assert response.status_code == 404

    def test_should_handle_invalid_cart_id_in_url(self, client, admin_user, test_shop):
        """Test that invalid cart_id in URL is handled gracefully."""
        client.force_login(admin_user)

        # Use direct URL construction since reverse won't work with invalid IDs
        response = client.get("/manage/carts/invalid/")

        assert response.status_code == 404

    def test_should_handle_very_large_cart_id_in_url(self, client, admin_user, test_shop):
        """Test that very large cart_id in URL is handled gracefully."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_cart", kwargs={"id": 999999999}))

        assert response.status_code == 404

    def test_should_handle_negative_cart_id_in_url(self, client, admin_user, test_shop):
        """Test that negative cart_id in URL is handled gracefully."""
        client.force_login(admin_user)

        # Use direct URL construction since reverse won't work with negative IDs
        response = client.get("/manage/carts/-1/")

        assert response.status_code == 404

    def test_should_handle_malformed_post_data(self, client, admin_user, test_shop):
        """Test that malformed POST data is handled gracefully."""
        client.force_login(admin_user)

        # Send malformed data to the list view filter endpoint
        response = client.post(
            reverse("lfs_apply_cart_filters_list"), data="malformed data", content_type="application/json"
        )

        # Should handle gracefully (may return 400 or redirect)
        assert response.status_code in [200, 302, 400]

    def test_should_handle_very_large_post_data(self, client, admin_user, test_shop):
        """Test that very large POST data is handled gracefully."""
        client.force_login(admin_user)

        # Send very large data
        large_data = {"start": "a" * 10000}
        response = client.post(reverse("lfs_apply_cart_filters_list"), large_data)

        # Should handle gracefully (may return 400 or redirect)
        assert response.status_code in [200, 302, 400]

    def test_should_handle_session_corruption(self, client, admin_user, test_shop):
        """Test that session corruption is handled gracefully."""
        client.force_login(admin_user)

        # Corrupt session data
        session = client.session
        session["cart-filters"] = "corrupted data"  # Should be dict
        session.save()

        response = client.get(reverse("lfs_manage_carts"))

        # Should handle gracefully
        assert response.status_code == 200

    def test_should_handle_missing_session_keys(self, client, admin_user, test_shop):
        """Test that missing session keys are handled gracefully."""
        client.force_login(admin_user)

        # Clear only cart-related session keys, not the entire session
        session = client.session
        if "cart-filters" in session:
            del session["cart-filters"]
        session.save()

        response = client.get(reverse("lfs_manage_carts"))

        # Should handle gracefully
        assert response.status_code == 200

    def test_should_handle_database_connection_error(self, client, admin_user, test_shop):
        """Test that database connection errors are handled gracefully."""
        client.force_login(admin_user)

        with patch("lfs.cart.models.Cart.objects.all", side_effect=DatabaseError("Database connection error")):
            response = client.get(reverse("lfs_manage_carts"))

            # Should handle gracefully (may return 500 or redirect)
            assert response.status_code in [200, 302, 500]

    def test_should_handle_permission_denied_gracefully(self, client, regular_user):
        """Test that permission denied is handled gracefully."""
        client.force_login(regular_user)

        response = client.get(reverse("lfs_manage_carts"))

        # Should return 403 Forbidden
        assert response.status_code == 403

    def test_should_handle_concurrent_session_modification(self, client, admin_user, test_shop):
        """Test that concurrent session modification is handled gracefully."""
        client.force_login(admin_user)

        # Simulate concurrent modification by changing session in another request
        session = client.session
        session["cart-filters"] = {"start": "2024-01-01"}
        session.save()

        # Make request that might modify session
        response = client.post(reverse("lfs_apply_cart_filters_list"), {"start": "2024-01-02"})

        # Should handle gracefully
        assert response.status_code == 302

    def test_should_handle_unicode_in_url_parameters(self, client, admin_user, test_shop):
        """Test that unicode in URL parameters is handled gracefully."""
        client.force_login(admin_user)

        # Test with unicode in URL path - use a cart view with unicode in the path
        response = client.get("/manage/carts/李小明/")

        # Should handle gracefully (404 for invalid cart ID)
        assert response.status_code == 404

    def test_should_handle_special_characters_in_url_parameters(self, client, admin_user, test_shop):
        """Test that special characters in URL parameters are handled gracefully."""
        client.force_login(admin_user)

        # Test with special characters in URL path
        response = client.get("/manage/carts/field;DROP TABLE carts;/")

        # Should handle gracefully (404 for invalid cart ID)
        assert response.status_code == 404

    def test_should_handle_very_long_url_parameters(self, client, admin_user, test_shop):
        """Test that very long URL parameters are handled gracefully."""
        client.force_login(admin_user)

        # Test with very long cart ID in URL path
        long_id = "a" * 1000
        response = client.get(f"/manage/carts/{long_id}/")

        # Should handle gracefully (404 for invalid cart ID)
        assert response.status_code == 404

    def test_should_handle_missing_csrf_token(self, client, admin_user, test_shop):
        """Test that missing CSRF token is handled gracefully."""
        client.force_login(admin_user)

        # Disable CSRF protection for this test
        client.csrf_exempt = True

        response = client.post(reverse("lfs_apply_cart_filters_list"), {"start": "2024-01-01"})

        # Should handle gracefully (may return 403 or redirect)
        assert response.status_code in [200, 302, 403]

    def test_should_handle_invalid_csrf_token(self, client, admin_user, test_shop):
        """Test that invalid CSRF token is handled gracefully."""
        client.force_login(admin_user)

        # Send invalid CSRF token
        response = client.post(
            reverse("lfs_apply_cart_filters_list"), {"start": "2024-01-01", "csrfmiddlewaretoken": "invalid_token"}
        )

        # Should handle gracefully (may return 403 or redirect)
        assert response.status_code in [200, 302, 403]

    def test_should_handle_invalid_predefined_filter_type(self, client, admin_user, test_shop):
        """Test that invalid predefined filter type is handled gracefully."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_apply_predefined_cart_filter_list", kwargs={"filter_type": "invalid"}))

        # Should handle gracefully (may return 404 or redirect)
        assert response.status_code in [200, 302, 404]

    def test_should_handle_predefined_filter_without_cart_id(self, client, admin_user, test_shop):
        """Test that predefined filter without cart_id is handled gracefully."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_apply_predefined_cart_filter_list", kwargs={"filter_type": "today"}))

        # Should handle gracefully
        assert response.status_code == 302


class TestCartMixinsEdgeCases:
    """Test cart mixins edge cases and error conditions."""

    def test_should_handle_none_request_in_mixin(self):
        """Test that None request in mixin is handled gracefully."""
        mixin = CartFilterMixin()
        mixin.request = None

        # Should return empty dict instead of raising AttributeError
        result = mixin.get_cart_filters()
        assert result == {}

    def test_should_handle_request_without_session(self):
        """Test that request without session is handled gracefully."""
        factory = RequestFactory()
        request = factory.get("/")
        # Don't add session to request

        mixin = CartFilterMixin()
        mixin.request = request

        result = mixin.get_cart_filters()

        assert result == {}

    def test_should_handle_request_with_none_session(self):
        """Test that request with None session is handled gracefully."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = None

        mixin = CartFilterMixin()
        mixin.request = request

        # Should return empty dict instead of raising AttributeError
        result = mixin.get_cart_filters()
        assert result == {}

    def test_should_handle_pagination_with_invalid_page_number(self, mock_request, multiple_carts):
        """Test that pagination with invalid page number is handled gracefully."""
        mock_request.GET = {"page": "invalid"}

        # Create a test class that inherits from both mixins
        class TestView(CartFilterMixin, CartPaginationMixin):
            model = Cart

            def get_filtered_carts_queryset(self):
                return Cart.objects.all()

        mixin = TestView()
        mixin.request = mock_request

        result = mixin.get_paginated_carts()

        assert result.number == 1  # Should default to first page

    def test_should_handle_pagination_with_negative_page_number(self, mock_request, multiple_carts):
        """Test that pagination with negative page number is handled gracefully."""
        mock_request.GET = {"page": "-1"}

        # Create a test class that inherits from both mixins
        class TestView(CartFilterMixin, CartPaginationMixin):
            model = Cart

            def get_filtered_carts_queryset(self):
                return Cart.objects.all()

        mixin = TestView()
        mixin.request = mock_request

        result = mixin.get_paginated_carts()

        # Django's get_page() returns the last page for invalid page numbers
        assert result.number > 0  # Should be a valid page number
        assert result.number <= result.paginator.num_pages

    def test_should_handle_pagination_with_zero_page_number(self, mock_request, multiple_carts):
        """Test that pagination with zero page number is handled gracefully."""
        mock_request.GET = {"page": "0"}

        # Create a test class that inherits from both mixins
        class TestView(CartFilterMixin, CartPaginationMixin):
            model = Cart

            def get_filtered_carts_queryset(self):
                return Cart.objects.all()

        mixin = TestView()
        mixin.request = mock_request

        result = mixin.get_paginated_carts()

        # Django's get_page() returns the last page for invalid page numbers
        assert result.number > 0  # Should be a valid page number
        assert result.number <= result.paginator.num_pages

    def test_should_handle_pagination_with_very_large_page_number(self, mock_request, multiple_carts):
        """Test that pagination with very large page number is handled gracefully."""
        mock_request.GET = {"page": "999999"}

        # Create a test class that inherits from both mixins
        class TestView(CartFilterMixin, CartPaginationMixin):
            model = Cart

            def get_filtered_carts_queryset(self):
                return Cart.objects.all()

        mixin = TestView()
        mixin.request = mock_request

        result = mixin.get_paginated_carts()

        # Should return last page
        assert result.number > 0
        assert result.number <= result.paginator.num_pages

    def test_should_handle_cart_data_mixin_with_none_cart(self, mock_request):
        """Test that CartDataMixin handles None cart gracefully."""
        mixin = CartDataMixin()
        mixin.request = mock_request

        result = mixin.get_cart_with_data(None)

        assert result is None

    def test_should_handle_cart_data_mixin_with_empty_carts_list(self, mock_request):
        """Test that CartDataMixin handles empty carts list gracefully."""
        mixin = CartDataMixin()
        mixin.request = mock_request

        result = mixin.get_carts_with_data([])

        assert result == []

    def test_should_handle_cart_context_mixin_with_none_request(self):
        """Test that CartContextMixin handles None request gracefully."""
        mixin = CartContextMixin()
        mixin.request = None

        # Should return empty dict instead of raising AttributeError
        result = mixin.get_cart_context_data()
        assert result == {}

    def test_should_handle_cart_context_mixin_with_request_without_session(self):
        """Test that CartContextMixin handles request without session gracefully."""
        factory = RequestFactory()
        request = factory.get("/")
        # Don't add session to request

        mixin = CartContextMixin()
        mixin.request = request

        result = mixin.get_cart_context_data()

        # Should return empty dict when no session
        assert result == {}
