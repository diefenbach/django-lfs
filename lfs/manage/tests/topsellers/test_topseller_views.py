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
from lfs.manage.topsellers.views import (
    ManageTopsellerView,
    AddTopsellerView,
    RemoveTopsellerView,
    SortTopsellerView,
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

    # Mock session with session_key attribute and proper dict-like behavior
    class MockSession(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.session_key = "test_session_key"

        def get(self, key, default=None):
            return super().get(key, default)

        def __setitem__(self, key, value):
            super().__setitem__(key, value)

        def __getitem__(self, key):
            return super().__getitem__(key)

        def __contains__(self, key):
            return super().__contains__(key)

    request.session = MockSession()

    # Mock messages framework for unit tests
    class MockMessages:
        def __init__(self):
            self.messages = []

        def success(self, msg):
            pass

        def error(self, msg):
            pass

        def add(self, level, message, extra_tags=""):
            pass

        def __iter__(self):
            return iter([])

        def __len__(self):
            return 0

    request._messages = MockMessages()
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
        # Ensure session has topseller-amount
        view.request.session["topseller-amount"] = 25

        with patch("lfs.manage.topsellers.views.Paginator") as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_paginator.return_value.page.return_value = mock_page
            mock_paginator.return_value.num_pages = 1

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
        # Ensure session has topseller-amount
        view.request.session["topseller-amount"] = 25

        with patch("lfs.manage.topsellers.views.Paginator") as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_paginator.return_value.page.return_value = mock_page
            mock_paginator.return_value.num_pages = 1

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
        # Ensure session has topseller-amount
        view.request.session["topseller-amount"] = 25

        with patch("lfs.manage.topsellers.views.Paginator") as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_paginator.return_value.page.return_value = mock_page
            mock_paginator.return_value.num_pages = 1

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
        # Ensure session has topseller-amount
        view.request.session["topseller-amount"] = 25

        with patch("lfs.manage.topsellers.views.Paginator") as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_paginator.return_value.page.return_value = mock_page
            mock_paginator.return_value.num_pages = 1

            context = view.get_context_data()

        assert context["filter"] == "SKU-004"
        assert context["total"] == 1  # One product matches SKU-004

    @pytest.mark.django_db
    def test_get_context_data_with_category_filter(
        self, mock_request, admin_user, sample_products, sample_categories, sample_topsellers
    ):
        """Test context data with category filter applied."""
        # Add product to category - use product that is NOT in topsellers
        sample_products[3].categories.add(sample_categories[0])

        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"topseller_category_filter": str(sample_categories[0].id)}
        # Ensure session has topseller-amount
        view.request.session["topseller-amount"] = 25

        with patch("lfs.manage.topsellers.views.Paginator") as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_paginator.return_value.page.return_value = mock_page
            mock_paginator.return_value.num_pages = 1

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
        # Ensure session has topseller-amount
        view.request.session["topseller-amount"] = 25

        with patch("lfs.manage.topsellers.views.Paginator") as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_paginator.return_value.page.return_value = mock_page
            mock_paginator.return_value.num_pages = 1

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
        # Ensure session has topseller-amount
        view.request.session["topseller-amount"] = 25

        with patch("lfs.manage.topsellers.views.Paginator") as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_paginator.return_value.page.return_value = mock_page
            mock_paginator.return_value.num_pages = 1

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


class TestManageTopsellerView:
    """Test ManageTopsellerView class."""

    @pytest.mark.django_db
    def test_manage_topseller_view_returns_http_response(self, mock_request, admin_user, sample_topsellers):
        """Test that ManageTopsellerView returns HTTP response."""
        mock_request.user = admin_user
        # Set session data without overriding the MockSession
        mock_request.session["topseller-amount"] = 25

        view = ManageTopsellerView()
        view.request = mock_request

        with patch("lfs.manage.topsellers.views.ManageTopsellerView.get_context_data") as mock_get_context:
            mock_get_context.return_value = {"topseller": sample_topsellers}
            with patch("django.template.loader.render_to_string", return_value="rendered template"):
                response = view.get(mock_request)
                response.render()  # Render the template response

                assert response.status_code == 200
                assert "Test Product 1" in response.content.decode()

    @pytest.mark.django_db
    def test_manage_topseller_view_uses_correct_template(self, mock_request, admin_user, sample_topsellers):
        """Test ManageTopsellerView uses correct template."""
        mock_request.user = admin_user
        mock_request.session = {"topseller-amount": 25}

        view = ManageTopsellerView()
        assert view.template_name == "manage/topsellers/topseller.html"


class TestManageTopsellerInlineView:
    """Test inline topseller functionality."""

    @pytest.mark.django_db
    def test_manage_topseller_inline_not_implemented(self, mock_request, admin_user, sample_topsellers):
        """Test that inline functionality is not currently implemented."""
        # Note: The inline functionality appears to have been removed in the class-based refactor
        # This test documents that the inline view is not available
        from lfs.manage.topsellers.views import ManageTopsellerView

        view = ManageTopsellerView()
        # The view only supports full page rendering, not inline partials
        assert not hasattr(view, "render_inline")


class TestAddTopsellerView:
    """Test AddTopsellerView class."""

    @pytest.mark.django_db
    def test_add_topseller_view_with_valid_products(self, mock_request, admin_user, sample_products):
        """Test adding valid products to topseller using AddTopsellerView."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "product-1": "1",
            "product-2": "2",
        }

        view = AddTopsellerView()
        view.request = mock_request

        # Call the post method
        response = view.post(mock_request)

        # Check that topsellers were created
        assert Topseller.objects.count() == 2
        assert Topseller.objects.filter(product_id=1).exists()
        assert Topseller.objects.filter(product_id=2).exists()

        # Check redirect response
        assert response.status_code == 302
        assert "/manage/topseller" in response.url

    @pytest.mark.django_db
    def test_add_topseller_view_ignores_invalid_keys(self, mock_request, admin_user, sample_products):
        """Test that AddTopsellerView ignores non-product keys."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "product-1": "1",
            "invalid-key": "value",
            "other-key": "value",
        }

        view = AddTopsellerView()
        view.request = mock_request

        response = view.post(mock_request)

        # Only one topseller should be created
        assert Topseller.objects.count() == 1
        assert Topseller.objects.filter(product_id=1).exists()

        # Check redirect response
        assert response.status_code == 302


