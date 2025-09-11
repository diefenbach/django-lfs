"""
Comprehensive unit tests for property_groups views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- View method logic and context data
- Form handling and validation
- Permission checks
- Error handling
- Edge cases and boundary conditions
"""

import pytest
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import RequestFactory

from lfs.catalog.models import PropertyGroup, Property, Product
from lfs.manage.property_groups.views import (
    ManagePropertyGroupsView,
    PropertyGroupDataView,
    PropertyGroupProductsView,
    PropertyGroupPropertiesView,
    NoPropertyGroupsView,
    PropertyGroupCreateView,
    PropertyGroupDeleteConfirmView,
    PropertyGroupDeleteView,
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
def sample_product(shop):
    """Create a sample product for testing."""
    return Product.objects.create(name="Test Product", slug="test-product", price=10.99, active=True)


class TestManagePropertyGroupsViewUnit:
    """Unit tests for ManagePropertyGroupsView."""

    @pytest.mark.django_db
    def test_get_redirect_url_redirects_to_first_property_group(self, mock_request, admin_user, sample_property_group):
        """Test that get_redirect_url redirects to first property group when groups exist."""
        view = ManagePropertyGroupsView()
        view.request = mock_request
        view.request.user = admin_user

        url = view.get_redirect_url()

        assert str(sample_property_group.id) in url
        assert "property-group" in url

    @pytest.mark.django_db
    def test_get_redirect_url_redirects_to_no_groups_when_none_exist(self, mock_request, admin_user):
        """Test that get_redirect_url redirects to no groups view when no groups exist."""
        view = ManagePropertyGroupsView()
        view.request = mock_request
        view.request.user = admin_user

        url = view.get_redirect_url()

        assert "no-property-groups" in url

    @pytest.mark.django_db
    def test_permission_required_is_correct(self, mock_request, regular_user):
        """Test that permission_required is set correctly."""
        view = ManagePropertyGroupsView()
        view.request = mock_request
        view.request.user = regular_user

        assert view.permission_required == "core.manage_shop"


class TestPropertyGroupDataViewUnit:
    """Unit tests for PropertyGroupDataView."""

    @pytest.mark.django_db
    def test_get_property_group_returns_property_group_by_id(self, mock_request, admin_user, sample_property_group):
        """Test that get_property_group returns property group by ID."""
        view = PropertyGroupDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": sample_property_group.id}

        result = view.get_property_group()

        assert result == sample_property_group

    @pytest.mark.django_db
    def test_get_property_group_raises_404_for_nonexistent_group(self, mock_request, admin_user):
        """Test that get_property_group raises 404 for nonexistent property group."""
        view = PropertyGroupDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": 99999}

        with pytest.raises(Http404):
            view.get_property_group()

    @pytest.mark.django_db
    def test_get_context_data_includes_required_keys(self, mock_request, admin_user, sample_property_group):
        """Test that get_context_data includes all required context keys."""
        view = PropertyGroupDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group), patch.object(
            view,
            "_get_tabs",
            return_value=[("data", "/data/"), ("products", "/products/"), ("properties", "/properties/")],
        ), patch.object(
            view, "_get_navigation_context", return_value={"property_groups": PropertyGroup.objects.none()}
        ):
            context = view.get_context_data()

            assert "property_group" in context
            assert "active_tab" in context
            assert "tabs" in context
            assert context["active_tab"] == "data"

    @pytest.mark.django_db
    def test_get_success_url_redirects_to_property_group_view(self, mock_request, admin_user, sample_property_group):
        """Test that get_success_url redirects to property group view."""
        view = PropertyGroupDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.object = sample_property_group

        url = view.get_success_url()

        assert str(sample_property_group.id) in url
        assert "property-group" in url

    @pytest.mark.django_db
    def test_form_valid_shows_success_message(self, mock_request, admin_user, sample_property_group):
        """Test that form_valid shows success message."""
        view = PropertyGroupDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.object = sample_property_group

        with patch("django.contrib.messages.success") as mock_success:
            from lfs.manage.property_groups.forms import PropertyGroupForm

            form = PropertyGroupForm(data={"name": "Updated Name"})
            form.is_valid()

            view.form_valid(form)

            mock_success.assert_called_once()

    @pytest.mark.django_db
    def test_permission_required_is_correct(self, mock_request, regular_user):
        """Test that permission_required is set correctly."""
        view = PropertyGroupDataView()
        view.request = mock_request
        view.request.user = regular_user

        assert view.permission_required == "core.manage_shop"


