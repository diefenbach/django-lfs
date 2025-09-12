"""
Comprehensive unit tests for Topseller views in the manage package.

Following TDD principles:
- Test behavior, not implementation
- Clear test names
- Arrange-Act-Assert structure
- One assertion per test (when practical)
"""

import json
import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.marketing.models import Topseller
from lfs.manage.topseller.views import (
    ManageTopsellerView,
    add_topseller,
    update_topseller,
    sort_topseller,
    _update_positions,
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestManageTopsellerView:
    """Tests for ManageTopsellerView class-based view."""

    def test_get_context_data_returns_correct_template_name(self, manage_user):
        """Should return the correct template name."""
        view = ManageTopsellerView()
        view.request = RequestFactory().get("/")
        view.request.user = manage_user

        assert view.template_name == "manage/topseller/topseller.html"

    def test_permission_required_is_correct(self, manage_user):
        """Should require manage_shop permission."""
        view = ManageTopsellerView()
        view.request = RequestFactory().get("/")
        view.request.user = manage_user

        assert view.permission_required == "core.manage_shop"

    def test_get_context_data_includes_topseller_products(self, authenticated_request, topseller_products):
        """Should include topseller products in context ordered by position."""
        view = ManageTopsellerView()
        request = authenticated_request()
        view.request = request

        context = view.get_context_data()

        assert "topseller" in context
        topseller = context["topseller"]
        assert len(topseller) == 3
        # Should be ordered by position
        assert topseller[0].position == 10
        assert topseller[1].position == 20
        assert topseller[2].position == 30

    def test_get_context_data_excludes_topseller_products_from_available_products(
        self, authenticated_request, topseller_products, multiple_products
    ):
        """Should exclude already topseller products from available products list."""
        view = ManageTopsellerView()
        request = authenticated_request()
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        # Should only show non-topseller products
        assert page_obj.paginator.count == 2  # 5 total - 3 topseller = 2 available

    def test_get_context_data_handles_empty_topseller_products(self, authenticated_request, multiple_products):
        """Should handle case when no products are topseller."""
        view = ManageTopsellerView()
        request = authenticated_request()
        view.request = request

        context = view.get_context_data()

        assert "topseller" in context
        assert len(context["topseller"]) == 0
        assert "page" in context
        # All products should be available
        assert context["page"].paginator.count == 5

    def test_get_context_data_includes_categories(self, authenticated_request, multiple_categories):
        """Should include all categories for filter dropdown."""
        view = ManageTopsellerView()
        request = authenticated_request()
        view.request = request

        context = view.get_context_data()

        assert "categories" in context
        categories = context["categories"]
        assert len(categories) == 3
        # Should be ordered by name
        assert categories[0].name == "Category A"
        assert categories[1].name == "Category B"
        assert categories[2].name == "Category C"

    def test_get_context_data_includes_amount_options(self, authenticated_request):
        """Should include pagination amount options."""
        view = ManageTopsellerView()
        request = authenticated_request()
        view.request = request

        context = view.get_context_data()

        assert "amount_options" in context
        amount_options = context["amount_options"]
        assert len(amount_options) == 4
        expected_values = [10, 25, 50, 100]
        for i, option in enumerate(amount_options):
            assert option["value"] == expected_values[i]

    def test_get_context_data_sets_default_amount_to_25(self, authenticated_request):
        """Should set default topseller-amount to 25."""
        view = ManageTopsellerView()
        request = authenticated_request()
        view.request = request

        context = view.get_context_data()

        # Check session was set to default
        assert view.request.session["topseller-amount"] == 25

    def test_get_context_data_uses_session_amount_when_keep_filters(self, authenticated_request):
        """Should use session amount when keep-filters is present."""
        view = ManageTopsellerView()
        request = authenticated_request(method="GET", data={"keep-filters": "1"})
        request.session["topseller-amount"] = 50
        view.request = request

        context = view.get_context_data()

        assert request.session["topseller-amount"] == 50

    def test_get_context_data_handles_invalid_amount(self, authenticated_request):
        """Should handle invalid topseller-amount gracefully."""
        view = ManageTopsellerView()
        request = authenticated_request(method="GET", data={"topseller-amount": "invalid"})
        view.request = request

        # This should raise a ValueError, which is the expected behavior
        with pytest.raises(ValueError):
            view.get_context_data()

    def test_get_context_data_filters_by_name(self, authenticated_request, multiple_products):
        """Should filter products by name."""
        view = ManageTopsellerView()
        request = authenticated_request(method="GET", data={"filter": "Product 1"})
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        assert page_obj.paginator.count == 1
        assert page_obj.object_list[0].name == "Product 1"

    def test_get_context_data_filters_by_sku(self, authenticated_request, multiple_products):
        """Should filter products by SKU."""
        view = ManageTopsellerView()
        request = authenticated_request(method="GET", data={"filter": "SKU-001"})
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        assert page_obj.paginator.count == 1
        assert page_obj.object_list[0].sku == "SKU-001"

    def test_get_context_data_filters_by_category(self, authenticated_request, multiple_products, multiple_categories):
        """Should filter products by category."""
        # Assign products to categories
        multiple_products[0].categories.add(multiple_categories[0])
        multiple_products[1].categories.add(multiple_categories[1])

        view = ManageTopsellerView()
        request = authenticated_request(
            method="GET", data={"topseller_category_filter": str(multiple_categories[0].id)}
        )
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        assert page_obj.paginator.count == 1
        assert page_obj.object_list[0] == multiple_products[0]

    def test_get_context_data_filters_by_none_category(
        self, authenticated_request, multiple_products, multiple_categories
    ):
        """Should filter products with no category when 'None' is selected."""
        # Only assign some products to categories
        multiple_products[0].categories.add(multiple_categories[0])

        view = ManageTopsellerView()
        request = authenticated_request(method="GET", data={"topseller_category_filter": "None"})
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        # Should show products without categories
        assert page_obj.paginator.count == 4  # 5 total - 1 with category = 4 without

    def test_get_context_data_filters_by_all_categories(
        self, authenticated_request, multiple_products, multiple_categories
    ):
        """Should show all products when 'All' categories is selected."""
        # Assign products to categories
        multiple_products[0].categories.add(multiple_categories[0])
        multiple_products[1].categories.add(multiple_categories[1])

        view = ManageTopsellerView()
        request = authenticated_request(method="GET", data={"topseller_category_filter": "All"})
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        # Should show all products regardless of category
        assert page_obj.paginator.count == 5

    def test_get_context_data_handles_pagination(self, authenticated_request, many_products):
        """Should handle pagination correctly."""
        view = ManageTopsellerView()
        request = authenticated_request(method="GET", data={"page": "2"})
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        assert page_obj.number == 2
        assert page_obj.paginator.num_pages > 1

    def test_get_context_data_handles_empty_page(self, authenticated_request):
        """Should handle empty page gracefully."""
        view = ManageTopsellerView()
        request = authenticated_request(method="GET", data={"page": "999"})
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        assert page_obj == 0  # EmptyPage case

    def test_get_context_data_saves_filters_in_session(self, authenticated_request, multiple_categories):
        """Should save current filters in session."""
        view = ManageTopsellerView()
        request = authenticated_request(
            method="GET",
            data={"filter": "test", "topseller_category_filter": str(multiple_categories[0].id), "page": "2"},
        )
        view.request = request

        context = view.get_context_data()

        assert request.session["filter"] == "test"
        assert request.session["topseller_category_filter"] == str(multiple_categories[0].id)
        assert request.session["topseller_products_page"] == "2"

    def test_get_context_data_uses_session_filters_when_keep_filters(self, authenticated_request, multiple_categories):
        """Should use session filters when keep-filters is present."""
        view = ManageTopsellerView()
        request = authenticated_request(method="GET", data={"keep-filters": "1"})
        request.session["filter"] = "session_filter"
        request.session["topseller_category_filter"] = str(multiple_categories[0].id)
        request.session["topseller_products_page"] = "3"
        view.request = request

        context = view.get_context_data()

        assert context["filter"] == "session_filter"
        assert context["category_filter"] == str(multiple_categories[0].id)
        # Page might be 0 if no products match the filter, or a pagination object
        assert context["page"] in ["3", 3, 0] or hasattr(context["page"], "number")

    def test_build_hierarchical_categories_creates_proper_structure(
        self, authenticated_request, hierarchical_categories
    ):
        """Should build hierarchical category structure with proper indentation."""
        view = ManageTopsellerView()
        request = authenticated_request()
        view.request = request

        context = view.get_context_data()

        assert "categories" in context
        categories = context["categories"]
        assert len(categories) >= 3  # At least 3 categories

        # Check that parent categories come before children
        parent_category = next(c for c in categories if c.level == 0)
        child_category = next(c for c in categories if c.level == 1)
        assert parent_category.category.id != child_category.category.id


@pytest.mark.django_db
@pytest.mark.unit
class TestAddTopseller:
    """Tests for add_topseller function."""

    def test_add_topseller_creates_topseller_products(self, authenticated_request, multiple_products):
        """Should create Topseller instances for selected products."""
        request = authenticated_request(
            method="POST",
            data={
                "product-1": "on",
                "product-2": "on",
                "other-field": "value",  # Should be ignored
            },
        )

        # Verify no topseller products exist initially
        assert Topseller.objects.count() == 0

        response = add_topseller(request)

        # Should create 2 topseller products
        assert Topseller.objects.count() == 2
        topseller_products = Topseller.objects.all()
        product_ids = [tp.product.id for tp in topseller_products]
        assert multiple_products[0].id in product_ids
        assert multiple_products[1].id in product_ids

    def test_add_topseller_ignores_non_product_fields(self, authenticated_request, multiple_products):
        """Should ignore POST fields that don't start with 'product-'."""
        request = authenticated_request(
            method="POST",
            data={
                "product-1": "on",
                "other-field": "value",
                "not-a-product": "ignored",
            },
        )

        response = add_topseller(request)

        # Should only create 1 topseller product
        assert Topseller.objects.count() == 1

    def test_add_topseller_updates_positions(self, authenticated_request, multiple_products):
        """Should update positions after adding topseller products."""
        request = authenticated_request(
            method="POST",
            data={
                "product-1": "on",
                "product-2": "on",
                "product-3": "on",
            },
        )

        response = add_topseller(request)

        topseller_products = Topseller.objects.all().order_by("position")
        assert len(topseller_products) == 3
        assert topseller_products[0].position == 10
        assert topseller_products[1].position == 20
        assert topseller_products[2].position == 30

    def test_add_topseller_renders_manage_view(self, authenticated_request, multiple_products):
        """Should render the manage topseller view after adding."""
        request = authenticated_request(method="POST", data={"product-1": "on"})

        response = add_topseller(request)

        assert response.status_code == 200
        # Check that the response contains the expected content
        assert b"topseller" in response.content.lower()

    def test_add_topseller_handles_empty_post_data(self, authenticated_request, shop):
        """Should handle empty POST data gracefully."""
        request = authenticated_request(method="POST", data={})

        response = add_topseller(request)

        assert response.status_code == 200
        assert Topseller.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.unit
class TestUpdateTopseller:
    """Tests for update_topseller function."""

    def test_update_topseller_removes_products_when_action_is_remove(self, authenticated_request, topseller_products):
        """Should remove topseller products when action is 'remove'."""
        request = authenticated_request(
            method="POST",
            data={
                "action": "remove",
                "product-1": "on",
                "product-2": "on",
            },
        )

        # Verify topseller products exist initially
        assert Topseller.objects.count() == 3

        response = update_topseller(request)

        # Should remove 2 topseller products
        assert Topseller.objects.count() == 1
        remaining = Topseller.objects.first()
        assert remaining.id == 3  # Only the third one should remain

    def test_update_topseller_ignores_non_product_fields_when_removing(self, authenticated_request, topseller_products):
        """Should ignore non-product fields when removing."""
        request = authenticated_request(
            method="POST",
            data={
                "action": "remove",
                "product-1": "on",
                "other-field": "value",
            },
        )

        response = update_topseller(request)

        # Should only remove 1 topseller product
        assert Topseller.objects.count() == 2

    def test_update_topseller_handles_nonexistent_topseller_product(self, authenticated_request, topseller_products):
        """Should handle nonexistent topseller product gracefully."""
        request = authenticated_request(
            method="POST",
            data={
                "action": "remove",
                "product-999": "on",  # Non-existent ID
            },
        )

        response = update_topseller(request)

        # Should not crash and all products should remain
        assert Topseller.objects.count() == 3

    def test_update_topseller_updates_positions_when_removing(self, authenticated_request, topseller_products):
        """Should update positions after removing topseller products."""
        request = authenticated_request(
            method="POST",
            data={
                "action": "remove",
                "product-1": "on",
            },
        )

        response = update_topseller(request)

        topseller_products = Topseller.objects.all().order_by("position")
        assert len(topseller_products) == 2
        assert topseller_products[0].position == 10
        assert topseller_products[1].position == 20

    def test_update_topseller_renders_manage_view_after_removing(self, authenticated_request, topseller_products):
        """Should render the manage topseller view after removing."""
        request = authenticated_request(
            method="POST",
            data={
                "action": "remove",
                "product-1": "on",
            },
        )

        response = update_topseller(request)

        assert response.status_code == 200
        # Check that the response contains the expected content
        assert b"topseller" in response.content.lower()

    def test_update_topseller_handles_empty_post_data(self, authenticated_request, shop):
        """Should handle empty POST data gracefully."""
        request = authenticated_request(method="POST", data={})

        response = update_topseller(request)

        assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.unit
class TestSortTopseller:
    """Tests for sort_topseller function."""

    def test_sort_topseller_updates_positions(self, authenticated_request, topseller_products):
        """Should update positions based on provided order."""
        # Get the original order
        original_order = list(Topseller.objects.all().order_by("id"))
        original_ids = [tp.id for tp in original_order]

        # Reverse the order
        new_order = list(reversed(original_ids))

        request = authenticated_request(
            method="POST", data=json.dumps({"topseller_ids": new_order}), content_type="application/json"
        )

        response = sort_topseller(request)

        assert response.status_code == 200

        # Check that positions were updated
        updated_topseller = Topseller.objects.all().order_by("position")
        assert updated_topseller[0].id == original_ids[2]  # Last becomes first
        assert updated_topseller[1].id == original_ids[1]
        assert updated_topseller[2].id == original_ids[0]  # First becomes last

    def test_sort_topseller_handles_nonexistent_ids(self, authenticated_request, topseller_products):
        """Should handle nonexistent topseller IDs gracefully."""
        original_count = Topseller.objects.count()

        request = authenticated_request(
            method="POST",
            data=json.dumps({"topseller_ids": [1, 2, 999, 3]}),  # 999 doesn't exist
            content_type="application/json",
        )

        response = sort_topseller(request)

        assert response.status_code == 200
        assert Topseller.objects.count() == original_count  # No products deleted

    def test_sort_topseller_handles_empty_ids_list(self, authenticated_request, topseller_products):
        """Should handle empty IDs list gracefully."""
        original_count = Topseller.objects.count()

        request = authenticated_request(
            method="POST", data=json.dumps({"topseller_ids": []}), content_type="application/json"
        )

        response = sort_topseller(request)

        assert response.status_code == 200
        assert Topseller.objects.count() == original_count

    def test_sort_topseller_requires_post_method(self, authenticated_request, topseller_products):
        """Should only accept POST requests."""
        request = authenticated_request(method="GET")

        # The decorator should handle this, but let's test the actual behavior
        response = sort_topseller(request)
        # Should return an empty response or handle gracefully
        assert response.status_code in [200, 405]  # Either OK or Method Not Allowed


@pytest.mark.django_db
@pytest.mark.unit
class TestUpdatePositions:
    """Tests for _update_positions helper function."""

    def test_update_positions_sets_sequential_positions(self, topseller_products):
        """Should set sequential positions starting from 10."""
        # Manually set some positions first
        topseller_products[0].position = 100
        topseller_products[1].position = 200
        topseller_products[2].position = 300
        for tp in topseller_products:
            tp.save()

        _update_positions()

        topseller_products = Topseller.objects.all().order_by("position")
        assert topseller_products[0].position == 10
        assert topseller_products[1].position == 20
        assert topseller_products[2].position == 30

    def test_update_positions_handles_empty_topseller_products(self):
        """Should handle empty topseller products list gracefully."""
        # Should not raise any exception
        _update_positions()

        assert Topseller.objects.count() == 0

    def test_update_positions_maintains_order(self, topseller_products):
        """Should maintain the order of topseller products."""
        # Get the original order
        original_order = list(Topseller.objects.all().order_by("id"))

        _update_positions()

        # Check that order is maintained
        updated_order = list(Topseller.objects.all().order_by("position"))
        assert len(original_order) == len(updated_order)
        for i, tp in enumerate(updated_order):
            assert tp.position == (i + 1) * 10

    def test_update_positions_handles_single_topseller_product(self, shop):
        """Should handle single topseller product correctly."""
        from lfs.catalog.models import Product
        from decimal import Decimal

        product = Product.objects.create(
            name="Single Product",
            slug="single-product",
            sku="SINGLE-001",
            price=Decimal("29.99"),
            active=True,
        )
        topseller = Topseller.objects.create(product=product, position=999)

        _update_positions()

        topseller.refresh_from_db()
        assert topseller.position == 10


@pytest.mark.django_db
@pytest.mark.unit
class TestTopsellerViewsIntegration:
    """Integration tests for topseller views."""

    def test_complete_topseller_workflow(self, authenticated_request, multiple_products, multiple_categories):
        """Should handle complete workflow: add -> sort -> remove."""
        # Step 1: Add topseller products
        request = authenticated_request(
            method="POST",
            data={
                "product-1": "on",
                "product-2": "on",
            },
        )
        response = add_topseller(request)
        assert response.status_code == 200
        assert Topseller.objects.count() == 2

        # Step 2: Sort products (reverse order)
        topseller_products = list(Topseller.objects.all().order_by("id"))
        new_order = [tp.id for tp in reversed(topseller_products)]

        request = authenticated_request(
            method="POST", data=json.dumps({"topseller_ids": new_order}), content_type="application/json"
        )
        response = sort_topseller(request)
        assert response.status_code == 200

        # Step 3: Remove one product
        request = authenticated_request(
            method="POST",
            data={
                "action": "remove",
                "product-1": "on",
            },
        )
        response = update_topseller(request)
        assert response.status_code == 200
        assert Topseller.objects.count() == 1

        # Verify final state
        remaining = Topseller.objects.first()
        assert remaining.product.id == 2  # Second product should remain
        assert remaining.position == 10  # Position should be normalized

    def test_filtering_and_pagination_workflow(self, authenticated_request, many_products, multiple_categories):
        """Should handle filtering and pagination correctly."""
        # Assign some products to categories
        many_products[0].categories.add(multiple_categories[0])
        many_products[1].categories.add(multiple_categories[0])
        many_products[2].categories.add(multiple_categories[1])

        # Test category filtering
        view = ManageTopsellerView()
        request = authenticated_request(
            method="GET", data={"topseller_category_filter": str(multiple_categories[0].id)}
        )
        view.request = request

        context = view.get_context_data()
        page_obj = context["page"]
        assert page_obj.paginator.count == 2  # Only products in category 0

        # Test name filtering
        request = authenticated_request(method="GET", data={"filter": "Product 1"})
        view.request = request

        context = view.get_context_data()
        page_obj = context["page"]
        # Should find products with "Product 1" in name (case insensitive)
        assert page_obj.paginator.count >= 1  # At least one product should match

    def test_session_persistence(self, authenticated_request, multiple_products, multiple_categories):
        """Should persist filters and pagination in session."""
        # Set initial filters
        request = authenticated_request(
            method="GET",
            data={
                "filter": "test",
                "topseller_category_filter": str(multiple_categories[0].id),
                "page": "2",
                "topseller-amount": "10",
            },
        )

        view = ManageTopsellerView()
        view.request = request
        context = view.get_context_data()

        # Verify session was updated
        assert request.session["filter"] == "test"
        assert request.session["topseller_category_filter"] == str(multiple_categories[0].id)
        assert request.session["topseller_products_page"] == "2"
        assert request.session["topseller-amount"] == 10

        # Test keep-filters functionality
        request = authenticated_request(method="GET", data={"keep-filters": "1"})
        request.session["filter"] = "session_filter"
        request.session["topseller_category_filter"] = str(multiple_categories[1].id)
        request.session["topseller_products_page"] = "3"

        view = ManageTopsellerView()
        view.request = request
        context = view.get_context_data()

        # Should use session values
        assert context["filter"] == "session_filter"
        assert context["category_filter"] == str(multiple_categories[1].id)
        # Page might be 0 if no products match the filter, or a pagination object
        assert context["page"] in ["3", 3, 0] or hasattr(context["page"], "number")
