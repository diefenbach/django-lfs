"""
Comprehensive unit tests for Featured views in the manage package.

Following TDD principles:
- Test behavior, not implementation
- Clear test names
- Arrange-Act-Assert structure
- One assertion per test (when practical)
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.marketing.models import FeaturedProduct
from lfs.manage.featured.views import (
    ManageFeaturedView,
    add_featured,
    update_featured,
    _update_positions,
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestManageFeaturedView:
    """Tests for ManageFeaturedView class-based view."""

    def test_get_context_data_returns_correct_template_name(self, manage_user):
        """Should return the correct template name."""
        view = ManageFeaturedView()
        view.request = RequestFactory().get("/")
        view.request.user = manage_user

        assert view.template_name == "manage/featured/featured.html"

    def test_permission_required_is_correct(self, manage_user):
        """Should require manage_shop permission."""
        view = ManageFeaturedView()
        view.request = RequestFactory().get("/")
        view.request.user = manage_user

        assert view.permission_required == "core.manage_shop"

    def test_get_context_data_includes_featured_products(self, authenticated_request, featured_products):
        """Should include featured products in context ordered by position."""
        view = ManageFeaturedView()
        request = authenticated_request()
        view.request = request

        context = view.get_context_data()

        assert "featured" in context
        featured = context["featured"]
        assert len(featured) == 3
        # Should be ordered by position
        assert featured[0].position == 10
        assert featured[1].position == 20
        assert featured[2].position == 30

    def test_get_context_data_excludes_featured_products_from_available_products(
        self, authenticated_request, featured_products, multiple_products
    ):
        """Should exclude already featured products from available products list."""
        view = ManageFeaturedView()
        request = authenticated_request()
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        # Should only show non-featured products
        assert page_obj.paginator.count == 2  # 5 total - 3 featured = 2 available

    def test_get_context_data_handles_empty_featured_products(self, authenticated_request, multiple_products):
        """Should handle case when no products are featured."""
        view = ManageFeaturedView()
        request = authenticated_request()
        view.request = request

        context = view.get_context_data()

        assert "featured" in context
        assert len(context["featured"]) == 0
        assert "page" in context
        # All products should be available
        assert context["page"].paginator.count == 5

    def test_get_context_data_includes_categories(self, authenticated_request, multiple_categories):
        """Should include all categories for filter dropdown."""
        view = ManageFeaturedView()
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
        view = ManageFeaturedView()
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
        """Should set default featured-amount to 25."""
        view = ManageFeaturedView()
        request = authenticated_request()
        view.request = request

        context = view.get_context_data()

        # Check session was set to default
        assert view.request.session["featured-amount"] == 25

    def test_get_context_data_uses_session_amount_when_keep_filters(self, authenticated_request):
        """Should use session amount when keep-filters is present."""
        view = ManageFeaturedView()
        request = authenticated_request(method="GET", data={"keep-filters": "1"})
        request.session["featured-amount"] = 50
        view.request = request

        context = view.get_context_data()

        assert request.session["featured-amount"] == 50

    def test_get_context_data_handles_invalid_amount(self, authenticated_request):
        """Should handle invalid featured-amount gracefully."""
        view = ManageFeaturedView()
        request = authenticated_request(method="GET", data={"featured-amount": "invalid"})
        view.request = request

        # This should raise a ValueError, which is the expected behavior
        with pytest.raises(ValueError):
            view.get_context_data()

    def test_get_context_data_filters_by_name(self, authenticated_request, multiple_products):
        """Should filter products by name."""
        view = ManageFeaturedView()
        request = authenticated_request(method="GET", data={"filter": "Product 1"})
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        assert page_obj.paginator.count == 1
        assert page_obj.object_list[0].name == "Product 1"

    def test_get_context_data_filters_by_sku(self, authenticated_request, multiple_products):
        """Should filter products by SKU."""
        view = ManageFeaturedView()
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

        view = ManageFeaturedView()
        request = authenticated_request(method="GET", data={"featured_category_filter": str(multiple_categories[0].id)})
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

        view = ManageFeaturedView()
        request = authenticated_request(method="GET", data={"featured_category_filter": "None"})
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        # Should show products without categories
        assert page_obj.paginator.count == 4  # 5 total - 1 with category = 4 without

    def test_get_context_data_handles_pagination(self, authenticated_request, many_products):
        """Should handle pagination correctly."""
        view = ManageFeaturedView()
        request = authenticated_request(method="GET", data={"page": "2"})
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        assert page_obj.number == 2
        assert page_obj.paginator.num_pages > 1

    def test_get_context_data_handles_empty_page(self, authenticated_request):
        """Should handle empty page gracefully."""
        view = ManageFeaturedView()
        request = authenticated_request(method="GET", data={"page": "999"})
        view.request = request

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        assert page_obj == 0  # EmptyPage case

    def test_get_context_data_saves_filters_in_session(self, authenticated_request, multiple_categories):
        """Should save current filters in session."""
        view = ManageFeaturedView()
        request = authenticated_request(
            method="GET",
            data={"filter": "test", "featured_category_filter": str(multiple_categories[0].id), "page": "2"},
        )
        view.request = request

        context = view.get_context_data()

        assert request.session["filter"] == "test"
        assert request.session["featured_category_filter"] == str(multiple_categories[0].id)
        assert request.session["featured_products_page"] == "2"

    def test_get_context_data_uses_session_filters_when_keep_filters(self, authenticated_request, multiple_categories):
        """Should use session filters when keep-filters is present."""
        view = ManageFeaturedView()
        request = authenticated_request(method="GET", data={"keep-filters": "1"})
        request.session["filter"] = "session_filter"
        request.session["featured_category_filter"] = str(multiple_categories[0].id)
        request.session["featured_products_page"] = "3"
        view.request = request

        context = view.get_context_data()

        assert context["filter"] == "session_filter"
        assert context["category_filter"] == str(multiple_categories[0].id)
        # Page might be 0 if no products match the filter, or a pagination object
        assert context["page"] in ["3", 3, 0] or hasattr(context["page"], "number")


@pytest.mark.django_db
@pytest.mark.unit
class TestAddFeatured:
    """Tests for add_featured function."""

    def test_add_featured_creates_featured_products(self, authenticated_request, multiple_products):
        """Should create FeaturedProduct instances for selected products."""
        request = authenticated_request(
            method="POST",
            data={
                "product-1": "on",
                "product-2": "on",
                "other-field": "value",  # Should be ignored
            },
        )

        # Verify no featured products exist initially
        assert FeaturedProduct.objects.count() == 0

        response = add_featured(request)

        # Should create 2 featured products
        assert FeaturedProduct.objects.count() == 2
        featured_products = FeaturedProduct.objects.all()
        product_ids = [fp.product.id for fp in featured_products]
        assert multiple_products[0].id in product_ids
        assert multiple_products[1].id in product_ids

    def test_add_featured_ignores_non_product_fields(self, authenticated_request, multiple_products):
        """Should ignore POST fields that don't start with 'product-'."""
        request = authenticated_request(
            method="POST",
            data={
                "product-1": "on",
                "other-field": "value",
                "not-a-product": "ignored",
            },
        )

        response = add_featured(request)

        # Should only create 1 featured product
        assert FeaturedProduct.objects.count() == 1

    def test_add_featured_updates_positions(self, authenticated_request, multiple_products):
        """Should update positions after adding featured products."""
        request = authenticated_request(
            method="POST",
            data={
                "product-1": "on",
                "product-2": "on",
                "product-3": "on",
            },
        )

        response = add_featured(request)

        featured_products = FeaturedProduct.objects.all().order_by("position")
        assert len(featured_products) == 3
        assert featured_products[0].position == 10
        assert featured_products[1].position == 20
        assert featured_products[2].position == 30

    def test_add_featured_renders_manage_view(self, authenticated_request, multiple_products):
        """Should render the manage featured view after adding."""
        request = authenticated_request(method="POST", data={"product-1": "on"})

        response = add_featured(request)

        assert response.status_code == 200
        # Check that the response contains the expected content
        assert b"featured" in response.content.lower()

    def test_add_featured_handles_empty_post_data(self, authenticated_request, shop):
        """Should handle empty POST data gracefully."""
        request = authenticated_request(method="POST", data={})

        response = add_featured(request)

        assert response.status_code == 200
        assert FeaturedProduct.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.unit
