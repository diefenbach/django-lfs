"""
Tests for refactored cart management views.
"""

from django.contrib.auth.models import User
from django.urls import reverse

from lfs.cart.models import Cart
from lfs.manage.carts.services import CartFilterService


class TestUtilityFunctions:
    """Test utility functions for date parsing and formatting."""

    def setup_method(self):
        """Set up the service for each test."""
        self.service = CartFilterService()

    def test_parse_iso_date_with_empty_string(self):
        """Test parse_iso_date returns None for empty string."""
        result = self.service.parse_iso_date("")
        assert result is None

    def test_parse_iso_date_with_whitespace_string(self):
        """Test parse_iso_date returns None for whitespace-only string."""
        result = self.service.parse_iso_date("   ")
        assert result is None

    def test_parse_iso_date_with_none(self):
        """Test parse_iso_date returns None for None."""
        result = self.service.parse_iso_date(None)
        assert result is None

    def test_parse_iso_date_with_valid_iso_format(self):
        """Test parse_iso_date correctly parses valid ISO format dates."""
        from datetime import datetime

        # Test various valid ISO dates
        test_cases = [
            ("2023-01-01", datetime(2023, 1, 1)),
            ("2023-12-31", datetime(2023, 12, 31)),
            ("2000-02-29", datetime(2000, 2, 29)),  # Leap year
            ("1999-06-15", datetime(1999, 6, 15)),
            ("2024-03-08", datetime(2024, 3, 8)),
        ]

        for date_string, expected in test_cases:
            result = self.service.parse_iso_date(date_string)
            assert result == expected

    def test_parse_iso_date_with_invalid_format(self):
        """Test parse_iso_date returns None for invalid format."""
        invalid_formats = [
            "invalid-date-format",
            "2023/01/01",  # Wrong separator
            "01-01-2023",  # Wrong order
            "2023-13-01",  # Invalid month
            "2023-01-32",  # Invalid day
            "2023-00-01",  # Invalid month
            "2023-01-00",  # Invalid day
            "2023-02-30",  # Invalid day for February
            "abc-def-ghi",  # Non-numeric
            "2023-01-01T12:00:00",  # ISO datetime (not just date)
            "2023-01-01 12:00:00",  # Space separator
        ]

        for invalid_format in invalid_formats:
            result = self.service.parse_iso_date(invalid_format)
            assert result is None, f"Expected None for '{invalid_format}', got {result}"

    def test_parse_iso_date_with_edge_case_years(self):
        """Test parse_iso_date with edge case years."""
        from datetime import datetime

        # Test very old and very new years
        test_cases = [
            ("1900-01-01", datetime(1900, 1, 1)),
            ("9999-12-31", datetime(9999, 12, 31)),
            ("0001-01-01", datetime(1, 1, 1)),
        ]

        for date_string, expected in test_cases:
            result = self.service.parse_iso_date(date_string)
            assert result == expected

    def test_format_iso_date_with_none(self):
        """Test format_iso_date returns empty string for None."""
        result = self.service.format_iso_date(None)
        assert result == ""

    def test_format_iso_date_with_empty_string(self):
        """Test format_iso_date returns empty string for empty string."""
        result = self.service.format_iso_date("")
        assert result == ""

    def test_format_iso_date_with_falsy_values(self):
        """Test format_iso_date returns empty string for falsy values."""
        falsy_values = [None, "", 0, False, [], {}]

        for value in falsy_values:
            result = self.service.format_iso_date(value)
            assert result == "", f"Expected empty string for {value}, got '{result}'"

    def test_format_iso_date_with_valid_datetime_objects(self):
        """Test format_iso_date correctly formats valid datetime objects."""
        from datetime import datetime

        test_cases = [
            (datetime(2023, 1, 1), "2023-01-01"),
            (datetime(2023, 12, 31), "2023-12-31"),
            (datetime(2000, 2, 29), "2000-02-29"),  # Leap year
            (datetime(1999, 6, 15), "1999-06-15"),
            (datetime(2024, 3, 8), "2024-03-08"),
            (datetime(1900, 1, 1), "1900-01-01"),
            (datetime(9999, 12, 31), "9999-12-31"),
        ]

        for date_obj, expected in test_cases:
            result = self.service.format_iso_date(date_obj)
            assert result == expected, f"Expected '{expected}' for {date_obj}, got '{result}'"

    def test_format_iso_date_with_datetime_objects_with_time(self):
        """Test format_iso_date ignores time component and only formats date."""
        from datetime import datetime

        test_cases = [
            (datetime(2023, 1, 1, 12, 30, 45, 123456), "2023-01-01"),
            (datetime(2023, 12, 31, 23, 59, 59, 999999), "2023-12-31"),
            (datetime(2000, 2, 29, 0, 0, 0, 0), "2000-02-29"),
        ]

        for date_obj, expected in test_cases:
            result = self.service.format_iso_date(date_obj)
            assert result == expected, f"Expected '{expected}' for {date_obj}, got '{result}'"

    def test_format_iso_date_with_date_objects(self):
        """Test format_iso_date works with date objects (not just datetime)."""
        from datetime import date

        test_cases = [
            (date(2023, 1, 1), "2023-01-01"),
            (date(2023, 12, 31), "2023-12-31"),
            (date(2000, 2, 29), "2000-02-29"),
        ]

        for date_obj, expected in test_cases:
            result = self.service.format_iso_date(date_obj)
            assert result == expected, f"Expected '{expected}' for {date_obj}, got '{result}'"

    def test_round_trip_parsing_and_formatting(self):
        """Test that parse_iso_date and format_iso_date work together correctly."""
        from datetime import datetime

        # Test round-trip: format -> parse -> format should give same result
        test_dates = [
            datetime(2023, 1, 1),
            datetime(2023, 12, 31),
            datetime(2000, 2, 29),
            datetime(1999, 6, 15),
            datetime(2024, 3, 8),
        ]

        for original_date in test_dates:
            # Format the date
            formatted = self.service.format_iso_date(original_date)
            # Parse it back
            parsed = self.service.parse_iso_date(formatted)
            # Format the parsed date
            reformatted = self.service.format_iso_date(parsed)

            # Should get the same string back
            assert formatted == reformatted
            # Parsed date should have same date components (ignoring time)
            assert parsed.date() == original_date.date()

    def test_parse_iso_date_preserves_timezone_naive_datetime(self):
        """Test that parse_iso_date returns timezone-naive datetime objects."""
        from datetime import datetime

        result = self.service.parse_iso_date("2023-01-01")
        assert result is not None
        assert result.tzinfo is None  # Should be timezone-naive
        assert isinstance(result, datetime)


