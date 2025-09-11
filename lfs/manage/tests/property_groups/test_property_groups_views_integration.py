"""
Comprehensive integration tests for property_groups views.

Following TDD principles:
- Test complete integration between components
- Test real database interactions
- Test complete request/response cycles
- Clear test names describing the integration being tested
- Arrange-Act-Assert structure
- One assertion per test (when practical)

Tests cover:
- View integration with database
- View integration with forms
- View integration with templates
- View integration with authentication
- View integration with permissions
- View integration with search
- View integration with pagination
- View integration with filtering
- View integration with AJAX requests
- View integration with error handling
"""

import pytest
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import RequestFactory, Client
from django.urls import reverse

from lfs.catalog.models import PropertyGroup, Property, Product, GroupsPropertiesRelation

User = get_user_model()


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def client():
    """Django test client for integration testing."""
    return Client()


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


@pytest.fixture
def sample_property_group():
    """Create a sample property group for testing."""
    return PropertyGroup.objects.create(name="Test Property Group")


@pytest.fixture
def sample_property():
    """Create a sample property for testing."""
    return Property.objects.create(
        name="test_property",
        title="Test Property",
        type=1,  # Text field
    )


@pytest.fixture
def sample_product():
    """Create a sample product for testing."""
    return Product.objects.create(name="Test Product", slug="test-product", price=10.99, active=True)


class TestPropertyGroupViewDatabaseIntegration:
    """Test property group view integration with database."""

    @pytest.mark.django_db
    def test_manage_property_groups_view_database_integration(self, client, admin_user, sample_property_group):
        """Test ManagePropertyGroupsView integration with database."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_groups"))

        assert response.status_code == 302
        assert "property-group" in response.url
        assert str(sample_property_group.id) in response.url

    @pytest.mark.django_db
    def test_manage_property_groups_view_database_integration_no_groups(self, client, admin_user):
        """Test ManagePropertyGroupsView integration with database when no groups exist."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_groups"))

        assert response.status_code == 302
        assert "no-property-groups" in response.url

    @pytest.mark.django_db
    def test_property_group_data_view_database_integration(self, client, admin_user, sample_property_group):
        """Test PropertyGroupDataView integration with database."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200
        assert "property_group" in response.context
        assert response.context["property_group"] == sample_property_group

    @pytest.mark.django_db
    def test_property_group_data_view_database_integration_nonexistent(self, client, admin_user):
        """Test PropertyGroupDataView integration with database for nonexistent group."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": 99999}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_property_group_products_view_database_integration(
        self, client, admin_user, sample_property_group, sample_product
    ):
        """Test PropertyGroupProductsView integration with database."""
        sample_property_group.products.add(sample_product)
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group_products", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200
        assert "property_group" in response.context
        assert response.context["property_group"] == sample_property_group
        assert "group_products" in response.context
        assert sample_product in response.context["group_products"]

    @pytest.mark.django_db
    def test_property_group_properties_view_database_integration(
        self, client, admin_user, sample_property_group, sample_property
    ):
        """Test PropertyGroupPropertiesView integration with database."""
        GroupsPropertiesRelation.objects.create(group=sample_property_group, property=sample_property, position=1)
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group_properties", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200
        assert "property_group" in response.context
        assert response.context["property_group"] == sample_property_group
        assert "properties" in response.context

    @pytest.mark.django_db
    def test_no_property_groups_view_database_integration(self, client, admin_user):
        """Test NoPropertyGroupsView integration with database."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_no_property_groups"))

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_property_group_create_view_database_integration(self, client, admin_user):
        """Test PropertyGroupCreateView integration with database."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_add_property_group"))

        assert response.status_code == 200
        assert "form" in response.context

    @pytest.mark.django_db
    def test_property_group_create_view_database_integration_post(self, client, admin_user):
        """Test PropertyGroupCreateView integration with database on POST."""
        client.force_login(admin_user)

        form_data = {"name": "New Property Group"}
        response = client.post(reverse("lfs_manage_add_property_group"), form_data)

        assert response.status_code == 302
        assert PropertyGroup.objects.filter(name="New Property Group").exists()

    @pytest.mark.django_db
    def test_property_group_delete_confirm_view_database_integration(self, client, admin_user, sample_property_group):
        """Test PropertyGroupDeleteConfirmView integration with database."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_delete_property_group_confirm", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200
        assert "property_group" in response.context
        assert response.context["property_group"] == sample_property_group

    @pytest.mark.django_db
    def test_property_group_delete_view_database_integration(self, client, admin_user, sample_property_group):
        """Test PropertyGroupDeleteView integration with database."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_delete_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 302
        assert not PropertyGroup.objects.filter(id=sample_property_group.id).exists()