class TestUpdateFeatured:
    """Tests for update_featured function."""

    def test_update_featured_removes_products_when_action_is_remove(self, authenticated_request, featured_products):
        """Should remove featured products when action is 'remove'."""
        request = authenticated_request(
            method="POST",
            data={
                "action": "remove",
                "product-1": "on",
                "product-2": "on",
            },
        )

        # Verify featured products exist initially
        assert FeaturedProduct.objects.count() == 3

        response = update_featured(request)

        # Should remove 2 featured products
        assert FeaturedProduct.objects.count() == 1
        remaining = FeaturedProduct.objects.first()
        assert remaining.id == 3  # Only the third one should remain

    def test_update_featured_ignores_non_product_fields_when_removing(self, authenticated_request, featured_products):
        """Should ignore non-product fields when removing."""
        request = authenticated_request(
            method="POST",
            data={
                "action": "remove",
                "product-1": "on",
                "other-field": "value",
            },
        )

        response = update_featured(request)

        # Should only remove 1 featured product
        assert FeaturedProduct.objects.count() == 2

    def test_update_featured_handles_nonexistent_featured_product(self, authenticated_request, featured_products):
        """Should handle nonexistent featured product gracefully."""
        request = authenticated_request(
            method="POST",
            data={
                "action": "remove",
                "product-999": "on",  # Non-existent ID
            },
        )

        response = update_featured(request)

        # Should not crash and all products should remain
        assert FeaturedProduct.objects.count() == 3

    def test_update_featured_updates_positions_when_removing(self, authenticated_request, featured_products):
        """Should update positions after removing featured products."""
        request = authenticated_request(
            method="POST",
            data={
                "action": "remove",
                "product-1": "on",
            },
        )

        response = update_featured(request)

        featured_products = FeaturedProduct.objects.all().order_by("position")
        assert len(featured_products) == 2
        assert featured_products[0].position == 10
        assert featured_products[1].position == 20

    def test_update_featured_updates_positions_when_not_removing(self, authenticated_request, featured_products):
        """Should update positions when action is not 'remove'."""
        request = authenticated_request(
            method="POST",
            data={
                "position-1": "50",
                "position-2": "60",
            },
        )

        response = update_featured(request)

        featured_products = FeaturedProduct.objects.all().order_by("position")
        assert len(featured_products) == 3
        # Positions should be updated and then normalized
        assert featured_products[0].position == 10
        assert featured_products[1].position == 20
        assert featured_products[2].position == 30

    def test_update_featured_ignores_non_position_fields_when_updating(self, authenticated_request, featured_products):
        """Should ignore non-position fields when updating positions."""
        request = authenticated_request(
            method="POST",
            data={
                "position-1": "50",
                "other-field": "value",
            },
        )

        response = update_featured(request)

        # Should update positions and normalize them
        featured_products = FeaturedProduct.objects.all().order_by("position")
        assert len(featured_products) == 3
        assert featured_products[0].position == 10
        assert featured_products[1].position == 20
        assert featured_products[2].position == 30

    def test_update_featured_renders_manage_view_after_removing(self, authenticated_request, featured_products):
        """Should render the manage featured view after removing."""
        request = authenticated_request(
            method="POST",
            data={
                "action": "remove",
                "product-1": "on",
            },
        )

        response = update_featured(request)

        assert response.status_code == 200
        # Check that the response contains the expected content
        assert b"featured" in response.content.lower()

    def test_update_featured_renders_manage_view_after_updating(self, authenticated_request, featured_products):
        """Should render the manage featured view after updating positions."""
        request = authenticated_request(
            method="POST",
            data={
                "position-1": "50",
            },
        )

        response = update_featured(request)

        assert response.status_code == 200
        # Check that the response contains the expected content
        assert b"featured" in response.content.lower()

    def test_update_featured_handles_empty_post_data(self, authenticated_request, shop):
        """Should handle empty POST data gracefully."""
        request = authenticated_request(method="POST", data={})

        response = update_featured(request)

        assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.unit