class TestCartListView:
    """Test CartListView functionality."""

    def test_cart_list_view_shows_cart_list(self, authenticated_client, test_carts):
        """Test that CartListView shows the cart list template."""
        response = authenticated_client.get(reverse("lfs_manage_carts"))
        # Should show cart list template, not redirect
        assert response.status_code == 200
        assert "carts_with_data" in response.context

    def test_cart_list_view_shows_empty_list_when_no_carts(self, authenticated_client):
        """Test that CartListView shows empty list when no carts exist."""
        Cart.objects.all().delete()
        response = authenticated_client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        assert len(response.context["carts_with_data"]) == 0

    def test_cart_list_view_with_actual_cart_items(self, authenticated_client, test_carts):
        """Test CartListView processes actual cart items to hit lines 115-117."""
        from lfs.catalog.models import Product
        from lfs.cart.models import CartItem

        cart1, cart2 = test_carts

        # Create actual products and cart items to ensure lines 115-117 are executed
        product = Product.objects.create(name="Test Product", slug="test-product", price=10.99, active=True)

        CartItem.objects.create(cart=cart1, product=product, amount=2)

        response = authenticated_client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200

        # Verify that cart data was processed correctly
        carts_with_data = response.context["carts_with_data"]
        cart_data = next((cd for cd in carts_with_data if cd["cart"].id == cart1.id), None)
        assert cart_data is not None
        assert cart_data["total"] > 0  # Should have calculated total
        assert cart_data["item_count"] > 0  # Should have counted items
        assert "Test Product" in cart_data["products"]  # Should have product name

    def test_cart_list_view_with_customer_lookup_error(self, authenticated_client, test_carts):
        """Test CartListView handles customer lookup errors."""
        cart1, cart2 = test_carts

        # Create a cart with a user but no corresponding customer
        user = User.objects.create_user(username="testuser", email="test@test.com")
        cart_with_user = Cart.objects.create(user=user)

        response = authenticated_client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200

        # Should handle Customer.DoesNotExist gracefully
        carts_with_data = response.context["carts_with_data"]
        cart_data = next((cd for cd in carts_with_data if cd["cart"].id == cart_with_user.id), None)
        assert cart_data is not None
        assert cart_data["customer"] is None

    def test_cart_list_view_shows_15_carts_per_page(self, authenticated_client, test_carts):
        """Test that cart list shows 15 carts per page."""
        cart1, cart2 = test_carts
        # Create 20 carts to test pagination (plus the 2 existing = 22 total)
        for i in range(20):
            Cart.objects.create(session=f"test_session_{i}")

        response = authenticated_client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200

        # Should have pagination context
        assert "carts_page" in response.context
        carts_page = response.context["carts_page"]

        # Should show 15 carts per page in list view
        assert len(carts_page) == 15
        assert carts_page.has_next()

    def test_cart_list_view_contains_cart_data(self, authenticated_client, test_carts):
        """Test that cart list view contains enriched cart data."""
        response = authenticated_client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200

        # Should have carts_with_data in context
        assert "carts_with_data" in response.context
        carts_with_data = response.context["carts_with_data"]

        # Should have at least the test carts
        assert len(carts_with_data) >= 2

        # Each cart data should have required fields
        for cart_data in carts_with_data:
            assert "cart" in cart_data
            assert "total" in cart_data
            assert "item_count" in cart_data
            assert "products" in cart_data
            assert "customer" in cart_data

    def test_cart_list_filter_form_is_present(self, authenticated_client, test_carts):
        """Test that cart list contains the filter form."""
        response = authenticated_client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200

        # Should have filter form in context
        assert "filter_form" in response.context

        # Should contain filter form in HTML
        content = response.content.decode()
        assert 'name="start"' in content
        assert 'name="end"' in content
        assert "dateinput" in content

    def test_cart_list_view_filtering_works(self, authenticated_client, test_carts):
        """Test that filtering works in cart list view."""
        # Set filters in session
        session = authenticated_client.session
        session["cart-filters"] = {"start": "2023-01-01", "end": "2023-12-31"}
        session.save()

        response = authenticated_client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200

        # Should apply filters to queryset
        assert "carts_page" in response.context
        # The actual filtering logic is tested in the view method tests

    def test_cart_list_view_template_renders_correctly(self, authenticated_client, test_carts):
        """Test that cart list template renders correctly."""
        response = authenticated_client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200

        content = response.content.decode()
        # Should contain table headers
        assert "Cart ID" in content or "cart id" in content.lower()
        assert "Customer" in content or "customer" in content.lower()
        assert "Items" in content or "items" in content.lower()
        assert "Total" in content or "total" in content.lower()

        # Should contain filter toggle button
        assert "Filter" in content or "filter" in content.lower()

        # Should contain cart rows (clickable)
        assert "cart-row" in content


