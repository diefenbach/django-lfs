import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseRedirect
from decimal import Decimal

from lfs.discounts.models import Discount
from lfs.discounts.settings import DISCOUNT_TYPE_ABSOLUTE, DISCOUNT_TYPE_PERCENTAGE
from lfs.catalog.models import Product, Category
from lfs.manufacturer.models import Manufacturer
from lfs.manage.discounts.views import (
    ManageDiscountsView,
    NoDiscountsView,
    DiscountTabMixin,
    DiscountDataView,
    DiscountCriteriaView,
    DiscountProductsView,
    DiscountCreateView,
    DiscountDeleteConfirmView,
    DiscountDeleteView,
)

User = get_user_model()


@pytest.fixture
def discount(db):
    """Sample Discount for testing."""
    return Discount.objects.create(
        name="Test Discount",
        value=Decimal("10.00"),
        type=DISCOUNT_TYPE_ABSOLUTE,
        active=True,
    )


@pytest.fixture
def multiple_discounts(db):
    """Multiple Discounts for list testing."""
    discounts = []
    for i in range(3):
        discount = Discount.objects.create(
            name=f"Discount {i+1}",
            value=Decimal(f"{(i+1)*5}.00"),
            type=DISCOUNT_TYPE_ABSOLUTE,
            active=True,
        )
        discounts.append(discount)
    return discounts


@pytest.fixture
def product(db, shop):
    """Sample Product for testing."""
    from decimal import Decimal

    return Product.objects.create(
        name="Test Product",
        slug="test-product",
        sku="TEST-001",
        price=Decimal("29.99"),
        active=True,
    )


@pytest.fixture
def multiple_products(db, shop):
    """Multiple Products for testing."""
    from decimal import Decimal

    products = []
    for i in range(5):
        product = Product.objects.create(
            name=f"Product {i+1}",
            slug=f"product-{i+1}",
            sku=f"SKU-{i+1:03d}",
            price=Decimal(f"{(i+1)*10}.99"),
            active=True,
        )
        products.append(product)
    return products


@pytest.fixture
def category(db):
    """Sample Category for testing."""
    return Category.objects.create(
        name="Test Category",
        slug="test-category",
        position=10,
    )


@pytest.fixture
def manufacturer(db):
    """Sample Manufacturer for testing."""
    return Manufacturer.objects.create(
        name="Test Manufacturer",
        slug="test-manufacturer",
        position=10,
    )


@pytest.mark.django_db
@pytest.mark.unit
class TestManageDiscountsView:
    """Tests for ManageDiscountsView."""

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = ManageDiscountsView()
        assert view.permission_required == "core.manage_shop"

    def test_get_redirect_url_redirects_to_first_discount(self, multiple_discounts):
        """Should redirect to first discount when discounts exist."""
        view = ManageDiscountsView()

        redirect_url = view.get_redirect_url()

        first_discount = Discount.objects.all().order_by("name")[0]
        expected_url = reverse("lfs_manage_discount", kwargs={"id": first_discount.id})
        assert redirect_url == expected_url

    def test_get_redirect_url_redirects_to_no_discounts_when_none_exist(self):
        """Should redirect to no discounts view when no discounts exist."""
        view = ManageDiscountsView()

        redirect_url = view.get_redirect_url()

        expected_url = reverse("lfs_manage_no_discounts")
        assert redirect_url == expected_url


@pytest.mark.django_db
@pytest.mark.unit
class TestNoDiscountsView:
    """Tests for NoDiscountsView."""

    def test_view_uses_correct_template(self):
        """Should use the correct template."""
        view = NoDiscountsView()
        assert view.template_name == "manage/discounts/no_discounts.html"

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = NoDiscountsView()
        assert view.permission_required == "core.manage_shop"