class TestPropertyGroupViewFormIntegration:
    """Test property group view integration with forms."""

    @pytest.mark.django_db
    def test_property_group_data_view_form_integration_get(self, client, admin_user, sample_property_group):
        """Test PropertyGroupDataView integration with forms on GET."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].instance == sample_property_group

    @pytest.mark.django_db
    def test_property_group_data_view_form_integration_post_valid(self, client, admin_user, sample_property_group):
        """Test PropertyGroupDataView integration with forms on POST with valid data."""
        client.force_login(admin_user)

        form_data = {"name": "Updated Property Group"}
        response = client.post(reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}), form_data)

        assert response.status_code == 302
        sample_property_group.refresh_from_db()
        assert sample_property_group.name == "Updated Property Group"

    @pytest.mark.django_db
    def test_property_group_data_view_form_integration_post_invalid(self, client, admin_user, sample_property_group):
        """Test PropertyGroupDataView integration with forms on POST with invalid data."""
        client.force_login(admin_user)

        form_data = {"name": ""}  # Invalid empty name
        response = client.post(reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}), form_data)

        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()

    @pytest.mark.django_db
    def test_property_group_create_view_form_integration_get(self, client, admin_user):
        """Test PropertyGroupCreateView integration with forms on GET."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_add_property_group"))

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].instance is None

    @pytest.mark.django_db
    def test_property_group_create_view_form_integration_post_valid(self, client, admin_user):
        """Test PropertyGroupCreateView integration with forms on POST with valid data."""
        client.force_login(admin_user)

        form_data = {"name": "New Property Group"}
        response = client.post(reverse("lfs_manage_add_property_group"), form_data)

        assert response.status_code == 302
        assert PropertyGroup.objects.filter(name="New Property Group").exists()

    @pytest.mark.django_db
    def test_property_group_create_view_form_integration_post_invalid(self, client, admin_user):
        """Test PropertyGroupCreateView integration with forms on POST with invalid data."""
        client.force_login(admin_user)

        form_data = {"name": ""}  # Invalid empty name
        response = client.post(reverse("lfs_manage_add_property_group"), form_data)

        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()


class TestPropertyGroupViewTemplateIntegration:
    """Test property group view integration with templates."""

    @pytest.mark.django_db
    def test_property_group_data_view_template_integration(self, client, admin_user, sample_property_group):
        """Test PropertyGroupDataView integration with templates."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200
        assert "manage/property_groups/property_group.html" in [template.name for template in response.templates]

    @pytest.mark.django_db
    def test_property_group_products_view_template_integration(self, client, admin_user, sample_property_group):
        """Test PropertyGroupProductsView integration with templates."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group_products", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200
        assert "manage/property_groups/property_group.html" in [template.name for template in response.templates]

    @pytest.mark.django_db
    def test_property_group_properties_view_template_integration(self, client, admin_user, sample_property_group):
        """Test PropertyGroupPropertiesView integration with templates."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group_properties", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200
        assert "manage/property_groups/property_group.html" in [template.name for template in response.templates]

    @pytest.mark.django_db
    def test_no_property_groups_view_template_integration(self, client, admin_user):
        """Test NoPropertyGroupsView integration with templates."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_no_property_groups"))

        assert response.status_code == 200
        assert "manage/property_groups/no_property_groups.html" in [template.name for template in response.templates]

    @pytest.mark.django_db
    def test_property_group_create_view_template_integration(self, client, admin_user):
        """Test PropertyGroupCreateView integration with templates."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_add_property_group"))

        assert response.status_code == 200
        assert "manage/property_groups/add_property_group.html" in [template.name for template in response.templates]

    @pytest.mark.django_db
    def test_property_group_delete_confirm_view_template_integration(self, client, admin_user, sample_property_group):
        """Test PropertyGroupDeleteConfirmView integration with templates."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_delete_property_group_confirm", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200
        assert "manage/property_groups/delete_property_group.html" in [template.name for template in response.templates]