class TestNoCartsView:
    """Test NoCartsView functionality."""

    def test_no_carts_view_renders_correctly(self, authenticated_client):
        """Test that NoCartsView renders the correct template."""
        Cart.objects.all().delete()
        response = authenticated_client.get(reverse("lfs_manage_no_carts"))
        assert response.status_code == 200
        assert "no carts" in response.content.decode().lower()


class TestCartDataView:
    """Test CartDataView functionality."""

    def test_cart_data_view_renders_correctly(self, authenticated_client, test_carts):
        """Test that CartDataView renders the cart data correctly."""
        cart1, cart2 = test_carts
        response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
        assert response.status_code == 200
        assert "cart" in response.content.decode().lower()

    def test_cart_data_view_with_actual_cart_items(self, authenticated_client, test_carts):
        """Test CartDataView processes actual cart items to hit lines 245-246."""
        from lfs.catalog.models import Product
        from lfs.cart.models import CartItem

        cart1, cart2 = test_carts

        # Create actual products and cart items to ensure lines 245-246 are executed
        product = Product.objects.create(
            name="Test Product for Cart Data", slug="test-product-cart-data", price=15.99, active=True
        )

        CartItem.objects.create(cart=cart1, product=product, amount=3)

        response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
        assert response.status_code == 200

        # Verify that cart data was processed correctly
        assert response.context["cart_total"] > 0  # Should have calculated total
        assert "Test Product for Cart Data" in response.context["cart_products"]  # Should have product name

    def test_cart_data_view_with_customer_lookup_error(self, authenticated_client, test_carts):
        """Test CartDataView handles customer lookup errors."""
        cart1, cart2 = test_carts

        # Create a cart with a user but no corresponding customer
        user = User.objects.create_user(username="testuser2", email="test2@test.com")
        cart_with_user = Cart.objects.create(user=user)

        response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart_with_user.id}))
        assert response.status_code == 200

        # Should handle Customer.DoesNotExist gracefully
        assert response.context["customer"] is None

    def test_sidebar_pagination_shows_10_carts_per_page(self, authenticated_client, test_carts):
        """Test that sidebar shows 10 carts per page."""
        cart1, cart2 = test_carts
        # Create 15 carts to test pagination (plus the 2 existing = 17 total)
        for i in range(15):
            Cart.objects.create(session=f"test_session_{i}")

        response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
        assert response.status_code == 200

        # Should have pagination context
        assert "carts_page" in response.context
        carts_page = response.context["carts_page"]

        # Should show 10 carts per page
        assert len(carts_page) == 10
        assert carts_page.has_next()

    def test_sidebar_filter_form_is_present(self, authenticated_client, test_carts):
        """Test that sidebar contains the filter form."""
        cart1, cart2 = test_carts
        response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
        assert response.status_code == 200

        # Should have filter form in context
        assert "filter_form" in response.context

        # Should contain filter form in HTML
        content = response.content.decode()
        assert 'name="start"' in content
        assert 'name="end"' in content

        # Should use Flatpickr class (check for the actual class that's being used)
        assert "dateinput" in content

    def test_date_format_parsing(self, authenticated_client, test_carts):
        """Test that various date formats are parsed correctly (testing uses ISO)."""
        cart1, cart2 = test_carts

        # Test ISO format (primary in testing settings)
        session = authenticated_client.session
        session["cart-filters"] = {"start": "2023-01-01", "end": "2023-12-31"}
        session.save()

        response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
        assert response.status_code == 200

        # Test US format (compatibility)
        session["cart-filters"] = {"start": "12/31/2023", "end": "01/01/2024"}
        session.save()

        response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
        assert response.status_code == 200

        # Test German format (compatibility)
        session["cart-filters"] = {"start": "31.12.2023", "end": "01.01.2024"}
        session.save()

        response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
        assert response.status_code == 200


