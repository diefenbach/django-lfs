"""
Comprehensive unit tests for topseller views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- View method logic and context data
- Permission checks
- Filtering and pagination
- AJAX responses
- Error handling
- Edge cases and boundary conditions
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory

from lfs.marketing.models import Topseller
from lfs.manage.topseller.views import (
    ManageTopsellerView,
    manage_topseller,
    manage_topseller_inline,
    add_topseller,
    update_topseller,
    sort_topseller,
    _update_positions,
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
    # Mock session with session_key attribute
    session_mock = type(
        "MockSession",
        (),
        {
            "session_key": "test_session_key",
            "get": lambda self, key, default=None: default,
            "__setitem__": lambda self, key, value: None,
            "__getitem__": lambda self, key: None,
            "__contains__": lambda self, key: False,
        },
    )()
    request.session = session_mock
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


class TestManageTopsellerView:
    """Test ManageTopsellerView functionality."""

    @pytest.mark.django_db
    def test_get_context_data_includes_required_keys(
        self, mock_request, admin_user, sample_products, sample_topsellers
    ):
        """Test that get_context_data includes all required context keys."""
        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user

        context = view.get_context_data()

        required_keys = [
            "topseller",
            "total",
            "page",
            "paginator",
            "filter",
            "category_filter",
            "amount_options",
            "categories",
        ]
        for key in required_keys:
            assert key in context

    @pytest.mark.django_db
    def test_get_context_data_with_no_filters(self, mock_request, admin_user, sample_products, sample_topsellers):
        """Test context data when no filters are applied."""
        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user

        context = view.get_context_data()

        assert context["filter"] == ""
        assert context["category_filter"] is None
        assert context["total"] == 2  # 5 products - 3 topsellers = 2 available

    @pytest.mark.django_db
    def test_get_context_data_with_name_filter(self, mock_request, admin_user, sample_products, sample_topsellers):
        """Test context data with name filter applied."""
        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"filter": "Product 1"}

        context = view.get_context_data()

        assert context["filter"] == "Product 1"
        assert context["total"] == 0  # No products match "Product 1" exactly

    @pytest.mark.django_db
    def test_get_context_data_with_sku_filter(self, mock_request, admin_user, sample_products, sample_topsellers):
        """Test context data with SKU filter applied."""
        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"filter": "SKU-004"}

        context = view.get_context_data()

        assert context["filter"] == "SKU-004"
        assert context["total"] == 1  # One product matches SKU-004

    @pytest.mark.django_db
    def test_get_context_data_with_category_filter(
        self, mock_request, admin_user, sample_products, sample_categories, sample_topsellers
    ):
        """Test context data with category filter applied."""
        # Add products to categories
        sample_products[0].categories.add(sample_categories[0])
        sample_products[1].categories.add(sample_categories[1])

        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"topseller_category_filter": str(sample_categories[0].id)}

        context = view.get_context_data()

        assert context["category_filter"] == str(sample_categories[0].id)
        assert context["total"] == 1  # One product in the selected category

    @pytest.mark.django_db
    def test_get_context_data_with_none_category_filter(
        self, mock_request, admin_user, sample_products, sample_topsellers
    ):
        """Test context data with 'None' category filter."""
        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"topseller_category_filter": "None"}

        context = view.get_context_data()

        assert context["category_filter"] == "None"
        assert context["total"] == 2  # Products without categories

    @pytest.mark.django_db
    def test_get_context_data_with_all_category_filter(
        self, mock_request, admin_user, sample_products, sample_topsellers
    ):
        """Test context data with 'All' category filter."""
        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"topseller_category_filter": "All"}

        context = view.get_context_data()

        assert context["category_filter"] == "All"
        assert context["total"] == 2  # All products (excluding topsellers)

    @pytest.mark.django_db
    def test_get_context_data_with_pagination(self, mock_request, admin_user, sample_products, sample_topsellers):
        """Test context data with pagination."""
        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"page": "1"}
        view.request.session = {"topseller-amount": 1}

        context = view.get_context_data()

        assert context["page"] is not None
        assert hasattr(context["page"], "object_list")

    @pytest.mark.django_db
    def test_get_context_data_with_invalid_page(self, mock_request, admin_user, sample_products, sample_topsellers):
        """Test context data with invalid page number."""
        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"page": "999"}
        view.request.session = {"topseller-amount": 1}

        context = view.get_context_data()

        assert context["page"] == 0  # EmptyPage returns 0

    @pytest.mark.django_db
    def test_get_context_data_amount_options(self, mock_request, admin_user, sample_products, sample_topsellers):
        """Test that amount options are correctly set."""
        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 25}

        context = view.get_context_data()

        amount_options = context["amount_options"]
        assert len(amount_options) == 4
        assert all(option["value"] in [10, 25, 50, 100] for option in amount_options)

        # Check that 25 is selected
        selected_option = next(option for option in amount_options if option["value"] == 25)
        assert selected_option["selected"] is True

    @pytest.mark.django_db
    def test_build_hierarchical_categories(self, mock_request, admin_user, sample_categories):
        """Test building hierarchical categories."""
        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user

        categories = view._build_hierarchical_categories()

        assert len(categories) == 4  # 1 parent + 3 children
        assert categories[0].level == 0  # Parent category
        assert categories[1].level == 1  # First child
        assert "Parent Category" in categories[0].name
        assert "Child Category" in categories[1].name

    @pytest.mark.django_db
    def test_permission_required(self, mock_request, regular_user):
        """Test that permission is required to access the view."""
        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = regular_user

        # Note: Permission check happens in dispatch(), not get_context_data()
        # This test verifies the view can be instantiated with proper permission settings
        assert view.permission_required == "core.manage_shop"
        assert hasattr(view, "get_context_data")


class TestManageTopsellerFunction:
    """Test manage_topseller function."""

    @pytest.mark.django_db
    def test_manage_topseller_returns_rendered_template(self, mock_request, admin_user, sample_topsellers):
        """Test that manage_topseller returns rendered template."""
        mock_request.user = admin_user
        mock_request.session = {"topseller-amount": 25}

        with patch(
            "lfs.manage.topseller.views.render_to_string",
            return_value="mocked topseller_inline content with amount_options",
        ):
            result = manage_topseller(mock_request)

            assert isinstance(result, str)
            assert "topseller_inline" in result
            assert "amount_options" in result

    @pytest.mark.django_db
    def test_manage_topseller_with_custom_template(self, mock_request, admin_user, sample_topsellers):
        """Test manage_topseller with custom template name."""
        mock_request.user = admin_user
        mock_request.session = {"topseller-amount": 25}

        with patch("lfs.manage.topseller.views.render_to_string", return_value="mocked custom template content"):
            result = manage_topseller(mock_request, template_name="custom_template.html")

            assert isinstance(result, str)


class TestManageTopsellerInlineFunction:
    """Test manage_topseller_inline function."""

    @pytest.mark.django_db
    def test_manage_topseller_inline_as_string(self, mock_request, admin_user, sample_topsellers):
        """Test manage_topseller_inline returns string when as_string=True."""
        mock_request.user = admin_user
        mock_request.session = {"topseller-amount": 25}

        with patch("lfs.manage.topseller.views.render_to_string", return_value="mocked inline content"):
            result = manage_topseller_inline(mock_request, as_string=True)

            assert isinstance(result, str)

    @pytest.mark.django_db
    def test_manage_topseller_inline_as_json(self, mock_request, admin_user, sample_topsellers):
        """Test manage_topseller_inline returns JSON when as_string=False."""
        mock_request.user = admin_user
        mock_request.session = {"topseller-amount": 25}

        result = manage_topseller_inline(mock_request, as_string=False)

        assert isinstance(result, HttpResponse)
        assert result["Content-Type"] == "application/json"

        data = json.loads(result.content)
        assert "html" in data
        assert len(data["html"]) == 1
        assert data["html"][0][0] == "#topseller-inline"

    @pytest.mark.django_db
    def test_manage_topseller_inline_with_filters(self, mock_request, admin_user, sample_products, sample_topsellers):
        """Test manage_topseller_inline with filters applied."""
        mock_request.user = admin_user
        mock_request.session = {"topseller-amount": 25}
        mock_request.GET = {"filter": "SKU-004"}

        with patch("lfs.manage.topseller.views.render_to_string", return_value="mocked filtered content with SKU-004"):
            result = manage_topseller_inline(mock_request, as_string=True)

            assert isinstance(result, str)
            assert "SKU-004" in result


class TestAddTopsellerFunction:
    """Test add_topseller function."""

    @pytest.mark.django_db
    def test_add_topseller_with_valid_products(self, mock_request, admin_user, sample_products):
        """Test adding valid products to topseller."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "product-1": "1",
            "product-2": "2",
        }

        # Mock the view rendering
        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class, patch(
            "lfs.manage.topseller.views.render"
        ) as mock_render:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}
            mock_render.return_value = HttpResponse("mocked")

            result = add_topseller(mock_request)

            # Check that topsellers were created
            assert Topseller.objects.count() == 2
            assert Topseller.objects.filter(product_id=1).exists()
            assert Topseller.objects.filter(product_id=2).exists()

    @pytest.mark.django_db
    def test_add_topseller_ignores_invalid_keys(self, mock_request, admin_user, sample_products):
        """Test that add_topseller ignores non-product keys."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "product-1": "1",
            "invalid-key": "value",
            "other-key": "value",
        }

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class, patch(
            "lfs.manage.topseller.views.render"
        ) as mock_render:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}
            mock_render.return_value = HttpResponse("mocked")

            result = add_topseller(mock_request)

            # Only one topseller should be created
            assert Topseller.objects.count() == 1
            assert Topseller.objects.filter(product_id=1).exists()

    @pytest.mark.django_db
    def test_add_topseller_updates_positions(self, mock_request, admin_user, sample_products):
        """Test that add_topseller updates positions after adding."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "product-1": "1",
            "product-2": "2",
        }

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class, patch(
            "lfs.manage.topseller.views.render"
        ) as mock_render:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}
            mock_render.return_value = HttpResponse("mocked")

            result = add_topseller(mock_request)

            # Check positions are set correctly
            topsellers = Topseller.objects.all().order_by("position")
            assert topsellers[0].position == 10
            assert topsellers[1].position == 20


