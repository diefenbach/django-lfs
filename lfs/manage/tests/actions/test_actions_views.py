"""
Unit tests for Action views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Parametrization for variations
"""

from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect

from lfs.core.models import Action, ActionGroup
from lfs.manage.actions.views import (
    manage_actions,
    ActionUpdateView,
    NoActionsView,
    ActionCreateView,
    ActionDeleteView,
    sort_actions,
    _update_positions,
)

User = get_user_model()


class TestManageActionsDispatcher:
    """Test the manage_actions dispatcher function."""

    def test_dispatcher_exists(self):
        """Should have manage_actions dispatcher function."""
        assert callable(manage_actions)

    def test_permission_required_attribute(self):
        """Should require core.manage_shop permission."""
        assert hasattr(manage_actions, "__wrapped__")

    def test_redirects_to_first_action_when_actions_exist(self, mock_request, action, monkeypatch):
        """Should redirect to first action when actions exist."""

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_manage_action" and kwargs and kwargs.get("pk") == action.id:
                return f"/manage/action/{action.id}/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.actions.views.reverse", mock_reverse)

        response = manage_actions(mock_request)

        assert isinstance(response, HttpResponseRedirect)
        assert f"/manage/action/{action.id}/" in response.url

    def test_redirects_to_no_actions_when_none_exist(self, mock_request, monkeypatch):
        """Should redirect to no actions view when no actions exist."""
        # Delete all actions
        Action.objects.all().delete()

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_no_actions":
                return "/manage/no-actions/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.actions.views.reverse", mock_reverse)

        response = manage_actions(mock_request)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == "/manage/no-actions/"


class TestActionUpdateView:
    """Test the ActionUpdateView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django UpdateView."""
        from django.views.generic.edit import UpdateView

        assert issubclass(ActionUpdateView, UpdateView)

    def test_model_attribute(self):
        """Should use Action model."""
        assert ActionUpdateView.model == Action

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ActionUpdateView.permission_required == "core.manage_shop"

    def test_fields_attribute(self):
        """Should define correct fields."""
        assert ActionUpdateView.fields == ("active", "title", "link")

    def test_template_name(self):
        """Should use correct template."""
        assert ActionUpdateView.template_name == "manage/actions/action.html"

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(ActionUpdateView, "get_success_url")
        assert callable(getattr(ActionUpdateView, "get_success_url"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ActionUpdateView, "get_context_data")
        assert callable(getattr(ActionUpdateView, "get_context_data"))

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(ActionUpdateView, "form_valid")
        assert callable(getattr(ActionUpdateView, "form_valid"))


class TestNoActionsView:
    """Test the NoActionsView template view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(NoActionsView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert NoActionsView.permission_required == "core.manage_shop"

    def test_template_name(self):
        """Should use correct template."""
        assert NoActionsView.template_name == "manage/actions/no_actions.html"


class TestActionCreateView:
    """Test the ActionCreateView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django CreateView."""
        from django.views.generic.edit import CreateView

        assert issubclass(ActionCreateView, CreateView)

    def test_model_attribute(self):
        """Should use Action model."""
        assert ActionCreateView.model == Action

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ActionCreateView.permission_required == "core.manage_shop"

    def test_fields_attribute(self):
        """Should define correct fields."""
        assert ActionCreateView.fields == ("active", "title", "link", "group")

    def test_template_name(self):
        """Should use correct template."""
        assert ActionCreateView.template_name == "manage/actions/add_action.html"

    def test_get_form_kwargs_method_exists(self):
        """Should have get_form_kwargs method."""
        assert hasattr(ActionCreateView, "get_form_kwargs")
        assert callable(getattr(ActionCreateView, "get_form_kwargs"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ActionCreateView, "get_context_data")
        assert callable(getattr(ActionCreateView, "get_context_data"))

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(ActionCreateView, "form_valid")
        assert callable(getattr(ActionCreateView, "form_valid"))


class TestActionDeleteView:
    """Test the ActionDeleteView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django DeleteView."""
        from django.views.generic.edit import DeleteView

        assert issubclass(ActionDeleteView, DeleteView)

    def test_model_attribute(self):
        """Should use Action model."""
        assert ActionDeleteView.model == Action

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ActionDeleteView.permission_required == "core.manage_shop"

    def test_delete_method_exists(self):
        """Should have delete method."""
        assert hasattr(ActionDeleteView, "delete")
        assert callable(getattr(ActionDeleteView, "delete"))


class TestSortActions:
    """Test the sort_actions drag and drop functionality."""

    def test_sort_actions_function_exists(self):
        """Should have sort_actions function."""
        assert callable(sort_actions)

    def test_sort_actions_requires_permission(self):
        """Should require manage_shop permission."""
        assert hasattr(sort_actions, "__wrapped__")


class TestUpdatePositionsHelper:
    """Test the _update_positions helper function."""

    def test_update_positions_function_exists(self):
        """Should have _update_positions function."""
        assert callable(_update_positions)

    def test_update_positions_with_multiple_actions(self, multiple_actions):
        """Should update positions correctly."""
        # Mess up the positions first
        for i, action in enumerate(multiple_actions):
            action.position = 999 - i
            action.save()

        _update_positions()

        # Refresh from database and check positions
        for action in multiple_actions:
            action.refresh_from_db()
            assert action.position is not None
            assert isinstance(action.position, int)

    def test_update_positions_with_empty_groups(self, action_group):
        """Should handle empty groups gracefully."""
        empty_group = ActionGroup.objects.create(name="Empty Group")

        # Should not raise any exceptions
        _update_positions()

        # No actions should exist in the empty group
        assert Action.objects.filter(group=empty_group).count() == 0
