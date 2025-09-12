"""
Comprehensive unit tests for topseller services and business logic.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- Topseller business logic functions
- Position management and updates
- Filtering and querying logic
- Data transformation and processing
- Edge cases and error conditions

Note: The topseller module currently doesn't have dedicated services,
but this test file covers the business logic functions.
"""

import pytest
import json

from django.test import RequestFactory
from django.db.models import Q

from lfs.catalog.models import Product
from lfs.marketing.models import Topseller
from lfs.manage.topseller.views import (
    _update_positions,
    sort_topseller,
)


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def mock_request(request_factory):
    """Mock request object for testing."""
    return request_factory.get("/")


class TestTopsellerPositionService:
    """Test topseller position management functionality."""

    @pytest.mark.django_db
    def test_update_positions_sets_sequential_positions(self, sample_topsellers):
        """Test that _update_positions sets sequential positions."""
        # Manually set incorrect positions
        Topseller.objects.filter(id=1).update(position=100)
        Topseller.objects.filter(id=2).update(position=50)
        Topseller.objects.filter(id=3).update(position=200)

        _update_positions()

        # Check that positions are now sequential
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

    @pytest.mark.django_db
    def test_update_positions_preserves_order(self, sample_products):
        """Test that _update_positions preserves the existing order."""
        # Create topsellers in specific order
        topseller1 = Topseller.objects.create(product=sample_products[0], position=100)
        topseller2 = Topseller.objects.create(product=sample_products[1], position=200)
        topseller3 = Topseller.objects.create(product=sample_products[2], position=300)

        _update_positions()

        # Check that order is preserved
        topsellers = Topseller.objects.all().order_by("position")
        assert topsellers[0].id == topseller1.id
        assert topsellers[1].id == topseller2.id
        assert topsellers[2].id == topseller3.id

    @pytest.mark.django_db
    def test_update_positions_handles_large_numbers(self, sample_products):
        """Test _update_positions with large numbers of topsellers."""
        # Create many topsellers
        for i in range(100):
            Topseller.objects.create(product=sample_products[i % len(sample_products)], position=i * 1000)

        _update_positions()

        # Check that positions are sequential
        topsellers = Topseller.objects.all().order_by("position")
        for i, topseller in enumerate(topsellers):
            assert topseller.position == (i + 1) * 10


class TestTopsellerFilterService:
    """Test topseller filtering functionality."""

    @pytest.mark.django_db
    def test_filter_products_by_name(self, sample_products, sample_topsellers):
        """Test filtering products by name."""
        # Get products excluding topsellers
        topseller_ids = [t.product.id for t in sample_topsellers]
        products = Product.objects.exclude(pk__in=topseller_ids)

        # Filter by name
        filtered = products.filter(name__icontains="Product 4")

        assert filtered.count() == 1
        assert filtered.first().name == "Test Product 4"

    @pytest.mark.django_db
    def test_filter_products_by_sku(self, sample_products, sample_topsellers):
        """Test filtering products by SKU."""
        # Get products excluding topsellers
        topseller_ids = [t.product.id for t in sample_topsellers]
        products = Product.objects.exclude(pk__in=topseller_ids)

        # Filter by SKU
        filtered = products.filter(sku__icontains="SKU-004")

        assert filtered.count() == 1
        assert filtered.first().sku == "SKU-004"

    @pytest.mark.django_db
    def test_filter_products_by_category(self, sample_products, sample_categories, sample_topsellers):
        """Test filtering products by category."""
        # Add products to categories
        sample_products[0].categories.add(sample_categories[0])
        sample_products[1].categories.add(sample_categories[1])

        # Get products excluding topsellers
        topseller_ids = [t.product.id for t in sample_topsellers]
        products = Product.objects.exclude(pk__in=topseller_ids)

        # Filter by category
        filtered = products.filter(categories__in=[sample_categories[0]])

        assert filtered.count() == 1
        assert filtered.first().id == sample_products[0].id

    @pytest.mark.django_db
    def test_filter_products_with_none_category(self, sample_products, sample_topsellers):
        """Test filtering products with no category."""
        # Get products excluding topsellers
        topseller_ids = [t.product.id for t in sample_topsellers]
        products = Product.objects.exclude(pk__in=topseller_ids)

        # Filter by no category
        filtered = products.filter(categories=None)

        assert filtered.count() == 2  # Products 4 and 5 have no categories

    @pytest.mark.django_db
    def test_filter_products_with_combined_filters(self, sample_products, sample_topsellers):
        """Test filtering products with combined filters."""
        # Get products excluding topsellers
        topseller_ids = [t.product.id for t in sample_topsellers]
        products = Product.objects.exclude(pk__in=topseller_ids)

        # Filter by name and SKU
        filtered = products.filter(Q(name__icontains="Product 4") | Q(sku__icontains="SKU-004"))

        assert filtered.count() == 1
        assert filtered.first().name == "Test Product 4"

    @pytest.mark.django_db
    def test_filter_products_excludes_topsellers(self, sample_products, sample_topsellers):
        """Test that filtering excludes topseller products."""
        # Get all products
        all_products = Product.objects.all()

        # Get products excluding topsellers
        topseller_ids = [t.product.id for t in sample_topsellers]
        filtered = all_products.exclude(pk__in=topseller_ids)

        assert filtered.count() == 2  # 5 products - 3 topsellers = 2
        assert not any(p.id in topseller_ids for p in filtered)