class TestRemoveTopsellerView:
    """Test RemoveTopsellerView class."""

    @pytest.mark.django_db
    def test_remove_topseller_view_remove_action(self, mock_request, admin_user, sample_topsellers):
        """Test removing topseller products using RemoveTopsellerView."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "action": "remove",
            "product-1": str(sample_topsellers[0].pk),
            "product-2": str(sample_topsellers[1].pk),
        }

        view = RemoveTopsellerView()
        view.request = mock_request

        initial_count = Topseller.objects.count()
        response = view.post(mock_request)

        # Check that topsellers were removed
        assert Topseller.objects.count() == initial_count - 2
        # Check redirect response
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_remove_topseller_view_ignores_invalid_keys(self, mock_request, admin_user, sample_topsellers):
        """Test that RemoveTopsellerView ignores non-product keys."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "action": "remove",
            "product-1": str(sample_topsellers[0].pk),
            "invalid-key": "value",
        }

        view = RemoveTopsellerView()
        view.request = mock_request

        initial_count = Topseller.objects.count()
        response = view.post(mock_request)

        # Only one topseller should be removed
        assert Topseller.objects.count() == initial_count - 1

    @pytest.mark.django_db
    def test_remove_topseller_view_handles_nonexistent_topseller(self, mock_request, admin_user):
        """Test that RemoveTopsellerView handles nonexistent topseller gracefully."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "action": "remove",
            "product-999": "999",  # Non-existent ID
        }

        view = RemoveTopsellerView()
        view.request = mock_request

        # Should not raise an exception
        response = view.post(mock_request)
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_remove_topseller_view_without_remove_action(self, mock_request, admin_user, sample_topsellers):
        """Test RemoveTopsellerView without remove action does nothing."""
        mock_request.user = admin_user
        mock_request.method = "POST"
        mock_request.POST = {
            "product-1": str(sample_topsellers[0].pk),
        }

        view = RemoveTopsellerView()
        view.request = mock_request

        initial_count = Topseller.objects.count()
        response = view.post(mock_request)

        # No topsellers should be removed (no "action": "remove")
        assert Topseller.objects.count() == initial_count
        assert response.status_code == 302


class TestSortTopsellerView:
    """Test SortTopsellerView class."""

    @pytest.mark.django_db
    def test_sort_topseller_view_with_valid_data(self, mock_request, admin_user, sample_topsellers):
        """Test sorting topseller products with valid data using SortTopsellerView."""
        mock_request.user = admin_user
        mock_request.method = "POST"

        # Create request with JSON body using a custom approach
        from django.test import RequestFactory

        factory = RequestFactory()
        request_data = json.dumps(
            {"topseller_ids": [sample_topsellers[1].pk, sample_topsellers[0].pk, sample_topsellers[2].pk]}
        )
        request = factory.post("/", data=request_data, content_type="application/json")
        request.user = admin_user

        view = SortTopsellerView()
        view.request = request

        result = view.post(request)

        assert isinstance(result, HttpResponse)

        # Check that positions were updated
        topseller1 = Topseller.objects.get(id=sample_topsellers[0].pk)
        topseller2 = Topseller.objects.get(id=sample_topsellers[1].pk)
        topseller3 = Topseller.objects.get(id=sample_topsellers[2].pk)

        assert topseller2.position == 10  # First in new order
        assert topseller1.position == 20  # Second in new order
        assert topseller3.position == 30  # Third in new order

    @pytest.mark.django_db
    def test_sort_topseller_view_with_invalid_data(self, mock_request, admin_user, sample_topsellers):
        """Test sorting topseller products with invalid data using SortTopsellerView."""
        mock_request.user = admin_user
        mock_request.method = "POST"

        # Create request with invalid JSON body
        from django.test import RequestFactory

        factory = RequestFactory()
        request_data = json.dumps({"topseller_ids": [999, 998]})
        request = factory.post("/", data=request_data, content_type="application/json")
        request.user = admin_user

        view = SortTopsellerView()
        view.request = request

        result = view.post(request)

        assert isinstance(result, HttpResponse)
        # Should not raise an exception

    @pytest.mark.django_db
    def test_sort_topseller_view_with_empty_data(self, mock_request, admin_user, sample_topsellers):
        """Test sorting topseller products with empty data using SortTopsellerView."""
        mock_request.user = admin_user
        mock_request.method = "POST"

        # Create request with empty JSON body
        from django.test import RequestFactory

        factory = RequestFactory()
        request_data = json.dumps({"topseller_ids": []})
        request = factory.post("/", data=request_data, content_type="application/json")
        request.user = admin_user

        view = SortTopsellerView()
        view.request = request

        result = view.post(request)

        assert isinstance(result, HttpResponse)
        # Should not raise an exception

    @pytest.mark.django_db
    def test_sort_topseller_view_with_missing_topseller_ids(self, mock_request, admin_user, sample_topsellers):
        """Test sorting topseller products with missing topseller_ids key using SortTopsellerView."""
        mock_request.user = admin_user
        mock_request.method = "POST"

        # Create request with missing topseller_ids key
        from django.test import RequestFactory

        factory = RequestFactory()
        request_data = json.dumps({})
        request = factory.post("/", data=request_data, content_type="application/json")
        request.user = admin_user

        view = SortTopsellerView()
        view.request = request

        result = view.post(request)

        assert isinstance(result, HttpResponse)
        # Should not raise an exception


class TestUpdatePositionsUtility:
    """Test _update_positions utility function."""

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