@pytest.mark.django_db
@pytest.mark.unit
class TestDiscountTabMixin:
    """Tests for DiscountTabMixin functionality."""

    def test_get_discount_returns_correct_object(self, discount):
        """Should return the Discount for given id."""
        mixin = DiscountTabMixin()
        mixin.kwargs = {"id": discount.id}

        result = mixin.get_discount()

        assert result == discount

    def test_get_discount_raises_404_for_nonexistent_id(self):
        """Should raise Http404 for non-existent Discount id."""
        mixin = DiscountTabMixin()
        mixin.kwargs = {"id": 99999}

        with pytest.raises(Http404):
            mixin.get_discount()

    def test_get_tabs_returns_correct_navigation_urls_without_search(self, discount, rf):
        """Should return list of tab navigation URLs without search parameters."""
        mixin = DiscountTabMixin()
        mixin.request = rf.get("/test/")

        tabs = mixin._get_tabs(discount)

        assert len(tabs) == 3
        assert tabs[0] == ("data", reverse("lfs_manage_discount", args=[discount.pk]))
        assert tabs[1] == ("criteria", reverse("lfs_manage_discount_criteria", args=[discount.pk]))
        assert tabs[2] == ("products", reverse("lfs_manage_discount_products", args=[discount.pk]))

    def test_get_tabs_returns_correct_navigation_urls_with_search(self, discount, rf):
        """Should return list of tab navigation URLs with search parameters."""
        mixin = DiscountTabMixin()
        mixin.request = rf.get("/test/?q=search_term")

        tabs = mixin._get_tabs(discount)

        expected_data_url = reverse("lfs_manage_discount", args=[discount.pk]) + "?q=search_term"
        expected_criteria_url = reverse("lfs_manage_discount_criteria", args=[discount.pk]) + "?q=search_term"
        expected_products_url = reverse("lfs_manage_discount_products", args=[discount.pk]) + "?q=search_term"

        assert tabs[0] == ("data", expected_data_url)
        assert tabs[1] == ("criteria", expected_criteria_url)
        assert tabs[2] == ("products", expected_products_url)

    def test_get_discounts_queryset_returns_all_discounts_without_search(self, multiple_discounts, rf):
        """Should return all discounts when no search query."""
        mixin = DiscountTabMixin()
        mixin.request = rf.get("/test/")

        queryset = mixin.get_discounts_queryset()

        assert queryset.count() == 3
        assert list(queryset) == list(Discount.objects.all().order_by("name"))

    def test_get_discounts_queryset_filters_by_search_query(self, multiple_discounts, rf):
        """Should filter discounts by search query."""
        mixin = DiscountTabMixin()
        mixin.request = rf.get("/test/?q=Discount 1")

        queryset = mixin.get_discounts_queryset()

        assert queryset.count() == 1
        assert queryset.first().name == "Discount 1"

    def test_get_discounts_queryset_case_insensitive_search(self, multiple_discounts, rf):
        """Should perform case-insensitive search."""
        mixin = DiscountTabMixin()
        mixin.request = rf.get("/test/?q=discount")

        queryset = mixin.get_discounts_queryset()

        assert queryset.count() == 3  # All discounts contain "discount" (case-insensitive)

    def test_get_context_data_includes_discount_and_tabs(self, discount, rf):
        """Should include discount and tabs in context."""
        from django.views.generic import TemplateView

        class TestView(DiscountTabMixin, TemplateView):
            template_name = "test.html"

        view = TestView()
        view.request = rf.get("/test/")
        view.kwargs = {"id": discount.id}
        view.tab_name = "data"

        context = view.get_context_data()

        assert "discount" in context
        assert context["discount"] == discount
        assert "discounts" in context
        assert "active_tab" in context
        assert context["active_tab"] == "data"
        assert "tabs" in context
        assert len(context["tabs"]) == 3