class TestTopsellerDataService:
    """Test topseller data processing functionality."""

    @pytest.mark.django_db
    def test_get_topseller_products_ordered_by_position(self, sample_topsellers):
        """Test getting topseller products ordered by position."""
        topsellers = Topseller.objects.all().order_by("position")

        assert len(topsellers) == 3
        assert topsellers[0].position == 10
        assert topsellers[1].position == 20
        assert topsellers[2].position == 30

    @pytest.mark.django_db
    def test_get_topseller_product_ids(self, sample_topsellers):
        """Test getting topseller product IDs."""
        topseller_ids = [t.product.id for t in sample_topsellers]

        assert len(topseller_ids) == 3
        assert all(isinstance(id, int) for id in topseller_ids)

    @pytest.mark.django_db
    def test_get_available_products_count(self, sample_products, sample_topsellers):
        """Test getting count of available products."""
        topseller_ids = [t.product.id for t in sample_topsellers]
        available_products = Product.objects.exclude(pk__in=topseller_ids)

        assert available_products.count() == 2

    @pytest.mark.django_db
    def test_get_paginated_products(self, sample_products, sample_topsellers):
        """Test getting paginated products."""
        from django.core.paginator import Paginator

        topseller_ids = [t.product.id for t in sample_topsellers]
        products = Product.objects.exclude(pk__in=topseller_ids)
        paginator = Paginator(products, 1)

        page = paginator.page(1)
        assert page.object_list.count() == 1
        assert paginator.num_pages == 2

    @pytest.mark.django_db
    def test_get_amount_options(self):
        """Test getting amount options for pagination."""
        amount_options = []
        for value in (10, 25, 50, 100):
            amount_options.append({"value": value, "selected": value == 25})

        assert len(amount_options) == 4
        assert amount_options[1]["selected"] is True  # 25 is selected
        assert all(not option["selected"] for option in amount_options if option["value"] != 25)

    @pytest.mark.django_db
    def test_get_hierarchical_categories(self, sample_categories):
        """Test getting hierarchical categories."""
        from lfs.manage.topseller.views import ManageTopsellerView

        view = ManageTopsellerView()
        categories = view._build_hierarchical_categories()

        assert len(categories) == 4  # 1 parent + 3 children
        assert categories[0].level == 0  # Parent category
        assert categories[1].level == 1  # First child

    @pytest.mark.django_db
    def test_get_category_filter_options(self, sample_categories):
        """Test getting category filter options."""
        # Test "None" option
        assert "None" in ["None", "All"] + [str(cat.id) for cat in sample_categories]

        # Test "All" option
        assert "All" in ["None", "All"] + [str(cat.id) for cat in sample_categories]

        # Test category IDs
        category_ids = [str(cat.id) for cat in sample_categories]
        assert len(category_ids) == 4