class TestPropertyGroupViewAuthenticationIntegration:
    """Test property group view integration with authentication."""

    @pytest.mark.django_db
    def test_property_group_data_view_authentication_integration_authenticated(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupDataView integration with authentication for authenticated user."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_property_group_data_view_authentication_integration_unauthenticated(self, client, sample_property_group):
        """Test PropertyGroupDataView integration with authentication for unauthenticated user."""
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 302
        assert "/login/" in response.url

    @pytest.mark.django_db
    def test_property_group_create_view_authentication_integration_authenticated(self, client, admin_user):
        """Test PropertyGroupCreateView integration with authentication for authenticated user."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_add_property_group"))

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_property_group_create_view_authentication_integration_unauthenticated(self, client):
        """Test PropertyGroupCreateView integration with authentication for unauthenticated user."""
        response = client.get(reverse("lfs_manage_add_property_group"))

        assert response.status_code == 302
        assert "/login/" in response.url

    @pytest.mark.django_db
    def test_property_group_delete_view_authentication_integration_authenticated(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupDeleteView integration with authentication for authenticated user."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_delete_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_property_group_delete_view_authentication_integration_unauthenticated(self, client, sample_property_group):
        """Test PropertyGroupDeleteView integration with authentication for unauthenticated user."""
        response = client.post(reverse("lfs_delete_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 302
        assert "/login/" in response.url


class TestPropertyGroupViewPermissionIntegration:
    """Test property group view integration with permissions."""

    @pytest.mark.django_db
    def test_property_group_data_view_permission_integration_staff_user(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupDataView integration with permissions for staff user."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_property_group_data_view_permission_integration_regular_user(
        self, client, regular_user, sample_property_group
    ):
        """Test PropertyGroupDataView integration with permissions for regular user."""
        client.force_login(regular_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 403  # Permission denied

    @pytest.mark.django_db
    def test_property_group_create_view_permission_integration_staff_user(self, client, admin_user):
        """Test PropertyGroupCreateView integration with permissions for staff user."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_add_property_group"))

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_property_group_create_view_permission_integration_regular_user(self, client, regular_user):
        """Test PropertyGroupCreateView integration with permissions for regular user."""
        client.force_login(regular_user)

        response = client.get(reverse("lfs_manage_add_property_group"))

        assert response.status_code == 403  # Permission denied

    @pytest.mark.django_db
    def test_property_group_delete_view_permission_integration_staff_user(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupDeleteView integration with permissions for staff user."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_delete_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_property_group_delete_view_permission_integration_regular_user(
        self, client, regular_user, sample_property_group
    ):
        """Test PropertyGroupDeleteView integration with permissions for regular user."""
        client.force_login(regular_user)

        response = client.post(reverse("lfs_delete_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 403  # Permission denied


class TestPropertyGroupViewSearchIntegration:
    """Test property group view integration with search."""

    @pytest.mark.django_db
    def test_property_group_data_view_search_integration_with_query(self, client, admin_user, sample_property_group):
        """Test PropertyGroupDataView integration with search when query is provided."""
        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}), {"q": "Test"}
        )

        assert response.status_code == 200
        assert "search_query" in response.context
        assert response.context["search_query"] == "Test"

    @pytest.mark.django_db
    def test_property_group_data_view_search_integration_without_query(self, client, admin_user, sample_property_group):
        """Test PropertyGroupDataView integration with search when no query is provided."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200
        assert "search_query" in response.context
        assert response.context["search_query"] == ""

    @pytest.mark.django_db
    def test_property_group_data_view_search_integration_with_empty_query(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupDataView integration with search when empty query is provided."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}), {"q": ""})

        assert response.status_code == 200
        assert "search_query" in response.context
        assert response.context["search_query"] == ""

    @pytest.mark.django_db
    def test_property_group_data_view_search_integration_with_whitespace_query(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupDataView integration with search when whitespace query is provided."""
        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}), {"q": "   "}
        )

        assert response.status_code == 200
        assert "search_query" in response.context
        assert response.context["search_query"] == "   "

    @pytest.mark.django_db
    def test_property_group_data_view_search_integration_with_unicode_query(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupDataView integration with search when unicode query is provided."""
        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}), {"q": "测试"}
        )

        assert response.status_code == 200
        assert "search_query" in response.context
        assert response.context["search_query"] == "测试"

    @pytest.mark.django_db
    def test_property_group_data_view_search_integration_with_special_characters_query(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupDataView integration with search when special characters query is provided."""
        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}), {"q": "!@#$%^&*()"}
        )

        assert response.status_code == 200
        assert "search_query" in response.context
        assert response.context["search_query"] == "!@#$%^&*()"


