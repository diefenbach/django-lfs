"""
Unit tests for Tools views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Parametrization for variations
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.test import RequestFactory
from django.views.generic.base import TemplateView

from lfs.manage.tools.views import ToolsView

User = get_user_model()


class TestToolsView:
    """Test the ToolsView class."""

    def test_view_inheritance(self):
        """Should inherit from PermissionRequiredMixin and TemplateView."""
        assert issubclass(ToolsView, PermissionRequiredMixin)
        assert issubclass(ToolsView, TemplateView)

    def test_template_name(self):
        """Should use correct template."""
        assert ToolsView.template_name == "manage/tools/tools.html"

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ToolsView.permission_required == "core.manage_shop"

    def test_get_context_data_returns_utilities_list(self, mock_request):
        """Should return utilities list in context."""
        view = ToolsView()
        view.request = mock_request

        context = view.get_context_data()

        assert "utilities" in context
        assert isinstance(context["utilities"], list)
        assert len(context["utilities"]) == 4

    def test_get_context_data_utilities_have_required_keys(self, mock_request):
        """Should include all required keys in each utility."""
        view = ToolsView()
        view.request = mock_request

        context = view.get_context_data()
        utilities = context["utilities"]

        required_keys = {"name", "description", "url", "icon"}
        for utility in utilities:
            assert set(utility.keys()) == required_keys

    @pytest.mark.parametrize(
        "utility_index,expected_name,expected_icon",
        [
            (0, "Clear Cache", "bi-arrow-clockwise"),
            (1, "Set Category Levels", "bi-diagram-3"),
            (2, "Reindex Topseller", "bi-star"),
            (3, "Update Effective Prices", "bi-currency-dollar"),
        ],
    )
    def test_get_context_data_utility_names_and_icons(self, mock_request, utility_index, expected_name, expected_icon):
        """Should have correct names and icons for each utility."""
        view = ToolsView()
        view.request = mock_request

        context = view.get_context_data()
        utility = context["utilities"][utility_index]

        assert utility["name"] == expected_name
        assert utility["icon"] == expected_icon

    def test_get_context_data_utility_urls_are_valid(self, mock_request):
        """Should have valid URLs for each utility."""
        view = ToolsView()
        view.request = mock_request

        context = view.get_context_data()
        utilities = context["utilities"]

        expected_urls = [
            reverse("lfs_manage_clear_cache"),
            reverse("lfs_manage_set_category_levels"),
            reverse("lfs_manage_reindex_topseller"),
            reverse("lfs_manage_update_effective_price"),
        ]

        actual_urls = [utility["url"] for utility in utilities]
        assert actual_urls == expected_urls

    def test_get_context_data_utility_descriptions_are_present(self, mock_request):
        """Should have non-empty descriptions for each utility."""
        view = ToolsView()
        view.request = mock_request

        context = view.get_context_data()
        utilities = context["utilities"]

        for utility in utilities:
            assert utility["description"]
            assert len(utility["description"]) > 0

    def test_view_works_with_regular_user(self, regular_user):
        """Should work with regular user (permission check is at mixin level)."""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = regular_user
        request.session = {}

        view = ToolsView()
        view.request = request

        # The view should work but permission check happens at the mixin level
        context = view.get_context_data()
        assert "utilities" in context

    def test_view_allows_authenticated_admin(self, mock_request):
        """Should allow authenticated admin users."""
        view = ToolsView()
        view.request = mock_request

        # This should not raise an exception
        context = view.get_context_data()
        assert "utilities" in context