class TestApplyCartFiltersView:
    """Test ApplyCartFiltersView functionality."""

    def test_apply_cart_filters_view_processes_form(self, authenticated_client, test_carts):
        """Test that ApplyCartFiltersView processes filter form correctly."""
        cart1, cart2 = test_carts
        response = authenticated_client.post(
            reverse("lfs_apply_cart_filters", kwargs={"id": cart1.id}),
            {"start": "2023-01-01", "end": "2023-12-31"},  # ISO format (testing settings)
        )
        assert response.status_code == 302  # Should redirect after processing

        # Check that filters are saved in localized format
        session = authenticated_client.session
        cart_filters = session.get("cart-filters", {})
        assert "start" in cart_filters
        assert "end" in cart_filters

    def test_apply_cart_filters_removes_start_filter_when_empty(self, authenticated_client, test_carts):
        """Test that empty start date removes the filter from session."""
        cart1, cart2 = test_carts

        # Set existing filters in session
        session = authenticated_client.session
        session["cart-filters"] = {"start": "2023-01-01", "end": "2023-12-31"}
        session.save()

        # Submit form with empty start date
        response = authenticated_client.post(
            reverse("lfs_apply_cart_filters", kwargs={"id": cart1.id}), {"start": "", "end": "2023-12-31"}
        )

        assert response.status_code == 302

        # Start filter should be removed from session
        session = authenticated_client.session
        cart_filters = session.get("cart-filters", {})
        assert "start" not in cart_filters
        assert "end" in cart_filters

    def test_apply_cart_filters_removes_end_filter_when_empty(self, authenticated_client, test_carts):
        """Test that empty end date removes the filter from session."""
        cart1, cart2 = test_carts

        # Set existing filters in session
        session = authenticated_client.session
        session["cart-filters"] = {"start": "2023-01-01", "end": "2023-12-31"}
        session.save()

        # Submit form with empty end date
        response = authenticated_client.post(
            reverse("lfs_apply_cart_filters", kwargs={"id": cart1.id}), {"start": "2023-01-01", "end": ""}
        )

        assert response.status_code == 302

        # End filter should be removed from session
        session = authenticated_client.session
        cart_filters = session.get("cart-filters", {})
        assert "start" in cart_filters
        assert "end" not in cart_filters

    def test_apply_cart_filters_list_view_processes_form(self, authenticated_client, test_carts):
        """Test that ApplyCartFiltersView processes filter form correctly for list view."""
        response = authenticated_client.post(
            reverse("lfs_apply_cart_filters_list"),
            {"start": "2023-01-01", "end": "2023-12-31"},  # ISO format (testing settings)
        )
        assert response.status_code == 302  # Should redirect after processing
        assert response.url == reverse("lfs_manage_carts")  # Should redirect to list view

        # Check that filters are saved in session
        session = authenticated_client.session
        cart_filters = session.get("cart-filters", {})
        assert "start" in cart_filters
        assert "end" in cart_filters