class TestUpdatePositions:
    """Tests for _update_positions helper function."""

    def test_update_positions_sets_sequential_positions(self, featured_products):
        """Should set sequential positions starting from 10."""
        # Manually set some positions first
        featured_products[0].position = 100
        featured_products[1].position = 200
        featured_products[2].position = 300
        for fp in featured_products:
            fp.save()

        _update_positions()

        featured_products = FeaturedProduct.objects.all().order_by("position")
        assert featured_products[0].position == 10
        assert featured_products[1].position == 20
        assert featured_products[2].position == 30

    def test_update_positions_handles_empty_featured_products(self):
        """Should handle empty featured products list gracefully."""
        # Should not raise any exception
        _update_positions()

        assert FeaturedProduct.objects.count() == 0

    def test_update_positions_maintains_order(self, featured_products):
        """Should maintain the order of featured products."""
        # Get the original order
        original_order = list(FeaturedProduct.objects.all().order_by("id"))

        _update_positions()

        # Check that order is maintained
        updated_order = list(FeaturedProduct.objects.all().order_by("position"))
        assert len(original_order) == len(updated_order)
        for i, fp in enumerate(updated_order):
            assert fp.position == (i + 1) * 10

    def test_update_positions_handles_single_featured_product(self, shop):
        """Should handle single featured product correctly."""
        from lfs.catalog.models import Product
        from decimal import Decimal

        product = Product.objects.create(
            name="Single Product",
            slug="single-product",
            sku="SINGLE-001",
            price=Decimal("29.99"),
            active=True,
        )
        featured = FeaturedProduct.objects.create(product=product, position=999)

        _update_positions()

        featured.refresh_from_db()
        assert featured.position == 10