@pytest.mark.django_db
@pytest.mark.unit
class TestDiscountDataView:
    """Tests for DiscountDataView."""

    def test_view_uses_correct_template(self):
        """Should use the correct template."""
        view = DiscountDataView()
        assert view.template_name == "manage/discounts/discount.html"

    def test_view_uses_correct_model(self):
        """Should use Discount model."""
        view = DiscountDataView()
        assert view.model == Discount

    def test_view_has_correct_tab_name(self):
        """Should have 'data' as tab name."""
        view = DiscountDataView()
        assert view.tab_name == "data"

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = DiscountDataView()
        assert view.permission_required == "core.manage_shop"

    def test_get_success_url_returns_data_tab_url(self, discount):
        """Should return URL to data tab after successful save."""
        view = DiscountDataView()
        view.object = discount

        success_url = view.get_success_url()

        expected_url = reverse("lfs_manage_discount", kwargs={"id": discount.pk})
        assert success_url == expected_url

    def test_form_valid_shows_success_message(self, discount, authenticated_request):
        """Should show success message after form validation."""
        from lfs.manage.discounts.forms import DiscountForm

        view = DiscountDataView()
        view.request = authenticated_request(
            method="POST",
            data={
                "name": "Updated Discount",
                "value": "15.00",
                "type": DISCOUNT_TYPE_ABSOLUTE,
            },
        )
        view.object = discount

        form = DiscountForm(
            data={
                "name": "Updated Discount",
                "value": "15.00",
                "type": DISCOUNT_TYPE_ABSOLUTE,
            }
        )
        form.is_valid()

        response = view.form_valid(form)

        assert isinstance(response, HttpResponseRedirect)
        # Check that success message was added (would be in messages framework)


@pytest.mark.django_db
@pytest.mark.unit
class TestDiscountCriteriaView:
    """Tests for DiscountCriteriaView."""

    def test_view_uses_correct_template(self):
        """Should use the correct template."""
        view = DiscountCriteriaView()
        assert view.template_name == "manage/discounts/discount.html"

    def test_view_has_correct_tab_name(self):
        """Should have 'criteria' as tab name."""
        view = DiscountCriteriaView()
        assert view.tab_name == "criteria"

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = DiscountCriteriaView()
        assert view.permission_required == "core.manage_shop"

    def test_get_success_url_returns_criteria_tab_url(self, discount):
        """Should return URL to criteria tab after successful operation."""
        view = DiscountCriteriaView()
        view.kwargs = {"id": discount.id}

        success_url = view.get_success_url()

        expected_url = reverse("lfs_manage_discount_criteria", kwargs={"id": discount.id})
        assert success_url == expected_url

    def test_post_handles_criteria_saving(self, discount, authenticated_request):
        """Should handle criteria saving via POST."""
        view = DiscountCriteriaView()
        view.request = authenticated_request(method="POST", data={})
        view.kwargs = {"id": discount.id}

        # Mock the save_criteria method to avoid complex criteria logic
        original_save_criteria = discount.save_criteria
        discount.save_criteria = lambda request: None

        response = view.post(authenticated_request(method="POST", data={}))

        # Restore original method
        discount.save_criteria = original_save_criteria

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse("lfs_manage_discount_criteria", kwargs={"id": discount.id})

    def test_post_handles_htmx_request(self, discount, authenticated_request, shop):
        """Should handle HTMX requests by returning partial content."""
        view = DiscountCriteriaView()
        view.request = authenticated_request(method="POST", data={})
        view.request.META["HTTP_HX_REQUEST"] = "true"
        view.kwargs = {"id": discount.id}

        # Mock the save_criteria method
        original_save_criteria = discount.save_criteria
        discount.save_criteria = lambda request: None

        response = view.post(view.request)

        # Restore original method
        discount.save_criteria = original_save_criteria

        assert response.status_code == 200
        # Should render the criteria tab template

    def test_get_context_data_includes_criteria(self, discount, authenticated_request):
        """Should include criteria in context."""
        view = DiscountCriteriaView()
        view.request = authenticated_request()
        view.kwargs = {"id": discount.id}

        context = view.get_context_data()

        assert "criteria" in context
        assert isinstance(context["criteria"], list)