class TestApplyPredefinedCartFilterView:
    """Test ApplyPredefinedCartFilterView with all filter types."""

    def test_apply_predefined_filter_week(self, authenticated_client, test_carts):
        """Test applying weekly filter."""
        cart1, cart2 = test_carts

        response = authenticated_client.get(
            reverse("lfs_apply_predefined_cart_filter", kwargs={"id": cart1.id, "filter_type": "week"})
        )

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_cart", kwargs={"id": cart1.id})

        # Check that weekly filters are saved in session
        session = authenticated_client.session
        cart_filters = session.get("cart-filters", {})
        assert "start" in cart_filters
        assert "end" in cart_filters

    def test_apply_predefined_filter_month(self, authenticated_client, test_carts):
        """Test applying monthly filter."""
        cart1, cart2 = test_carts

        response = authenticated_client.get(
            reverse("lfs_apply_predefined_cart_filter", kwargs={"id": cart1.id, "filter_type": "month"})
        )

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_cart", kwargs={"id": cart1.id})

        # Check that monthly filters are saved in session
        session = authenticated_client.session
        cart_filters = session.get("cart-filters", {})
        assert "start" in cart_filters
        assert "end" in cart_filters

    def test_apply_predefined_filter_invalid_type(self, authenticated_client, test_carts):
        """Test applying invalid filter type shows error."""
        cart1, cart2 = test_carts

        response = authenticated_client.get(
            reverse("lfs_apply_predefined_cart_filter", kwargs={"id": cart1.id, "filter_type": "invalid"})
        )

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_cart", kwargs={"id": cart1.id})

        # Should show error message (would need to check messages in a real app)

    def test_apply_predefined_filter_with_cart_id_in_url(self, authenticated_client, test_carts):
        """Test predefined filter redirects correctly with cart_id."""
        cart1, cart2 = test_carts

        response = authenticated_client.get(
            reverse("lfs_apply_predefined_cart_filter", kwargs={"id": cart1.id, "filter_type": "today"})
        )

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_cart", kwargs={"id": cart1.id})

    def test_apply_predefined_filter_list_view_week(self, authenticated_client, test_carts):
        """Test applying weekly filter for list view."""
        response = authenticated_client.get(
            reverse("lfs_apply_predefined_cart_filter_list", kwargs={"filter_type": "week"})
        )

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_carts")

        # Check that weekly filters are saved in session
        session = authenticated_client.session
        cart_filters = session.get("cart-filters", {})
        assert "start" in cart_filters
        assert "end" in cart_filters

    def test_apply_predefined_filter_list_view_month(self, authenticated_client, test_carts):
        """Test applying monthly filter for list view."""
        response = authenticated_client.get(
            reverse("lfs_apply_predefined_cart_filter_list", kwargs={"filter_type": "month"})
        )

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_carts")

        # Check that monthly filters are saved in session
        session = authenticated_client.session
        cart_filters = session.get("cart-filters", {})
        assert "start" in cart_filters
        assert "end" in cart_filters

    def test_apply_predefined_filter_list_view_invalid_type(self, authenticated_client, test_carts):
        """Test applying invalid filter type for list view shows error."""
        response = authenticated_client.get(
            reverse("lfs_apply_predefined_cart_filter_list", kwargs={"filter_type": "invalid"})
        )

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_carts")

    def test_apply_predefined_cart_filter_list_view(self, authenticated_client, test_carts):
        """Test that predefined filters work for list view."""
        response = authenticated_client.get(
            reverse("lfs_apply_predefined_cart_filter_list", kwargs={"filter_type": "today"})
        )
        assert response.status_code == 302  # Should redirect after processing
        assert response.url == reverse("lfs_manage_carts")  # Should redirect to list view

        # Check that filters are saved in session
        session = authenticated_client.session
        cart_filters = session.get("cart-filters", {})
        assert "start" in cart_filters
        assert "end" in cart_filters