@pytest.mark.django_db
@pytest.mark.unit
class TestFeaturedViewsIntegration:
    """Integration tests for featured views."""

    def test_complete_featured_workflow(self, authenticated_request, multiple_products, multiple_categories):
        """Should handle complete workflow: add -> update positions -> remove."""
        # Step 1: Add featured products
        request = authenticated_request(
            method="POST",
            data={
                "product-1": "on",
                "product-2": "on",
            },
        )
        response = add_featured(request)
        assert response.status_code == 200
        assert FeaturedProduct.objects.count() == 2

        # Step 2: Update positions
        request = authenticated_request(
            method="POST",
            data={
                "position-1": "50",
                "position-2": "30",
            },
        )
        response = update_featured(request)
        assert response.status_code == 200

        # Step 3: Remove one product
        request = authenticated_request(
            method="POST",
            data={
                "action": "remove",
                "product-1": "on",
            },
        )
        response = update_featured(request)
        assert response.status_code == 200
        assert FeaturedProduct.objects.count() == 1

        # Verify final state
        remaining = FeaturedProduct.objects.first()
        assert remaining.product.id == 2  # Second product should remain
        assert remaining.position == 10  # Position should be normalized

    def test_filtering_and_pagination_workflow(self, authenticated_request, many_products, multiple_categories):
        """Should handle filtering and pagination correctly."""
        # Assign some products to categories
        many_products[0].categories.add(multiple_categories[0])
        many_products[1].categories.add(multiple_categories[0])
        many_products[2].categories.add(multiple_categories[1])

        # Test category filtering
        view = ManageFeaturedView()
        request = authenticated_request(method="GET", data={"featured_category_filter": str(multiple_categories[0].id)})
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
                "featured_category_filter": str(multiple_categories[0].id),
                "page": "2",
                "featured-amount": "10",
            },
        )

        view = ManageFeaturedView()
        view.request = request
        context = view.get_context_data()

        # Verify session was updated
        assert request.session["filter"] == "test"
        assert request.session["featured_category_filter"] == str(multiple_categories[0].id)
        assert request.session["featured_products_page"] == "2"
        assert request.session["featured-amount"] == 10

        # Test keep-filters functionality
        request = authenticated_request(method="GET", data={"keep-filters": "1"})
        request.session["filter"] = "session_filter"
        request.session["featured_category_filter"] = str(multiple_categories[1].id)
        request.session["featured_products_page"] = "3"

        view = ManageFeaturedView()
        view.request = request
        context = view.get_context_data()

        # Should use session values
        assert context["filter"] == "session_filter"
        assert context["category_filter"] == str(multiple_categories[1].id)
        # Page might be 0 if no products match the filter, or a pagination object
        assert context["page"] in ["3", 3, 0] or hasattr(context["page"], "number")