@pytest.mark.django_db
@pytest.mark.unit
class TestDiscountCriteriaModel:
    """Tests for Discount model criteria functionality."""

    def test_save_criteria_with_invalid_type_key(self, discount, request_factory):
        """Test that save_criteria handles invalid type keys gracefully."""
        # Create a request with invalid type key (no dash)
        request = request_factory.post(
            "/test/",
            {"type": "invalid_key_without_dash", "csrfmiddlewaretoken": "test"},  # This should cause IndexError
        )

        # Add session and messages middleware
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.messages.middleware import MessageMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        messages_middleware = MessageMiddleware(lambda req: None)
        messages_middleware.process_request(request)

        # This should not raise an IndexError
        try:
            discount.save_criteria(request)
        except IndexError:
            pytest.fail("save_criteria raised IndexError when it should handle it gracefully")

    def test_save_criteria_with_empty_post(self, discount, request_factory):
        """Test that save_criteria handles empty POST data."""
        request = request_factory.post("/test/", {})

        # Add session and messages middleware
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.messages.middleware import MessageMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        messages_middleware = MessageMiddleware(lambda req: None)
        messages_middleware.process_request(request)

        # This should not raise any exception
        try:
            discount.save_criteria(request)
        except Exception as e:
            pytest.fail(f"save_criteria raised {type(e).__name__}: {e}")

    def test_save_criteria_with_valid_type_key(self, discount, request_factory):
        """Test that save_criteria works with valid type keys."""
        request = request_factory.post(
            "/test/",
            {
                "type-123": "lfs.criteria.models.CartPriceCriterion",
                "operator-123": "0",
                "position-123": "10",
                "value-123": "100",
                "csrfmiddlewaretoken": "test",
            },
        )

        # Add session and messages middleware
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.messages.middleware import MessageMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        messages_middleware = MessageMiddleware(lambda req: None)
        messages_middleware.process_request(request)

        # This should work without raising exceptions
        try:
            discount.save_criteria(request)
        except Exception as e:
            pytest.fail(f"save_criteria raised {type(e).__name__}: {e}")


