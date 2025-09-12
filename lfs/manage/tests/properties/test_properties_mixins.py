"""
Comprehensive unit tests for property mixins.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- PropertyNavigationMixin navigation and search functionality
- Context data provision
- Edge cases and error conditions
"""

import pytest
from unittest.mock import patch

from django.http import Http404

from lfs.catalog.models import Property
from lfs.manage.properties.views import PropertyNavigationMixin


class TestPropertyNavigationMixin:
    """Test PropertyNavigationMixin functionality."""

    @pytest.mark.django_db
    def test_get_property_returns_property_object(self, mock_request):
        """Test that get_property returns the correct Property object."""
        property_obj = Property.objects.create(name="Test Property", title="Test Property")
        mixin = PropertyNavigationMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": property_obj.id}

        result = mixin.get_property()

        assert result == property_obj
        assert isinstance(result, Property)

    @pytest.mark.django_db
    def test_get_property_raises_404_for_nonexistent_property(self, mock_request):
        """Test that get_property raises Http404 for non-existent property."""
        mixin = PropertyNavigationMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": 99999}  # Non-existent ID

        with pytest.raises(Http404):
            mixin.get_property()

    @pytest.mark.django_db
    def test_get_properties_queryset_returns_queryset(self, mock_request):
        """Test that get_properties_queryset returns a queryset."""
        Property.objects.create(name="Test Property", title="Test Property")
        mixin = PropertyNavigationMixin()
        mixin.request = mock_request

        queryset = mixin.get_properties_queryset()

        assert hasattr(queryset, "filter")  # It's a queryset
        assert queryset.model == Property

    @pytest.mark.django_db
    def test_get_properties_queryset_excludes_local_properties(self, mock_request):
        """Test that get_properties_queryset excludes local properties."""
        # Create local property
        Property.objects.create(name="Local Property", title="Local Property", local=True)
        # Create non-local property
        Property.objects.create(name="Global Property", title="Global Property", local=False)

        mixin = PropertyNavigationMixin()
        mixin.request = mock_request

        queryset = mixin.get_properties_queryset()

        # Should only include the global property
        assert queryset.count() == 1
        assert queryset.first().local is False

    @pytest.mark.django_db
    def test_get_properties_queryset_orders_by_name(self, mock_request, sample_properties):
        """Test that get_properties_queryset orders properties by name."""
        mixin = PropertyNavigationMixin()
        mixin.request = mock_request

        queryset = mixin.get_properties_queryset()
        properties_list = list(queryset)

        # Check that properties are ordered alphabetically by name
        names = [p.name for p in properties_list]
        assert names == sorted(names)

    @pytest.mark.django_db
    def test_get_properties_queryset_filters_by_search_query(self, request_factory, mock_request, sample_properties):
        """Test that get_properties_queryset filters by search query."""
        # Create request with search query
        request = request_factory.get("/?q=col")
        mixin = PropertyNavigationMixin()
        mixin.request = request

        queryset = mixin.get_properties_queryset()

        # Should only return properties containing "col" in name or title
        properties_list = list(queryset)
        assert len(properties_list) == 1
        assert "Color" in properties_list[0].name

    @pytest.mark.django_db
    def test_get_properties_queryset_search_case_insensitive(self, request_factory, mock_request, sample_properties):
        """Test that search is case insensitive."""
        # Create request with mixed case search query
        request = request_factory.get("/?q=COL")
        mixin = PropertyNavigationMixin()
        mixin.request = request

        queryset = mixin.get_properties_queryset()

        # Should find "Color" property despite case difference
        properties_list = list(queryset)
        assert len(properties_list) == 1
        assert properties_list[0].name == "Color"

    @pytest.mark.django_db
    def test_get_properties_queryset_search_title_field(self, request_factory, mock_request, sample_properties):
        """Test that search works on title field as well as name."""
        # Search for "Material" in title
        request = request_factory.get("/?q=Material")
        mixin = PropertyNavigationMixin()
        mixin.request = request

        queryset = mixin.get_properties_queryset()

        properties_list = list(queryset)
        assert len(properties_list) == 1
        assert properties_list[0].title == "Material"

    @pytest.mark.django_db
    def test_get_properties_queryset_empty_search_returns_all(self, request_factory, mock_request, sample_properties):
        """Test that empty search query returns all properties."""
        request = request_factory.get("/?q=")
        mixin = PropertyNavigationMixin()
        mixin.request = request

        queryset = mixin.get_properties_queryset()

        # Should return all non-local properties
        assert queryset.count() == len(sample_properties)

    @pytest.mark.django_db
    def test_get_properties_queryset_no_search_param_returns_all(self, mock_request, sample_properties):
        """Test that no search parameter returns all properties."""
        mixin = PropertyNavigationMixin()
        mixin.request = mock_request

        queryset = mixin.get_properties_queryset()

        # Should return all non-local properties
        assert queryset.count() == len(sample_properties)

    def test_get_context_data_calls_super_and_adds_property_data(self, mock_request):
        """Test that get_context_data calls super() and adds property/navigation data."""
        mixin = PropertyNavigationMixin()
        mixin.request = mock_request
        mixin.object = Property(name="Test Property", title="Test Property")  # Mock object

        # Mock the super() call to return base context
        with patch("builtins.super") as mock_super:
            mock_super.return_value.get_context_data.return_value = {"base_context": True}

            # Mock the navigation context method
            with patch.object(mixin, "_get_navigation_context", return_value={"nav": "data"}):
                context = mixin.get_context_data()

                # Check that super().get_context_data was called
                mock_super.return_value.get_context_data.assert_called_once()

                # Check that context includes base context
                assert context["base_context"] is True

                # Check that property is included
                assert "property" in context
                assert context["property"].name == "Test Property"

                # Check that navigation data is included
                assert context["nav"] == "data"

    def test_get_context_data_prefers_object_over_get_property(self, mock_request):
        """Test that get_context_data uses object attribute if available, otherwise calls get_property()."""
        mixin = PropertyNavigationMixin()
        mixin.request = mock_request
        property_obj = Property(name="Test Property", title="Test Property")

        # Test with object attribute set
        mixin.object = property_obj

        with patch("builtins.super") as mock_super:
            mock_super.return_value.get_context_data.return_value = {"base_context": True}

            with patch.object(mixin, "_get_navigation_context", return_value={"nav": "data"}):
                context = mixin.get_context_data()

                # Should use mixin.object instead of calling get_property()
                assert context["property"] == property_obj
                assert context["property"].name == "Test Property"

    @pytest.mark.django_db
    def test_get_navigation_context_includes_expected_data(self, mock_request, sample_properties):
        """Test that _get_navigation_context includes expected navigation data."""
        property_obj = Property.objects.create(name="Test Property", title="Test Property")
        mixin = PropertyNavigationMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": property_obj.id}

        nav_context = mixin._get_navigation_context(property_obj)

        expected_keys = ["property", "properties", "page", "search_query"]
        for key in expected_keys:
            assert key in nav_context

        assert nav_context["property"] == property_obj
        assert nav_context["search_query"] == ""

    @pytest.mark.django_db
    def test_get_navigation_context_with_search_query(self, request_factory, mock_request, sample_properties):
        """Test that _get_navigation_context includes search query."""
        property_obj = Property.objects.create(name="Test Property", title="Test Property")
        request = request_factory.get("/?q=test")
        mixin = PropertyNavigationMixin()
        mixin.request = request
        mixin.kwargs = {"id": property_obj.id}

        nav_context = mixin._get_navigation_context(property_obj)

        assert nav_context["search_query"] == "test"