class TestCartDeleteViews:
    """Test cart deletion views."""

    def test_cart_delete_confirm_view_renders_correctly(self, authenticated_client, test_carts):
        """Test that CartDeleteConfirmView renders correctly."""
        cart1, cart2 = test_carts
        response = authenticated_client.get(reverse("lfs_manage_delete_cart_confirm", kwargs={"id": cart1.id}))
        assert response.status_code == 200

    def test_cart_delete_view_deletes_cart(self, authenticated_client, test_carts):
        """Test that CartDeleteView actually deletes the cart."""
        cart1, cart2 = test_carts
        cart_id = cart1.id
        response = authenticated_client.post(reverse("lfs_delete_cart", kwargs={"id": cart_id}))

        # Should redirect after deletion
        assert response.status_code == 302

        # Cart should be deleted
        assert not Cart.objects.filter(id=cart_id).exists()


class TestResetCartFiltersView:
    """Test ResetCartFiltersView functionality."""

    def test_reset_cart_filters_view_clears_session(self, authenticated_client):
        """Test that ResetCartFiltersView clears the cart filters from session."""
        # Set some filters in session
        session = authenticated_client.session
        session["cart-filters"] = {"start": "2023-01-01", "end": "2023-12-31"}
        session.save()

        response = authenticated_client.get(reverse("lfs_reset_cart_filters"))

        # Should redirect
        assert response.status_code == 302

        # Filters should be cleared
        assert "cart-filters" not in authenticated_client.session

    def test_reset_cart_filters_with_cart_id_parameter(self, authenticated_client, test_carts):
        """Test that reset cart filters works with cart_id parameter."""
        cart1, cart2 = test_carts

        # Set some filters first
        session = authenticated_client.session
        session["cart-filters"] = {"start": "2023-01-01", "end": "2023-12-31"}
        session.save()

        # Reset filters with cart_id parameter (should redirect back to cart)
        response = authenticated_client.get(reverse("lfs_reset_cart_filters") + f"?cart_id={cart1.id}")

        # Should redirect successfully
        assert response.status_code == 302

        # Should redirect to the cart view, not the old filters view
        assert response.url == reverse("lfs_manage_cart", kwargs={"id": cart1.id})

        # Filters should be cleared
        session = authenticated_client.session
        assert "cart-filters" not in session


class TestEdgeCasesAndBoundaryConditions:
    """Test edge cases and boundary conditions."""

    def test_cart_queryset_with_no_session_filters(self, authenticated_client, test_carts):
        """Test cart queryset when no session filters exist."""
        # Clear any existing filters
        session = authenticated_client.session
        if "cart-filters" in session:
            del session["cart-filters"]
        session.save()

        response = authenticated_client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
        # Should use default date range (1970 to now)

    def test_cart_queryset_with_partial_filters(self, authenticated_client, test_carts):
        """Test cart queryset with only start or end filter."""
        # Set only start filter
        session = authenticated_client.session
        session["cart-filters"] = {"start": "2023-01-01"}
        session.save()

        response = authenticated_client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200

        # Set only end filter
        session["cart-filters"] = {"end": "2023-12-31"}
        session.save()

        response = authenticated_client.get(reverse("lfs_manage_carts"))
        assert response.status_code == 200