class TestPropertyGroupProductsViewUnit:
    """Unit tests for PropertyGroupProductsView."""

    @pytest.mark.django_db
    def test_get_context_data_includes_required_keys(self, mock_request, admin_user, sample_property_group):
        """Test that get_context_data includes all required context keys."""
        view = PropertyGroupProductsView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group), patch.object(
            view,
            "_get_tabs",
            return_value=[("data", "/data/"), ("products", "/products/"), ("properties", "/properties/")],
        ), patch.object(
            view, "_get_navigation_context", return_value={"property_groups": PropertyGroup.objects.none()}
        ):
            context = view.get_context_data()

            assert "property_group" in context
            assert "active_tab" in context
            assert "tabs" in context
            assert context["active_tab"] == "products"

    @pytest.mark.django_db
    def test_get_context_data_includes_products_data(
        self, mock_request, admin_user, sample_property_group, sample_product
    ):
        """Test that get_context_data includes products data."""
        view = PropertyGroupProductsView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group), patch.object(
            view,
            "_get_tabs",
            return_value=[("data", "/data/"), ("products", "/products/"), ("properties", "/properties/")],
        ), patch.object(
            view, "_get_navigation_context", return_value={"property_groups": PropertyGroup.objects.none()}
        ):
            context = view.get_context_data()

            assert "group_products" in context
            assert "page" in context
            assert "paginator" in context
            assert "filter" in context
            assert "category_filter" in context

    @pytest.mark.django_db
    def test_permission_required_is_correct(self, mock_request, regular_user):
        """Test that permission_required is set correctly."""
        view = PropertyGroupProductsView()
        view.request = mock_request
        view.request.user = regular_user

        assert view.permission_required == "core.manage_shop"


class TestPropertyGroupPropertiesViewUnit:
    """Unit tests for PropertyGroupPropertiesView."""

    @pytest.mark.django_db
    def test_get_context_data_includes_required_keys(self, mock_request, admin_user, sample_property_group):
        """Test that get_context_data includes all required context keys."""
        view = PropertyGroupPropertiesView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group), patch.object(
            view,
            "_get_tabs",
            return_value=[("data", "/data/"), ("products", "/products/"), ("properties", "/properties/")],
        ), patch.object(
            view, "_get_navigation_context", return_value={"property_groups": PropertyGroup.objects.none()}
        ):
            context = view.get_context_data()

            assert "property_group" in context
            assert "active_tab" in context
            assert "tabs" in context
            assert context["active_tab"] == "properties"

    @pytest.mark.django_db
    def test_get_context_data_includes_properties_data(self, mock_request, admin_user, sample_property_group):
        """Test that get_context_data includes properties data."""
        view = PropertyGroupPropertiesView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group), patch.object(
            view,
            "_get_tabs",
            return_value=[("data", "/data/"), ("products", "/products/"), ("properties", "/properties/")],
        ), patch.object(
            view, "_get_navigation_context", return_value={"property_groups": PropertyGroup.objects.none()}
        ):
            context = view.get_context_data()

            assert "properties" in context
            assert "group_properties" in context

    @pytest.mark.django_db
    def test_permission_required_is_correct(self, mock_request, regular_user):
        """Test that permission_required is set correctly."""
        view = PropertyGroupPropertiesView()
        view.request = mock_request
        view.request.user = regular_user

        assert view.permission_required == "core.manage_shop"


class TestNoPropertyGroupsViewUnit:
    """Unit tests for NoPropertyGroupsView."""

    @pytest.mark.django_db
    def test_get_renders_no_property_groups_template(self, mock_request, admin_user):
        """Test that GET renders no property groups template."""
        view = NoPropertyGroupsView()
        view.request = mock_request
        view.request.user = admin_user

        response = view.get(mock_request)

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_permission_required_is_correct(self, mock_request, regular_user):
        """Test that permission_required is set correctly."""
        view = NoPropertyGroupsView()
        view.request = mock_request
        view.request.user = regular_user

        assert view.permission_required == "core.manage_shop"


class TestPropertyGroupCreateViewUnit:
    """Unit tests for PropertyGroupCreateView."""

    @pytest.mark.django_db
    def test_get_success_url_redirects_to_property_group_view(self, mock_request, admin_user):
        """Test that get_success_url redirects to property group view."""
        view = PropertyGroupCreateView()
        view.request = mock_request
        view.request.user = admin_user
        view.object = PropertyGroup(id=123)

        url = view.get_success_url()

        assert "123" in url
        assert "property-group" in url

    @pytest.mark.django_db
    def test_get_context_data_includes_required_keys(self, mock_request, admin_user):
        """Test that get_context_data includes all required context keys."""
        view = PropertyGroupCreateView()
        view.request = mock_request
        view.request.user = admin_user

        context = view.get_context_data()

        assert "property_groups" in context
        assert "came_from" in context

    @pytest.mark.django_db
    def test_permission_required_is_correct(self, mock_request, regular_user):
        """Test that permission_required is set correctly."""
        view = PropertyGroupCreateView()
        view.request = mock_request
        view.request.user = regular_user

        assert view.permission_required == "core.manage_shop"