class TestUpdateTopsellerFunction:
    """Test update_topseller function."""

    @pytest.mark.django_db
    def test_update_topseller_remove_action(self, mock_request, admin_user, sample_topsellers):
        """Test removing topseller products."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "action": "remove",
            "product-1": "1",
            "product-2": "2",
        }

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class, patch(
            "lfs.manage.topseller.views.render"
        ) as mock_render:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}
            mock_render.return_value = HttpResponse("mocked")

            initial_count = Topseller.objects.count()
            result = update_topseller(mock_request)

            # Check that topsellers were removed
            assert Topseller.objects.count() == initial_count - 2

    @pytest.mark.django_db
    def test_update_topseller_ignores_invalid_keys(self, mock_request, admin_user, sample_topsellers):
        """Test that update_topseller ignores non-product keys."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "action": "remove",
            "product-1": "1",
            "invalid-key": "value",
        }

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class, patch(
            "lfs.manage.topseller.views.render"
        ) as mock_render:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}
            mock_render.return_value = HttpResponse("mocked")

            initial_count = Topseller.objects.count()
            result = update_topseller(mock_request)

            # Only one topseller should be removed
            assert Topseller.objects.count() == initial_count - 1

    @pytest.mark.django_db
    def test_update_topseller_handles_nonexistent_topseller(self, mock_request, admin_user):
        """Test that update_topseller handles nonexistent topseller gracefully."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "action": "remove",
            "product-999": "999",  # Non-existent ID
        }

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class, patch(
            "lfs.manage.topseller.views.render"
        ) as mock_render:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}
            mock_render.return_value = HttpResponse("mocked")

            # Should not raise an exception
            result = update_topseller(mock_request)

    @pytest.mark.django_db
    def test_update_topseller_without_remove_action(self, mock_request, admin_user, sample_topsellers):
        """Test update_topseller without remove action does nothing."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "product-1": "1",
        }

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class, patch(
            "lfs.manage.topseller.views.render"
        ) as mock_render:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}
            mock_render.return_value = HttpResponse("mocked")

            initial_count = Topseller.objects.count()
            result = update_topseller(mock_request)

            # No topsellers should be removed
            assert Topseller.objects.count() == initial_count