class TestPropertyGroupViewPaginationIntegration:
    """Test property group view integration with pagination."""

    @pytest.mark.django_db
    def test_property_group_products_view_pagination_integration(self, client, admin_user, sample_property_group):
        """Test PropertyGroupProductsView integration with pagination."""
        # Create many products to test pagination
        for i in range(30):
            product = Product.objects.create(
                name=f"Product {i}", slug=f"product-{i}", price=Decimal(f"{i}.99"), active=True
            )
            sample_property_group.products.add(product)

        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group_products", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200
        assert "page" in response.context
        assert "paginator" in response.context

    @pytest.mark.django_db
    def test_property_group_products_view_pagination_integration_page_parameter(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupProductsView integration with pagination using page parameter."""
        # Create many products to test pagination
        for i in range(30):
            product = Product.objects.create(
                name=f"Product {i}", slug=f"product-{i}", price=Decimal(f"{i}.99"), active=True
            )
            sample_property_group.products.add(product)

        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_manage_property_group_products", kwargs={"id": sample_property_group.id}), {"page": 2}
        )

        assert response.status_code == 200
        assert "page" in response.context
        assert "paginator" in response.context

    @pytest.mark.django_db
    def test_property_group_products_view_pagination_integration_invalid_page(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupProductsView integration with pagination using invalid page parameter."""
        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_manage_property_group_products", kwargs={"id": sample_property_group.id}), {"page": "invalid"}
        )

        assert response.status_code == 200
        assert "page" in response.context
        assert "paginator" in response.context

    @pytest.mark.django_db
    def test_property_group_products_view_pagination_integration_out_of_range_page(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupProductsView integration with pagination using out of range page parameter."""
        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_manage_property_group_products", kwargs={"id": sample_property_group.id}), {"page": 999}
        )

        assert response.status_code == 200
        assert "page" in response.context
        assert "paginator" in response.context


class TestPropertyGroupViewFilteringIntegration:
    """Test property group view integration with filtering."""

    @pytest.mark.django_db
    def test_property_group_products_view_filtering_integration_name_filter(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupProductsView integration with filtering by name."""
        # Create products with different names
        product1 = Product.objects.create(
            name="Test Product 1", slug="test-product-1", price=Decimal("10.99"), active=True
        )
        product2 = Product.objects.create(
            name="Another Product", slug="another-product", price=Decimal("20.99"), active=True
        )
        product3 = Product.objects.create(
            name="Test Product 2", slug="test-product-2", price=Decimal("30.99"), active=True
        )

        sample_property_group.products.add(product1, product2, product3)

        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_manage_property_group_products", kwargs={"id": sample_property_group.id}), {"filter": "Test"}
        )

        assert response.status_code == 200
        assert "filter" in response.context
        assert response.context["filter"] == "Test"

    @pytest.mark.django_db
    def test_property_group_products_view_filtering_integration_category_filter(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupProductsView integration with filtering by category."""
        from lfs.catalog.models import Category

        # Create category
        category = Category.objects.create(name="Test Category", slug="test-category")

        # Create products with category
        product1 = Product.objects.create(
            name="Test Product 1", slug="test-product-1", price=Decimal("10.99"), active=True
        )
        product1.categories.add(category)

        sample_property_group.products.add(product1)

        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_manage_property_group_products", kwargs={"id": sample_property_group.id}),
            {"products_category_filter": str(category.id)},
        )

        assert response.status_code == 200
        assert "category_filter" in response.context
        assert response.context["category_filter"] == str(category.id)

    @pytest.mark.django_db
    def test_property_group_products_view_filtering_integration_combined_filters(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupProductsView integration with combined filters."""
        from lfs.catalog.models import Category

        # Create category
        category = Category.objects.create(name="Test Category", slug="test-category")

        # Create products
        product1 = Product.objects.create(
            name="Test Product 1", slug="test-product-1", price=Decimal("10.99"), active=True
        )
        product1.categories.add(category)

        sample_property_group.products.add(product1)

        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_manage_property_group_products", kwargs={"id": sample_property_group.id}),
            {"filter": "Test", "products_category_filter": str(category.id)},
        )

        assert response.status_code == 200
        assert "filter" in response.context
        assert "category_filter" in response.context
        assert response.context["filter"] == "Test"
        assert response.context["category_filter"] == str(category.id)