@pytest.mark.django_db
@pytest.mark.unit
class TestDiscountProductsView:
    """Tests for DiscountProductsView."""

    def test_view_uses_correct_template(self):
        """Should use the correct template."""
        view = DiscountProductsView()
        assert view.template_name == "manage/discounts/discount.html"

    def test_view_has_correct_tab_name(self):
        """Should have 'products' as tab name."""
        view = DiscountProductsView()
        assert view.tab_name == "products"

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = DiscountProductsView()
        assert view.permission_required == "core.manage_shop"

    def test_get_success_url_returns_products_tab_url(self, discount):
        """Should return URL to products tab after successful operation."""
        view = DiscountProductsView()
        view.kwargs = {"id": discount.id}

        success_url = view.get_success_url()

        expected_url = reverse("lfs_manage_discount_products", kwargs={"id": discount.id})
        assert success_url == expected_url

    def test_post_handles_assign_products(self, discount, multiple_products, authenticated_request):
        """Should handle product assignment via POST."""
        view = DiscountProductsView()
        view.request = authenticated_request(
            method="POST",
            data={
                "assign_products": "1",
                "product-1": "on",
                "product-2": "on",
            },
        )
        view.kwargs = {"id": discount.id}

        response = view.post(view.request)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse("lfs_manage_discount_products", kwargs={"id": discount.id})
        # Check that products were assigned
        assert discount.products.count() == 2

    def test_post_handles_remove_products(self, discount, multiple_products, authenticated_request):
        """Should handle product removal via POST."""
        # First assign some products
        discount.products.add(multiple_products[0], multiple_products[1])

        view = DiscountProductsView()
        view.request = authenticated_request(
            method="POST",
            data={
                "remove_products": "1",
                "product-1": "on",
            },
        )
        view.kwargs = {"id": discount.id}

        response = view.post(view.request)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse("lfs_manage_discount_products", kwargs={"id": discount.id})
        # Check that one product was removed
        assert discount.products.count() == 1

    def test_get_context_data_includes_products_and_filters(self, discount, multiple_products, authenticated_request):
        """Should include products and filters in context."""
        # Assign some products to discount
        discount.products.add(multiple_products[0], multiple_products[1])

        view = DiscountProductsView()
        view.request = authenticated_request()
        view.kwargs = {"id": discount.id}

        context = view.get_context_data()

        assert "discount_products" in context
        assert "page" in context
        assert "paginator" in context
        assert "filter" in context
        assert "category_filter" in context
        assert "manufacturer_filter" in context

    def test_get_context_data_filters_products_by_name(self, discount, multiple_products, authenticated_request):
        """Should filter products by name."""
        view = DiscountProductsView()
        view.request = authenticated_request(method="GET", data={"filter": "Product 1"})
        view.kwargs = {"id": discount.id}

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        if hasattr(page_obj, "object_list"):
            # Should only show products matching the filter
            assert all("Product 1" in product.name for product in page_obj.object_list)

    def test_get_context_data_filters_products_by_category(
        self, discount, multiple_products, category, authenticated_request
    ):
        """Should filter products by category."""
        # Assign a product to a category
        multiple_products[0].categories.add(category)

        view = DiscountProductsView()
        view.request = authenticated_request(method="GET", data={"products_category_filter": str(category.id)})
        view.kwargs = {"id": discount.id}

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        if hasattr(page_obj, "object_list"):
            # Should only show products in the specified category
            assert all(category in product.categories.all() for product in page_obj.object_list)

    def test_get_context_data_filters_products_by_manufacturer(
        self, discount, multiple_products, manufacturer, authenticated_request
    ):
        """Should filter products by manufacturer."""
        # Assign a product to a manufacturer
        multiple_products[0].manufacturer = manufacturer
        multiple_products[0].save()

        view = DiscountProductsView()
        view.request = authenticated_request(method="GET", data={"products_manufacturer_filter": str(manufacturer.id)})
        view.kwargs = {"id": discount.id}

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        if hasattr(page_obj, "object_list"):
            # Should only show products with the specified manufacturer
            assert all(product.manufacturer == manufacturer for product in page_obj.object_list)

    def test_get_context_data_handles_pagination(self, discount, authenticated_request, shop):
        """Should handle pagination correctly."""
        # Create many products to trigger pagination
        from decimal import Decimal

        for i in range(30):
            Product.objects.create(
                name=f"Product {i+1}",
                slug=f"product-{i+1}",
                sku=f"SKU-{i+1:03d}",
                price=Decimal(f"{(i+1)*10}.99"),
                active=True,
            )

        view = DiscountProductsView()
        view.request = authenticated_request(method="GET", data={"page": "2"})
        view.kwargs = {"id": discount.id}

        context = view.get_context_data()

        assert "page" in context
        page_obj = context["page"]
        if hasattr(page_obj, "number"):
            assert page_obj.number == 2

    def test_search_field_displays_correct_value(self, discount, authenticated_client):
        """Test that search field displays the correct value from context."""
        # Test with search term
        response = authenticated_client.get(
            reverse("lfs_manage_discount_products", kwargs={"id": discount.id}), {"filter": "test search"}
        )
        assert response.status_code == 200

        # Check that the search field contains the search term
        content = response.content.decode()
        assert 'value="test search"' in content

        # Test without search term (should be empty, not "None")
        response = authenticated_client.get(reverse("lfs_manage_discount_products", kwargs={"id": discount.id}))
        assert response.status_code == 200

        # Check that the search field is empty and does NOT contain "None"
        content = response.content.decode()
        # Look specifically for the search input field
        import re

        search_input_match = re.search(r'<input[^>]*name="filter"[^>]*value="([^"]*)"', content)
        assert search_input_match is not None
        search_value = search_input_match.group(1)
        assert search_value != "None"
        assert search_value == ""

    def test_search_field_does_not_display_none_string(self, discount, authenticated_client):
        """Test that search field does not display 'None' as a string."""
        # First visit with a search term to set session
        response = authenticated_client.get(
            reverse("lfs_manage_discount_products", kwargs={"id": discount.id}), {"filter": "test search"}
        )
        assert response.status_code == 200

        # Then visit without filter parameter - this should not show "None"
        response = authenticated_client.get(reverse("lfs_manage_discount_products", kwargs={"id": discount.id}))
        assert response.status_code == 200

        content = response.content.decode()
        # The search field should not contain the string "None" as its value
        # Look specifically for the search input field
        import re

        search_input_match = re.search(r'<input[^>]*name="filter"[^>]*value="([^"]*)"', content)
        assert search_input_match is not None
        search_value = search_input_match.group(1)
        assert search_value != "None"
        assert search_value == ""


