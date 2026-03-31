import pytest
from datetime import datetime, date

from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import RequestFactory

from lfs.cart.models import Cart, CartItem
from lfs.catalog.models import Product
from lfs.manage.carts.views import (
    CartListView,
    CartDataView,
    ApplyCartFiltersView,
    ResetCartFiltersView,
    ApplyPredefinedCartFilterView,
    NoCartsView,
    CartDeleteConfirmView,
    CartDeleteView,
)

User = get_user_model()


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def mock_request(request_factory):
    """Mock request object for testing."""
    request = request_factory.get("/")
    request.session = {}
    # Mock messages framework for unit tests
    messages_mock = type(
        "MockMessages",
        (),
        {
            "success": lambda msg: None,
            "error": lambda msg: None,
            "add": lambda self, level, message, extra_tags="": None,
        },
    )()
    request._messages = messages_mock
    return request


@pytest.fixture
def admin_user():
    """Admin user for testing."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def regular_user():
    """Regular user for testing."""
    return User.objects.create_user(username="user", email="user@example.com", password="testpass123")


class TestCartListViewUnit:
    """Unit tests for CartListView."""

    @pytest.mark.django_db
    def test_get_context_data_includes_required_keys(self, mock_request, admin_user):
        """Test that get_context_data includes all required context keys."""
        view = CartListView()
        view.request = mock_request
        view.request.user = admin_user

        context = view.get_context_data()

        assert "carts_with_data" in context
        assert "carts_page" in context
        assert "filter_form" in context

    @pytest.mark.django_db
    def test_get_context_data_returns_cart_queryset(self, mock_request, admin_user):
        """Test that get_context_data includes filtered carts."""
        view = CartListView()
        view.request = mock_request
        view.request.user = admin_user

        context = view.get_context_data()

        assert "carts_page" in context
        assert hasattr(context["carts_page"], "object_list")

    @pytest.mark.django_db
    def test_get_context_data_applies_filters_from_session(self, mock_request, admin_user, monkeypatch):
        """Test that get_context_data applies filters from session."""
        view = CartListView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {"cart-filters": {"start": "2024-01-01", "end": "2024-12-31"}}

        mock_filter_called = False

        def mock_filter_carts(*args, **kwargs):
            nonlocal mock_filter_called
            mock_filter_called = True
            return Cart.objects.none()

        monkeypatch.setattr("lfs.manage.carts.services.CartFilterService.filter_carts", mock_filter_carts)

        view.get_context_data()

        assert mock_filter_called

    @pytest.mark.django_db
    def test_get_context_data_handles_empty_session(self, mock_request, admin_user):
        """Test that get_context_data handles empty session gracefully."""
        view = CartListView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {}

        context = view.get_context_data()

        assert "carts_page" in context

    @pytest.mark.django_db
    def test_get_context_data_handles_empty_session(self, mock_request, admin_user):
        """Test that get_context_data handles empty session gracefully."""
        view = CartListView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {}

        context = view.get_context_data()

        assert "carts_page" in context


class TestCartDataViewUnit:
    """Unit tests for CartDataView."""

    @pytest.mark.django_db
    def test_get_cart_returns_cart_by_id(self, mock_request, admin_user):
        """Test that get_cart returns cart by ID."""
        cart = Cart.objects.create(session="test_session")
        view = CartDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": cart.id}

        result = view.get_cart()

        assert result == cart

    @pytest.mark.django_db
    def test_get_cart_raises_404_for_nonexistent_cart(self, mock_request, admin_user):
        """Test that get_cart raises 404 for nonexistent cart."""
        view = CartDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": 99999}

        with pytest.raises(Http404):
            view.get_cart()

    @pytest.mark.django_db
    def test_get_context_data_includes_required_keys(self, mock_request, admin_user):
        """Test that get_context_data includes all required context keys."""
        cart = Cart.objects.create(session="test_session")
        view = CartDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": cart.id}

        context = view.get_context_data()

        assert "cart" in context
        assert "carts_page" in context
        assert "filter_form" in context

    @pytest.mark.django_db
    def test_get_context_data_calculates_cart_total(self, mock_request, admin_user, monkeypatch):
        """Test that get_context_data calculates cart total correctly."""
        cart = Cart.objects.create(session="test_session")
        product = Product.objects.create(name="Test Product", slug="test-product", price=10.99, active=True)
        CartItem.objects.create(cart=cart, product=product, amount=2)

        view = CartDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": cart.id}

        monkeypatch.setattr(view, "get_cart", lambda: cart)
        context = view.get_context_data()

        assert "cart_total" in context
        assert context["cart_total"] > 0

    @pytest.mark.django_db
    def test_get_context_data_handles_empty_cart(self, mock_request, admin_user, monkeypatch):
        """Test that get_context_data handles empty cart."""
        cart = Cart.objects.create(session="test_session")

        view = CartDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": cart.id}

        monkeypatch.setattr(view, "get_cart", lambda: cart)
        context = view.get_context_data()

        assert "cart_total" in context
        assert context["cart_total"] == 0


class TestApplyCartFiltersViewUnit:
    """Unit tests for ApplyCartFiltersView."""

    @pytest.mark.django_db
    def test_post_saves_filters_to_session(self, mock_request, admin_user):
        """Test that POST saves filters to session."""
        cart = Cart.objects.create(session="test_session")
        view = ApplyCartFiltersView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {}
        view.kwargs = {"id": cart.id}

        # Test the form_valid method directly
        from lfs.manage.carts.forms import CartFilterForm

        form = CartFilterForm(data={"start": "2024-01-01", "end": "2024-12-31"})
        form.is_valid()

        view.form_valid(form)

        assert "cart-filters" in view.request.session
        assert view.request.session["cart-filters"]["start"] == "2024-01-01"
        assert view.request.session["cart-filters"]["end"] == "2024-12-31"

    @pytest.mark.django_db
    def test_post_removes_empty_filters_from_session(self, mock_request, admin_user):
        """Test that POST removes empty filters from session."""
        cart = Cart.objects.create(session="test_session")
        view = ApplyCartFiltersView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {"cart-filters": {"start": "2024-01-01", "end": "2024-12-31"}}
        view.kwargs = {"id": cart.id}

        # Test the form_valid method directly with empty start date
        from lfs.manage.carts.forms import CartFilterForm

        form = CartFilterForm(data={"start": "", "end": "2024-12-31"})
        form.is_valid()

        view.form_valid(form)

        assert "start" not in view.request.session["cart-filters"]
        assert "end" in view.request.session["cart-filters"]

    @pytest.mark.django_db
    def test_get_success_url_redirects_to_cart_view(self, mock_request, admin_user):
        """Test that get_success_url redirects to cart view."""
        cart = Cart.objects.create(session="test_session")
        view = ApplyCartFiltersView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": cart.id}

        url = view.get_success_url()

        assert str(cart.id) in url

    @pytest.mark.django_db
    def test_get_success_url_redirects_to_list_view_for_list_action(self, mock_request, admin_user):
        """Test that get_success_url redirects to list view for list action."""
        view = ApplyCartFiltersView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"action": "list"}

        url = view.get_success_url()

        assert "carts" in url


class TestResetCartFiltersViewUnit:
    """Unit tests for ResetCartFiltersView."""

    @pytest.mark.django_db
    def test_get_clears_cart_filters_from_session(self, mock_request, admin_user):
        """Test that get_redirect_url clears cart filters from session."""
        view = ResetCartFiltersView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {"cart-filters": {"start": "2024-01-01", "end": "2024-12-31"}}

        # Call get_redirect_url directly since that's where the session clearing happens
        view.get_redirect_url()

        assert "cart-filters" not in view.request.session

    @pytest.mark.django_db
    def test_get_handles_empty_session(self, mock_request, admin_user):
        """Test that get_redirect_url handles empty session gracefully."""
        view = ResetCartFiltersView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {}

        # Call get_redirect_url directly - should not raise exception
        view.get_redirect_url()

        # Should not raise exception

    @pytest.mark.django_db
    def test_get_redirect_url_redirects_to_carts_list(self, mock_request, admin_user):
        """Test that get_redirect_url redirects to carts list."""
        view = ResetCartFiltersView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {}

        url = view.get_redirect_url()

        assert "carts" in url

    @pytest.mark.django_db
    def test_get_redirect_url_with_cart_id_parameter(self, mock_request, admin_user):
        """Test that get_redirect_url handles cart_id parameter."""
        view = ResetCartFiltersView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {}
        view.request.GET = {"cart_id": "123"}

        url = view.get_redirect_url()

        assert "123" in url


class TestApplyPredefinedCartFilterViewUnit:
    """Unit tests for ApplyPredefinedCartFilterView."""

    @pytest.mark.django_db
    def test_get_applies_week_filter(self, mock_request, admin_user, monkeypatch):
        """Test that GET applies week filter."""
        cart = Cart.objects.create(session="test_session")
        view = ApplyPredefinedCartFilterView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {}
        view.kwargs = {"id": cart.id, "filter_type": "week"}

        monkeypatch.setattr("django.contrib.messages.success", lambda request, message: None)
        view.get(mock_request)

        assert "cart-filters" in view.request.session
        assert "start" in view.request.session["cart-filters"]

    @pytest.mark.django_db
    def test_get_applies_month_filter(self, mock_request, admin_user, monkeypatch):
        """Test that GET applies month filter."""
        cart = Cart.objects.create(session="test_session")
        view = ApplyPredefinedCartFilterView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {}
        view.kwargs = {"id": cart.id, "filter_type": "month"}

        monkeypatch.setattr("django.contrib.messages.success", lambda request, message: None)
        view.get(mock_request)

        assert "cart-filters" in view.request.session
        assert "start" in view.request.session["cart-filters"]

    @pytest.mark.django_db
    def test_get_applies_today_filter(self, mock_request, admin_user, monkeypatch):
        """Test that GET applies today filter."""
        cart = Cart.objects.create(session="test_session")
        view = ApplyPredefinedCartFilterView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {}
        view.kwargs = {"id": cart.id, "filter_type": "today"}

        monkeypatch.setattr("django.contrib.messages.success", lambda request, message: None)
        view.get(mock_request)

        assert "cart-filters" in view.request.session
        assert "start" in view.request.session["cart-filters"]

    @pytest.mark.django_db
    def test_get_handles_invalid_filter_type(self, mock_request, admin_user, monkeypatch):
        """Test that GET handles invalid filter type."""
        cart = Cart.objects.create(session="test_session")
        view = ApplyPredefinedCartFilterView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {}
        view.kwargs = {"id": cart.id, "filter_type": "invalid"}

        monkeypatch.setattr("django.contrib.messages.error", lambda request, message: None)
        view.get(mock_request)

        # Should not crash, but may not set filters

    @pytest.mark.django_db
    def test_get_redirect_url_redirects_to_cart_view(self, mock_request, admin_user):
        """Test that get_redirect_url redirects to cart view."""
        cart = Cart.objects.create(session="test_session")
        view = ApplyPredefinedCartFilterView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": cart.id}

        url = view.get_redirect_url()

        assert str(cart.id) in url


class TestNoCartsViewUnit:
    """Unit tests for NoCartsView."""

    @pytest.mark.django_db
    def test_get_renders_no_carts_template(self, mock_request, admin_user):
        """Test that GET renders no carts template."""
        view = NoCartsView()
        view.request = mock_request
        view.request.user = admin_user

        response = view.get(mock_request)

        assert response.status_code == 200


class TestCartDeleteViewsUnit:
    """Unit tests for cart deletion views."""

    @pytest.mark.django_db
    def test_cart_delete_confirm_view_get_context_data(self, mock_request, admin_user):
        """Test that CartDeleteConfirmView includes cart in context."""
        cart = Cart.objects.create(session="test_session")
        view = CartDeleteConfirmView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": cart.id}

        context = view.get_context_data()

        assert "cart" in context
        assert context["cart"] == cart

    @pytest.mark.django_db
    def test_cart_delete_view_post_deletes_cart(self, mock_request, admin_user, monkeypatch):
        """Test that CartDeleteView POST deletes the cart."""
        cart = Cart.objects.create(session="test_session")
        cart_id = cart.id
        view = CartDeleteView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": cart_id}

        monkeypatch.setattr(view, "get_success_url", lambda: "/success/")
        # Call the delete method directly instead of post
        view.delete(mock_request)

        assert not Cart.objects.filter(id=cart_id).exists()

    @pytest.mark.django_db
    def test_cart_delete_view_get_success_url_redirects_to_carts_list(self, mock_request, admin_user):
        """Test that CartDeleteView get_success_url redirects to carts list."""
        view = CartDeleteView()
        view.request = mock_request
        view.request.user = admin_user

        url = view.get_success_url()

        assert "carts" in url


class TestUtilityFunctions:
    """Test utility functions for date parsing and formatting."""

    def setup_method(self):
        """Set up the service for each test."""
        from lfs.manage.carts.services import CartFilterService

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

    @pytest.mark.parametrize(
        "date_string,expected",
        [
            ("2023-01-01", date(2023, 1, 1)),
            ("2023-12-31", date(2023, 12, 31)),
            ("2000-02-29", date(2000, 2, 29)),
            ("1999-06-15", date(1999, 6, 15)),
            ("2024-03-08", date(2024, 3, 8)),
        ],
    )
    def test_parse_iso_date_with_valid_iso_format(self, date_string, expected):
        """Test parse_iso_date correctly parses valid ISO format dates."""
        result = self.service.parse_iso_date(date_string)
        assert result == expected

    @pytest.mark.parametrize(
        "invalid_format",
        [
            "invalid-date-format",
            "2023/01/01",
            "01-01-2023",
            "2023-13-01",
            "2023-01-32",
            "2023-00-01",
            "2023-01-00",
            "2023-02-30",
            "abc-def-ghi",
            "2023-01-01T12:00:00",
            "2023-01-01 12:00:00",
        ],
    )
    def test_parse_iso_date_with_invalid_format(self, invalid_format):
        """Test parse_iso_date returns None for invalid format."""
        result = self.service.parse_iso_date(invalid_format)
        assert result is None, f"Expected None for '{invalid_format}', got {result}"

    @pytest.mark.parametrize(
        "date_string,expected",
        [
            ("1900-01-01", date(1900, 1, 1)),
            ("9999-12-31", date(9999, 12, 31)),
            ("0001-01-01", date(1, 1, 1)),
        ],
    )
    def test_parse_iso_date_with_edge_case_years(self, date_string, expected):
        """Test parse_iso_date with edge case years."""
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

    @pytest.mark.parametrize("value", [None, "", 0, False, [], {}])
    def test_format_iso_date_with_falsy_values(self, value):
        """Test format_iso_date returns empty string for falsy values."""
        result = self.service.format_iso_date(value)
        assert result == "", f"Expected empty string for {value}, got '{result}'"

    @pytest.mark.parametrize(
        "date_obj,expected",
        [
            (datetime(2023, 1, 1), "2023-01-01"),
            (datetime(2023, 12, 31), "2023-12-31"),
            (datetime(2000, 2, 29), "2000-02-29"),
            (datetime(1999, 6, 15), "1999-06-15"),
            (datetime(2024, 3, 8), "2024-03-08"),
            (datetime(1900, 1, 1), "1900-01-01"),
            (datetime(9999, 12, 31), "9999-12-31"),
        ],
    )
    def test_format_iso_date_with_valid_datetime_objects(self, date_obj, expected):
        """Test format_iso_date correctly formats valid datetime objects."""
        result = self.service.format_iso_date(date_obj)
        assert result == expected, f"Expected '{expected}' for {date_obj}, got '{result}'"

    @pytest.mark.parametrize(
        "date_obj,expected",
        [
            (datetime(2023, 1, 1, 12, 30, 45, 123456), "2023-01-01"),
            (datetime(2023, 12, 31, 23, 59, 59, 999999), "2023-12-31"),
            (datetime(2000, 2, 29, 0, 0, 0, 0), "2000-02-29"),
        ],
    )
    def test_format_iso_date_with_datetime_objects_with_time(self, date_obj, expected):
        """Test format_iso_date ignores time component and only formats date."""
        result = self.service.format_iso_date(date_obj)
        assert result == expected, f"Expected '{expected}' for {date_obj}, got '{result}'"

    def test_format_iso_date_with_date_objects(self):
        """Test format_iso_date works with date objects (not just datetime)."""
        test_cases = [
            (date(2023, 1, 1), "2023-01-01"),
            (date(2023, 12, 31), "2023-12-31"),
            (date(2000, 2, 29), "2000-02-29"),
        ]

        for date_obj, expected in test_cases:
            result = self.service.format_iso_date(date_obj)
            assert result == expected, f"Expected '{expected}' for {date_obj}, got '{result}'"

    @pytest.mark.parametrize(
        "original_date",
        [
            datetime(2023, 1, 1),
            datetime(2023, 12, 31),
            datetime(2000, 2, 29),
            datetime(1999, 6, 15),
            datetime(2024, 3, 8),
        ],
    )
    def test_round_trip_parsing_and_formatting(self, original_date):
        """Test that parse_iso_date and format_iso_date work together correctly."""
        formatted = self.service.format_iso_date(original_date)
        parsed = self.service.parse_iso_date(formatted)
        reformatted = self.service.format_iso_date(parsed)

        assert formatted == reformatted
        assert parsed == original_date.date()

    def test_parse_iso_date_preserves_timezone_naive_datetime(self):
        """Test that parse_iso_date returns timezone-naive datetime objects."""
        result = self.service.parse_iso_date("2023-01-01")
        assert result is not None
        assert isinstance(result, date)