class TestPropertyGroupViewAJAXIntegration:
    """Test property group view integration with AJAX requests."""

    @pytest.mark.django_db
    def test_property_group_products_ajax_integration(self, client, admin_user, sample_property_group):
        """Test property group products AJAX integration."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group_products", kwargs={"id": sample_property_group.id}))

        assert response.status_code == 200
        assert "group_products" in response.context

    @pytest.mark.django_db
    def test_property_group_assign_properties_ajax_integration(
        self, client, admin_user, sample_property_group, sample_property
    ):
        """Test property group assign properties AJAX integration."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_assign_properties", kwargs={"group_id": sample_property_group.id}),
            {f"property-{sample_property.id}": "on"},
        )

        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"

    @pytest.mark.django_db
    def test_property_group_update_properties_ajax_integration(
        self, client, admin_user, sample_property_group, sample_property
    ):
        """Test property group update properties AJAX integration."""
        # First assign a property
        GroupsPropertiesRelation.objects.create(group=sample_property_group, property=sample_property, position=1)

        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_update_properties", kwargs={"group_id": sample_property_group.id}),
            {f"position-{sample_property.id}": "5"},
        )

        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"

    @pytest.mark.django_db
    def test_property_group_assign_products_ajax_integration(
        self, client, admin_user, sample_property_group, sample_product
    ):
        """Test property group assign products AJAX integration."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_assign_products_to_property_group", kwargs={"group_id": sample_property_group.id}),
            {f"product-{sample_product.id}": "on"},
        )

        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"

    @pytest.mark.django_db
    def test_property_group_remove_products_ajax_integration(
        self, client, admin_user, sample_property_group, sample_product
    ):
        """Test property group remove products AJAX integration."""
        # First assign a product
        sample_property_group.products.add(sample_product)

        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_pg_remove_products", kwargs={"group_id": sample_property_group.id}),
            {f"product-{sample_product.id}": "on"},
        )

        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"


class TestPropertyGroupViewErrorHandlingIntegration:
    """Test property group view integration with error handling."""

    @pytest.mark.django_db
    def test_property_group_data_view_error_handling_integration_nonexistent_id(self, client, admin_user):
        """Test PropertyGroupDataView error handling integration with nonexistent ID."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": 99999}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_property_group_data_view_error_handling_integration_invalid_id(self, client, admin_user):
        """Test PropertyGroupDataView error handling integration with invalid ID."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": "invalid"}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_property_group_data_view_error_handling_integration_negative_id(self, client, admin_user):
        """Test PropertyGroupDataView error handling integration with negative ID."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": -1}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_property_group_data_view_error_handling_integration_zero_id(self, client, admin_user):
        """Test PropertyGroupDataView error handling integration with zero ID."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": 0}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_property_group_data_view_error_handling_integration_form_validation_error(
        self, client, admin_user, sample_property_group
    ):
        """Test PropertyGroupDataView error handling integration with form validation error."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_manage_property_group", kwargs={"id": sample_property_group.id}), {"name": ""}
        )

        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()

    @pytest.mark.django_db
    def test_property_group_create_view_error_handling_integration_form_validation_error(self, client, admin_user):
        """Test PropertyGroupCreateView error handling integration with form validation error."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_manage_add_property_group"), {"name": ""})

        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()

    @pytest.mark.django_db
    def test_property_group_delete_view_error_handling_integration_nonexistent_id(self, client, admin_user):
        """Test PropertyGroupDeleteView error handling integration with nonexistent ID."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_delete_property_group", kwargs={"id": 99999}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_property_group_delete_view_error_handling_integration_invalid_id(self, client, admin_user):
        """Test PropertyGroupDeleteView error handling integration with invalid ID."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_delete_property_group", kwargs={"id": "invalid"}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_property_group_delete_view_error_handling_integration_negative_id(self, client, admin_user):
        """Test PropertyGroupDeleteView error handling integration with negative ID."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_delete_property_group", kwargs={"id": -1}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_property_group_delete_view_error_handling_integration_zero_id(self, client, admin_user):
        """Test PropertyGroupDeleteView error handling integration with zero ID."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_delete_property_group", kwargs={"id": 0}))

        assert response.status_code == 404