class TestPropertyGroupDeleteViewsUnit:
    """Unit tests for property group deletion views."""

    @pytest.mark.django_db
    def test_property_group_delete_confirm_view_get_context_data(self, mock_request, admin_user, sample_property_group):
        """Test that PropertyGroupDeleteConfirmView includes property group in context."""
        view = PropertyGroupDeleteConfirmView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": sample_property_group.id}

        context = view.get_context_data()

        assert "property_group" in context
        assert context["property_group"] == sample_property_group

    @pytest.mark.django_db
    def test_property_group_delete_view_post_deletes_property_group(
        self, mock_request, admin_user, sample_property_group
    ):
        """Test that PropertyGroupDeleteView POST deletes the property group."""
        property_group_id = sample_property_group.id
        view = PropertyGroupDeleteView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": property_group_id}

        with patch.object(view, "get_success_url", return_value="/success/"):
            # Call the delete method directly instead of post
            view.delete(mock_request)

            assert not PropertyGroup.objects.filter(id=property_group_id).exists()

    @pytest.mark.django_db
    def test_property_group_delete_view_get_success_url_redirects_to_property_groups_list(
        self, mock_request, admin_user
    ):
        """Test that PropertyGroupDeleteView get_success_url redirects to property groups list."""
        view = PropertyGroupDeleteView()
        view.request = mock_request
        view.request.user = admin_user

        url = view.get_success_url()

        assert "property-groups" in url

    @pytest.mark.django_db
    def test_permission_required_is_correct(self, mock_request, regular_user):
        """Test that permission_required is set correctly."""
        view = PropertyGroupDeleteView()
        view.request = mock_request
        view.request.user = regular_user

        assert view.permission_required == "core.manage_shop"


class TestPropertyGroupTabMixinUnit:
    """Unit tests for PropertyGroupTabMixin."""

    @pytest.mark.django_db
    def test_get_property_groups_queryset_returns_property_group_queryset(self, mock_request, admin_user):
        """Test that get_property_groups_queryset returns PropertyGroup queryset."""
        view = PropertyGroupDataView()
        view.request = mock_request
        view.request.user = admin_user

        queryset = view.get_property_groups_queryset()

        assert queryset.model == PropertyGroup

    @pytest.mark.django_db
    def test_get_property_groups_queryset_applies_search_filter(self, mock_request, admin_user, sample_property_group):
        """Test that get_property_groups_queryset applies search filter."""
        view = PropertyGroupDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"q": "Test"}

        queryset = view.get_property_groups_queryset()

        assert queryset.count() == 1
        assert queryset.first() == sample_property_group

    @pytest.mark.django_db
    def test_get_property_groups_queryset_handles_empty_search(self, mock_request, admin_user, sample_property_group):
        """Test that get_property_groups_queryset handles empty search gracefully."""
        view = PropertyGroupDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"q": ""}

        queryset = view.get_property_groups_queryset()

        assert queryset.count() == 1
        assert queryset.first() == sample_property_group

    @pytest.mark.django_db
    def test_get_tabs_returns_correct_tabs(self, mock_request, admin_user, sample_property_group):
        """Test that _get_tabs returns correct tab structure."""
        view = PropertyGroupDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.kwargs = {"id": sample_property_group.id}

        tabs = view._get_tabs(sample_property_group)

        assert len(tabs) == 3
        tab_names = [tab[0] for tab in tabs]
        assert "data" in tab_names
        assert "products" in tab_names
        assert "properties" in tab_names

    @pytest.mark.django_db
    def test_get_tabs_includes_search_parameter(self, mock_request, admin_user, sample_property_group):
        """Test that _get_tabs includes search parameter in URLs."""
        view = PropertyGroupDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"q": "test"}
        view.kwargs = {"id": sample_property_group.id}

        tabs = view._get_tabs(sample_property_group)

        for tab_name, tab_url in tabs:
            assert "q=test" in tab_url

    @pytest.mark.django_db
    def test_get_navigation_context_returns_required_data(self, mock_request, admin_user, sample_property_group):
        """Test that _get_navigation_context returns required data."""
        view = PropertyGroupDataView()
        view.request = mock_request
        view.request.user = admin_user
        view.request.GET = {"q": "test"}

        context = view._get_navigation_context(sample_property_group)

        assert "property_group" in context
        assert "property_groups" in context
        assert "search_query" in context
        assert context["property_group"] == sample_property_group
        assert context["search_query"] == "test"