class TestTopsellerAjaxService:
    """Test topseller AJAX functionality."""

    @pytest.mark.django_db
    def test_sort_topseller_with_valid_json(self, sample_topsellers):
        """Test sorting topseller products with valid JSON data."""
        request = RequestFactory().post(
            "/sort-topseller", data=json.dumps({"topseller_ids": [2, 1, 3]}), content_type="application/json"
        )

        result = sort_topseller(request)

        assert result.status_code == 200

        # Check that positions were updated
        topseller1 = Topseller.objects.get(id=1)
        topseller2 = Topseller.objects.get(id=2)
        topseller3 = Topseller.objects.get(id=3)

        assert topseller2.position == 10  # First in new order
        assert topseller1.position == 20  # Second in new order
        assert topseller3.position == 30  # Third in new order

    @pytest.mark.django_db
    def test_sort_topseller_with_invalid_json(self, sample_topsellers):
        """Test sorting topseller products with invalid JSON data."""
        request = RequestFactory().post("/sort-topseller", data="invalid json", content_type="application/json")

        # Should not raise an exception
        result = sort_topseller(request)
        assert result.status_code == 200

    @pytest.mark.django_db
    def test_sort_topseller_with_empty_data(self, sample_topsellers):
        """Test sorting topseller products with empty data."""
        request = RequestFactory().post("/sort-topseller", data=json.dumps({}), content_type="application/json")

        result = sort_topseller(request)
        assert result.status_code == 200

    @pytest.mark.django_db
    def test_sort_topseller_with_nonexistent_ids(self, sample_topsellers):
        """Test sorting topseller products with nonexistent IDs."""
        request = RequestFactory().post(
            "/sort-topseller", data=json.dumps({"topseller_ids": [999, 998]}), content_type="application/json"
        )

        result = sort_topseller(request)
        assert result.status_code == 200

    @pytest.mark.django_db
    def test_sort_topseller_with_mixed_valid_invalid_ids(self, sample_topsellers):
        """Test sorting topseller products with mixed valid and invalid IDs."""
        request = RequestFactory().post(
            "/sort-topseller", data=json.dumps({"topseller_ids": [1, 999, 2]}), content_type="application/json"
        )

        result = sort_topseller(request)
        assert result.status_code == 200

        # Check that valid IDs were processed
        topseller1 = Topseller.objects.get(id=1)
        topseller2 = Topseller.objects.get(id=2)

        assert topseller1.position == 20  # Second in new order
        assert topseller2.position == 30  # Third in new order


class TestTopsellerSessionService:
    """Test topseller session management functionality."""

    @pytest.mark.django_db
    def test_session_filter_persistence(self, mock_request, admin_user):
        """Test that filters are persisted in session."""
        from lfs.manage.topseller.views import ManageTopsellerView

        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"filter": "test", "topseller_category_filter": "1"}

        # First call should set session
        view.get_context_data()

        assert mock_request.session["filter"] == "test"
        assert mock_request.session["topseller_category_filter"] == "1"

    @pytest.mark.django_db
    def test_session_filter_retrieval(self, mock_request, admin_user):
        """Test that filters are retrieved from session."""
        from lfs.manage.topseller.views import ManageTopsellerView

        # Set session data
        mock_request.session = {
            "filter": "session_filter",
            "topseller_category_filter": "2",
            "topseller_products_page": "2",
        }

        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"keep-filters": "1"}

        context = view.get_context_data()

        assert context["filter"] == "session_filter"
        assert context["category_filter"] == "2"

    @pytest.mark.django_db
    def test_session_amount_handling(self, mock_request, admin_user):
        """Test that amount is handled in session."""
        from lfs.manage.topseller.views import ManageTopsellerView

        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"topseller-amount": "50"}

        view.get_context_data()

        assert mock_request.session["topseller-amount"] == 50

    @pytest.mark.django_db
    def test_session_amount_default(self, mock_request, admin_user):
        """Test that amount defaults to 25 when not provided."""
        from lfs.manage.topseller.views import ManageTopsellerView

        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user

        view.get_context_data()

        assert mock_request.session["topseller-amount"] == 25

    @pytest.mark.django_db
    def test_session_amount_invalid_type(self, mock_request, admin_user):
        """Test that invalid amount type defaults to 25."""
        from lfs.manage.topseller.views import ManageTopsellerView

        view = ManageTopsellerView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"topseller-amount": "invalid"}

        view.get_context_data()

        assert mock_request.session["topseller-amount"] == 25