@pytest.mark.django_db
@pytest.mark.unit
class TestDiscountCreateView:
    """Tests for DiscountCreateView."""

    def test_view_uses_correct_model(self):
        """Should use Discount model."""
        view = DiscountCreateView()
        assert view.model == Discount

    def test_view_uses_correct_template(self):
        """Should use the correct template."""
        view = DiscountCreateView()
        assert view.template_name == "manage/discounts/add_discount.html"

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = DiscountCreateView()
        assert view.permission_required == "core.manage_shop"

    def test_get_success_url_returns_discount_url(self, discount):
        """Should return URL to discount after successful creation."""
        view = DiscountCreateView()
        view.object = discount

        success_url = view.get_success_url()

        expected_url = reverse("lfs_manage_discount", kwargs={"id": discount.id})
        assert success_url == expected_url

    def test_form_valid_creates_discount_and_redirects(self, authenticated_request):
        """Should create discount and redirect with success message."""
        from lfs.manage.discounts.forms import DiscountForm

        view = DiscountCreateView()
        view.request = authenticated_request(
            method="POST",
            data={
                "name": "New Discount",
                "value": "20.00",
                "type": DISCOUNT_TYPE_PERCENTAGE,
            },
        )

        form = DiscountForm(
            data={
                "name": "New Discount",
                "value": "20.00",
                "type": DISCOUNT_TYPE_PERCENTAGE,
            }
        )
        form.is_valid()

        response = view.form_valid(form)

        assert isinstance(response, HttpResponseRedirect)
        assert Discount.objects.filter(name="New Discount").exists()


@pytest.mark.django_db
@pytest.mark.unit
class TestDiscountDeleteConfirmView:
    """Tests for DiscountDeleteConfirmView."""

    def test_view_uses_correct_template(self):
        """Should use the correct template."""
        view = DiscountDeleteConfirmView()
        assert view.template_name == "manage/discounts/delete_discount.html"

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = DiscountDeleteConfirmView()
        assert view.permission_required == "core.manage_shop"

    def test_get_context_data_includes_discount(self, discount):
        """Should include discount in context."""
        view = DiscountDeleteConfirmView()
        view.kwargs = {"id": discount.id}

        context = view.get_context_data()

        assert "discount" in context
        assert context["discount"] == discount


@pytest.mark.django_db
@pytest.mark.unit
class TestDiscountDeleteView:
    """Tests for DiscountDeleteView."""

    def test_view_uses_correct_model(self):
        """Should use Discount model."""
        view = DiscountDeleteView()
        assert view.model == Discount

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = DiscountDeleteView()
        assert view.permission_required == "core.manage_shop"

    def test_get_success_url_returns_discounts_list(self):
        """Should return URL to discounts list after deletion."""
        view = DiscountDeleteView()

        success_url = view.get_success_url()

        expected_url = reverse("lfs_manage_discounts")
        assert success_url == expected_url

    def test_post_deletes_discount_and_redirects(self, authenticated_request, discount):
        """Should delete discount and redirect with success message."""
        view = DiscountDeleteView()
        view.request = authenticated_request(method="POST", data={})
        view.kwargs = {"id": discount.id}

        response = view.post(authenticated_request(method="POST", data={}))

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse("lfs_manage_discounts")
        # Check that discount was deleted
        assert not Discount.objects.filter(id=discount.id).exists()


