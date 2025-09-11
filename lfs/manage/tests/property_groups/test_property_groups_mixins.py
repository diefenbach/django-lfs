"""
Comprehensive unit tests for property_groups mixins.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- PropertyGroupTabMixin functionality
- Tab navigation and context data
- Search functionality
- Navigation context generation
- Tab URL generation with search parameters
"""

import pytest
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.catalog.models import PropertyGroup, Property, Product
from lfs.manage.property_groups.views import PropertyGroupDataView

User = get_user_model()


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def admin_user():
    """Admin user for testing."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


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


class TestPropertyGroupTabMixin:
    """Test PropertyGroupTabMixin functionality."""

    @pytest.mark.django_db
    def test_get_property_group_returns_correct_group(self, request_factory, admin_user, sample_property_group):
        """Test that get_property_group returns the correct property group."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        result = view.get_property_group()
        assert result == sample_property_group

    @pytest.mark.django_db
    def test_get_property_groups_queryset_returns_property_group_queryset(self, request_factory, admin_user):
        """Test that get_property_groups_queryset returns PropertyGroup queryset."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request

        queryset = view.get_property_groups_queryset()
        assert queryset.model == PropertyGroup

    @pytest.mark.django_db
    def test_get_property_groups_queryset_applies_search_filter(
        self, request_factory, admin_user, sample_property_group
    ):
        """Test that get_property_groups_queryset applies search filter."""
        request = request_factory.get("/", {"q": "Test"})
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request

        queryset = view.get_property_groups_queryset()
        assert queryset.count() == 1
        assert queryset.first() == sample_property_group

    @pytest.mark.django_db
    def test_get_property_groups_queryset_handles_empty_search(
        self, request_factory, admin_user, sample_property_group
    ):
        """Test that get_property_groups_queryset handles empty search gracefully."""
        request = request_factory.get("/", {"q": ""})
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request

        queryset = view.get_property_groups_queryset()
        assert queryset.count() == 1
        assert queryset.first() == sample_property_group

    @pytest.mark.django_db
    def test_get_property_groups_queryset_handles_none_search(self, request_factory, admin_user, sample_property_group):
        """Test that get_property_groups_queryset handles None search gracefully."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request

        queryset = view.get_property_groups_queryset()
        assert queryset.count() == 1
        assert queryset.first() == sample_property_group

    @pytest.mark.django_db
    def test_get_property_groups_queryset_handles_whitespace_search(
        self, request_factory, admin_user, sample_property_group
    ):
        """Test that get_property_groups_queryset handles whitespace search gracefully."""
        request = request_factory.get("/", {"q": "   "})
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request

        queryset = view.get_property_groups_queryset()
        assert queryset.count() == 1
        assert queryset.first() == sample_property_group

    @pytest.mark.django_db
    def test_get_tabs_returns_correct_tabs(self, request_factory, admin_user, sample_property_group):
        """Test that _get_tabs returns correct tab structure."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        tabs = view._get_tabs(sample_property_group)
        assert len(tabs) == 3
        tab_names = [tab[0] for tab in tabs]
        assert "data" in tab_names
        assert "products" in tab_names
        assert "properties" in tab_names

    @pytest.mark.django_db
    def test_get_tabs_includes_search_parameter(self, request_factory, admin_user, sample_property_group):
        """Test that _get_tabs includes search parameter in URLs."""
        request = request_factory.get("/", {"q": "test"})
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        tabs = view._get_tabs(sample_property_group)
        for tab_name, tab_url in tabs:
            assert "q=test" in tab_url

    @pytest.mark.django_db
    def test_get_tabs_without_search_parameter(self, request_factory, admin_user, sample_property_group):
        """Test that _get_tabs works without search parameter."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        tabs = view._get_tabs(sample_property_group)
        for tab_name, tab_url in tabs:
            assert "q=" not in tab_url

    @pytest.mark.django_db
    def test_get_navigation_context_returns_required_data(self, request_factory, admin_user, sample_property_group):
        """Test that _get_navigation_context returns required data."""
        request = request_factory.get("/", {"q": "test"})
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request

        context = view._get_navigation_context(sample_property_group)
        assert "property_group" in context
        assert "property_groups" in context
        assert "search_query" in context
        assert context["property_group"] == sample_property_group
        assert context["search_query"] == "test"

    @pytest.mark.django_db
    def test_get_navigation_context_without_search(self, request_factory, admin_user, sample_property_group):
        """Test that _get_navigation_context works without search query."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request

        context = view._get_navigation_context(sample_property_group)
        assert "property_group" in context
        assert "property_groups" in context
        assert "search_query" in context
        assert context["property_group"] == sample_property_group
        assert context["search_query"] == ""

    @pytest.mark.django_db
    def test_get_context_data_includes_tab_data(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data includes tab-related data."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group):
            context = view.get_context_data()

            assert "property_group" in context
            assert "active_tab" in context
            assert "tabs" in context
            assert "property_groups" in context
            assert "search_query" in context

    @pytest.mark.django_db
    def test_get_context_data_with_search_query(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data includes search query in context."""
        request = request_factory.get("/", {"q": "test"})
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group):
            context = view.get_context_data()

            assert context["search_query"] == "test"

    @pytest.mark.django_db
    def test_get_context_data_with_empty_search_query(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data handles empty search query."""
        request = request_factory.get("/", {"q": ""})
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group):
            context = view.get_context_data()

            assert context["search_query"] == ""

    @pytest.mark.django_db
    def test_get_context_data_with_none_search_query(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data handles None search query."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group):
            context = view.get_context_data()

            assert context["search_query"] == ""

    @pytest.mark.django_db
    def test_get_context_data_with_whitespace_search_query(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data handles whitespace search query."""
        request = request_factory.get("/", {"q": "   "})
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group):
            context = view.get_context_data()

            assert context["search_query"] == "   "

    @pytest.mark.django_db
    def test_get_context_data_includes_property_groups_queryset(
        self, request_factory, admin_user, sample_property_group
    ):
        """Test that get_context_data includes property groups queryset."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group):
            context = view.get_context_data()

            assert "property_groups" in context
            assert context["property_groups"].model == PropertyGroup

    @pytest.mark.django_db
    def test_get_context_data_includes_active_tab(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data includes active tab."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group):
            context = view.get_context_data()

            assert "active_tab" in context
            assert context["active_tab"] == "data"

    @pytest.mark.django_db
    def test_get_context_data_includes_tabs_list(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data includes tabs list."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group):
            context = view.get_context_data()

            assert "tabs" in context
            assert isinstance(context["tabs"], list)
            assert len(context["tabs"]) == 3

    @pytest.mark.django_db
    def test_get_context_data_includes_property_group(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data includes property group."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group):
            context = view.get_context_data()

            assert "property_group" in context
            assert context["property_group"] == sample_property_group

    @pytest.mark.django_db
    def test_get_context_data_with_object_attribute(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data works with object attribute."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}
        view.object = sample_property_group  # Set object attribute

        context = view.get_context_data()

        assert "property_group" in context
        assert context["property_group"] == sample_property_group

    @pytest.mark.django_db
    def test_get_context_data_without_object_attribute(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data works without object attribute."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group):
            context = view.get_context_data()

            assert "property_group" in context
            assert context["property_group"] == sample_property_group

    @pytest.mark.django_db
    def test_get_context_data_extends_existing_context(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data extends existing context."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group):
            existing_context = {"existing_key": "existing_value"}
            context = view.get_context_data(**existing_context)

            assert "existing_key" in context
            assert context["existing_key"] == "existing_value"
            assert "property_group" in context
            assert context["property_group"] == sample_property_group

    @pytest.mark.django_db
    def test_get_context_data_overwrites_existing_context(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data overwrites existing context with same keys."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group):
            existing_context = {"property_group": "old_value"}
            context = view.get_context_data(**existing_context)

            assert "property_group" in context
            assert context["property_group"] == sample_property_group  # Should be overwritten
            assert context["property_group"] != "old_value"

    @pytest.mark.django_db
    def test_get_context_data_calls_super_get_context_data(self, request_factory, admin_user, sample_property_group):
        """Test that get_context_data calls super get_context_data."""
        request = request_factory.get("/")
        request.user = admin_user

        view = PropertyGroupDataView()
        view.request = request
        view.kwargs = {"id": sample_property_group.id}

        with patch.object(view, "get_property_group", return_value=sample_property_group), patch.object(
            view.__class__.__mro__[3], "get_context_data"  # UpdateView is the 4th class in MRO
        ) as mock_super:
            mock_super.return_value = {"super_key": "super_value"}

            context = view.get_context_data()

            mock_super.assert_called_once()
            assert "super_key" in context
            assert context["super_key"] == "super_value"