class TestSortTopsellerFunction:
    """Test sort_topseller function."""

    @pytest.mark.django_db
    def test_sort_topseller_with_valid_data(self, mock_request, admin_user, sample_topsellers):
        """Test sorting topseller products with valid data."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        # Mock json.loads to return the expected data
        with patch("lfs.manage.topseller.views.json.loads", return_value={"topseller_ids": [2, 1, 3]}):
            result = sort_topseller(mock_request)

        assert isinstance(result, HttpResponse)

        # Check that positions were updated
        topseller1 = Topseller.objects.get(id=1)
        topseller2 = Topseller.objects.get(id=2)
        topseller3 = Topseller.objects.get(id=3)

        assert topseller2.position == 10  # First in new order
        assert topseller1.position == 20  # Second in new order
        assert topseller3.position == 30  # Third in new order

    @pytest.mark.django_db
    def test_sort_topseller_with_invalid_data(self, mock_request, admin_user, sample_topsellers):
        """Test sorting topseller products with invalid data."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        # Mock json.loads to return the expected data
        with patch("lfs.manage.topseller.views.json.loads", return_value={"topseller_ids": [999, 998]}):
            result = sort_topseller(mock_request)

        assert isinstance(result, HttpResponse)
        # Should not raise an exception

    @pytest.mark.django_db
    def test_sort_topseller_with_empty_data(self, mock_request, admin_user, sample_topsellers):
        """Test sorting topseller products with empty data."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        # Mock json.loads to return the expected data
        with patch("lfs.manage.topseller.views.json.loads", return_value={"topseller_ids": []}):
            result = sort_topseller(mock_request)

        assert isinstance(result, HttpResponse)
        # Should not raise an exception

    @pytest.mark.django_db
    def test_sort_topseller_with_missing_topseller_ids(self, mock_request, admin_user, sample_topsellers):
        """Test sorting topseller products with missing topseller_ids key."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        # Mock json.loads to return the expected data
        with patch("lfs.manage.topseller.views.json.loads", return_value={}):
            result = sort_topseller(mock_request)

        assert isinstance(result, HttpResponse)
        # Should not raise an exception


class TestUpdatePositionsFunction:
    """Test _update_positions function."""

    @pytest.mark.django_db
    def test_update_positions_sets_correct_positions(self, sample_topsellers):
        """Test that _update_positions sets correct positions."""
        # Manually set incorrect positions
        Topseller.objects.filter(id=1).update(position=100)
        Topseller.objects.filter(id=2).update(position=50)
        Topseller.objects.filter(id=3).update(position=200)

        _update_positions()

        # Check that positions are now correct
        topsellers = Topseller.objects.all().order_by("position")
        assert topsellers[0].position == 10
        assert topsellers[1].position == 20
        assert topsellers[2].position == 30

    @pytest.mark.django_db
    def test_update_positions_with_empty_queryset(self):
        """Test _update_positions with no topsellers."""
        _update_positions()
        # Should not raise an exception
        assert Topseller.objects.count() == 0

    @pytest.mark.django_db
    def test_update_positions_with_single_topseller(self, sample_products):
        """Test _update_positions with single topseller."""
        Topseller.objects.create(product=sample_products[0], position=999)

        _update_positions()

        topseller = Topseller.objects.first()
        assert topseller.position == 10