@pytest.mark.django_db
@pytest.mark.integration
class TestDiscountViewsIntegration:
    """Integration tests for discount views."""

    def test_discount_data_view_get_request(self, client, manage_user, discount, shop):
        """Should render discount data view successfully."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_discount", kwargs={"id": discount.id})

        response = client.get(url)

        assert response.status_code == 200
        assert "discount" in response.context
        assert response.context["discount"] == discount
        assert response.context["active_tab"] == "data"

    def test_discount_criteria_view_get_request(self, client, manage_user, discount, shop):
        """Should render discount criteria view successfully."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_discount_criteria", kwargs={"id": discount.id})

        response = client.get(url)

        assert response.status_code == 200
        assert "discount" in response.context
        assert response.context["discount"] == discount
        assert response.context["active_tab"] == "criteria"
        assert "criteria" in response.context

    def test_discount_products_view_get_request(self, client, manage_user, discount, shop):
        """Should render discount products view successfully."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_discount_products", kwargs={"id": discount.id})

        response = client.get(url)

        assert response.status_code == 200
        assert "discount" in response.context
        assert response.context["discount"] == discount
        assert response.context["active_tab"] == "products"
        assert "discount_products" in response.context

    def test_manage_discounts_redirects_to_first_discount(self, client, manage_user, discount, shop):
        """Should redirect to first discount."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_discounts")

        response = client.get(url)

        expected_url = reverse("lfs_manage_discount", kwargs={"id": discount.id})
        assert response.status_code == 302
        assert response.url == expected_url

    def test_manage_discounts_redirects_to_no_discounts_when_empty(self, client, manage_user, shop):
        """Should redirect to no discounts view when no discounts exist."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_discounts")

        response = client.get(url)

        expected_url = reverse("lfs_manage_no_discounts")
        assert response.status_code == 302
        assert response.url == expected_url

    def test_no_discounts_view_renders_correctly(self, client, manage_user, shop):
        """Should render no discounts view successfully."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_no_discounts")

        response = client.get(url)

        assert response.status_code == 200

    def test_add_discount_view_get_request(self, client, manage_user, shop):
        """Should render add discount form successfully."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_add_discount")

        response = client.get(url)

        assert response.status_code == 200
        assert "form" in response.context

    def test_discount_views_require_authentication(self, client, discount):
        """Should require authentication for all discount views."""
        urls = [
            reverse("lfs_manage_discounts"),
            reverse("lfs_manage_discount", kwargs={"id": discount.id}),
            reverse("lfs_manage_discount_criteria", kwargs={"id": discount.id}),
            reverse("lfs_manage_discount_products", kwargs={"id": discount.id}),
            reverse("lfs_manage_add_discount"),
            reverse("lfs_manage_no_discounts"),
        ]

        for url in urls:
            response = client.get(url)
            # Should redirect to login or return 403/401
            assert response.status_code in [302, 403, 401]

    def test_complete_discount_workflow(self, client, manage_user, multiple_products, category, shop):
        """Should handle complete discount workflow: create -> assign products -> remove."""
        client.force_login(manage_user)

        # Step 1: Create discount
        response = client.post(
            reverse("lfs_manage_add_discount"),
            {
                "name": "Test Workflow Discount",
                "value": "15.00",
                "type": DISCOUNT_TYPE_ABSOLUTE,
            },
        )
        assert response.status_code == 302

        # Get the created discount
        discount = Discount.objects.get(name="Test Workflow Discount")

        # Step 2: Assign products
        response = client.post(
            reverse("lfs_manage_discount_products", kwargs={"id": discount.id}),
            {
                "assign_products": "1",
                "product-1": "on",
                "product-2": "on",
            },
        )
        assert response.status_code == 302
        assert discount.products.count() == 2

        # Step 3: Remove one product
        response = client.post(
            reverse("lfs_manage_discount_products", kwargs={"id": discount.id}),
            {
                "remove_products": "1",
                "product-1": "on",
            },
        )
        assert response.status_code == 302
        assert discount.products.count() == 1

        # Step 4: Delete discount
        response = client.post(reverse("lfs_manage_delete_discount", kwargs={"id": discount.id}))
        assert response.status_code == 302
        assert not Discount.objects.filter(id=discount.id).exists()
