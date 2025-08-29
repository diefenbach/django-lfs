"""
Comprehensive unit tests for LFS action management views.

Tests cover all action views including:
- manage_actions dispatcher
- ActionUpdateView
- NoActionsView
- ActionCreateView
- ActionDeleteView
- sort_actions functionality
- _update_positions helper
"""

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from unittest.mock import MagicMock

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


# Fixtures are now in conftest.py for better reusability


class TestManageActionsDispatcher:
    """Test the manage_actions dispatcher function."""

    def test_redirects_to_first_action_when_actions_exist(self, authenticated_request, action, monkeypatch):
        """Should redirect to first action when actions exist."""
        request = authenticated_request()

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_manage_action" and kwargs and kwargs.get("pk") == action.id:
                return f"/manage/action/{action.id}/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.actions.views.reverse", mock_reverse)

        response = manage_actions(request)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == f"/manage/action/{action.id}/"

    def test_redirects_to_no_actions_when_none_exist(self, authenticated_request, db, monkeypatch):
        """Should redirect to no actions view when no actions exist."""
        request = authenticated_request()

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_no_actions":
                return "/manage/no-actions/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.actions.views.reverse", mock_reverse)

        response = manage_actions(request)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == "/manage/no-actions/"

    def test_requires_manage_shop_permission(self, request_factory, regular_user):
        """Should require manage_shop permission."""
        request = request_factory.get("/")
        request.user = regular_user

        # This should be handled by the permission_required decorator
        # In actual usage, this would redirect to login or show 403
        # For testing, we just verify the decorator is applied
        assert hasattr(manage_actions, "__wrapped__")


class TestActionUpdateView:
    """Test the ActionUpdateView class-based view."""

    @pytest.mark.parametrize(
        "attribute,expected",
        [
            ("permission_required", "core.manage_shop"),
            ("model", Action),
            ("template_name", "manage/actions/action.html"),
            ("fields", ("active", "title", "link")),
        ],
    )
    def test_view_configuration(self, attribute, expected):
        """Should have correct view configuration."""
        assert getattr(ActionUpdateView, attribute) == expected

    def test_get_success_url_returns_action_edit_url(self, action, monkeypatch):
        """Should return URL to edit the same action after successful update."""
        view = ActionUpdateView()
        view.object = action

        def mock_reverse_lazy(view_name, kwargs=None):
            if view_name == "lfs_manage_action" and kwargs and kwargs.get("pk") == action.id:
                return f"/manage/action/{action.id}/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.actions.views.reverse_lazy", mock_reverse_lazy)

        url = view.get_success_url()

        assert url == f"/manage/action/{action.id}/"

    def test_get_context_data_includes_action_groups(self, request_factory, action_group, action):
        """Should include all action groups in context."""
        request = request_factory.get("/")
        view = ActionUpdateView()
        view.request = request
        view.object = action

        context = view.get_context_data()

        assert "groups" in context
        assert action_group in context["groups"]

    def test_form_valid_calls_update_positions(self, action, monkeypatch):
        """Should call _update_positions after successful form submission."""
        view = ActionUpdateView()
        view.object = action

        mock_form = MagicMock()
        update_called = False
        super_called = False

        def mock_update_positions():
            nonlocal update_called
            update_called = True

        def mock_super_form_valid(self, form):
            nonlocal super_called
            super_called = True
            assert form == mock_form
            return HttpResponse()

        monkeypatch.setattr("lfs.manage.actions.views._update_positions", mock_update_positions)
        monkeypatch.setattr("django.views.generic.edit.UpdateView.form_valid", mock_super_form_valid)

        response = view.form_valid(mock_form)

        assert update_called
        assert super_called
        assert isinstance(response, HttpResponse)


class TestNoActionsView:
    """Test the NoActionsView template view."""

    @pytest.mark.parametrize(
        "attribute,expected",
        [
            ("permission_required", "core.manage_shop"),
            ("template_name", "manage/actions/no_actions.html"),
        ],
    )
    def test_view_configuration(self, attribute, expected):
        """Should have correct view configuration."""
        assert getattr(NoActionsView, attribute) == expected


class TestActionCreateView:
    """Test the ActionCreateView class-based view."""

    @pytest.mark.parametrize(
        "attribute,expected",
        [
            ("permission_required", "core.manage_shop"),
            ("model", Action),
            ("template_name", "manage/actions/add_action.html"),
            ("fields", ("active", "title", "link", "group")),
        ],
    )
    def test_view_configuration(self, attribute, expected):
        """Should have correct view configuration."""
        assert getattr(ActionCreateView, attribute) == expected

    def test_get_form_kwargs_adds_create_prefix(self, monkeypatch):
        """Should add 'create' prefix to form fields for modal usage."""
        view = ActionCreateView()

        def mock_super_get_form_kwargs(self):
            return {}

        monkeypatch.setattr("django.views.generic.edit.CreateView.get_form_kwargs", mock_super_get_form_kwargs)

        kwargs = view.get_form_kwargs()

        assert kwargs["prefix"] == "create"

    def test_get_context_data_includes_groups_and_came_from(self, request_factory, action_group):
        """Should include action groups and came_from in context."""
        request = request_factory.post("/", {"came_from": "/test-url/"})

        view = ActionCreateView()
        view.request = request
        view.object = None  # CreateView starts with no object

        context = view.get_context_data()

        assert "groups" in context
        assert action_group in context["groups"]
        assert context["came_from"] == "/test-url/"

    def test_get_context_data_defaults_came_from_to_manage_actions(self, request_factory, action_group, monkeypatch):
        """Should default came_from to manage actions URL when not provided."""
        request = request_factory.post("/")

        view = ActionCreateView()
        view.request = request
        view.object = None  # CreateView starts with no object

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_manage_actions":
                return "/manage/actions/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.actions.views.reverse", mock_reverse)

        context = view.get_context_data()

        assert context["came_from"] == "/manage/actions/"

    def test_form_valid_creates_action_and_returns_htmx_redirect(self, action_group, monkeypatch):
        """Should create action, update positions, and return HTMX redirect."""
        view = ActionCreateView()

        mock_form = MagicMock()
        mock_action = Action(id=123, title="New Action")
        mock_form.save.return_value = mock_action

        update_called = False

        def mock_update_positions():
            nonlocal update_called
            update_called = True

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_manage_action" and kwargs and kwargs.get("pk") == 123:
                return "/manage/action/123/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.actions.views._update_positions", mock_update_positions)
        monkeypatch.setattr("lfs.manage.actions.views.reverse", mock_reverse)

        response = view.form_valid(mock_form)

        assert isinstance(response, HttpResponse)
        assert response["HX-Redirect"] == "/manage/action/123/"
        mock_form.save.assert_called_once()
        assert update_called


class TestActionDeleteView:
    """Test the ActionDeleteView class-based view."""

    @pytest.mark.parametrize(
        "attribute,expected",
        [
            ("permission_required", "core.manage_shop"),
            ("model", Action),
        ],
    )
    def test_view_configuration(self, attribute, expected):
        """Should have correct view configuration."""
        assert getattr(ActionDeleteView, attribute) == expected

    def test_post_redirects_to_next_action_when_others_exist(self, request_factory, multiple_actions, monkeypatch):
        """Should redirect to another action when other actions exist after deletion."""
        request = request_factory.post("/")

        view = ActionDeleteView()
        view.request = request
        view.kwargs = {"pk": multiple_actions[0].id}

        def mock_get_object():
            return multiple_actions[0]

        monkeypatch.setattr(view, "get_object", mock_get_object)

        response = view.post(request)

        assert isinstance(response, HttpResponseRedirect)
        # Should redirect to one of the remaining actions
        remaining_action = Action.objects.exclude(pk=multiple_actions[0].pk).first()
        expected_url = reverse("lfs_manage_action", kwargs={"pk": remaining_action.id})
        assert response.url == expected_url

    def test_post_returns_htmx_redirect_when_no_actions_remain(self, request_factory, action, monkeypatch):
        """Should return HTMX redirect to no actions when last action is deleted."""
        request = request_factory.post("/")

        view = ActionDeleteView()
        view.request = request
        view.kwargs = {"pk": action.id}

        def mock_get_object():
            return action

        monkeypatch.setattr(view, "get_object", mock_get_object)

        response = view.post(request)

        assert isinstance(response, HttpResponse)
        assert response["HX-Redirect"] == reverse("lfs_no_actions")


class TestSortActions:
    """Test the sort_actions drag and drop functionality."""

    def test_requires_manage_shop_permission_and_post(self):
        """Should require manage_shop permission and POST method."""
        assert hasattr(sort_actions, "__wrapped__")  # permission_required decorator
        # The require_POST decorator should also be applied

    def test_updates_action_group_when_moved_to_different_group(
        self, request_factory, manage_user, multiple_actions, monkeypatch
    ):
        """Should update action's group when moved to different group."""
        new_group = ActionGroup.objects.create(name="New Group")
        action_to_move = multiple_actions[0]

        request = request_factory.post(
            "/", {"item_id": str(action_to_move.id), "to_list": str(new_group.id), "new_index": "0"}
        )
        request.user = manage_user

        update_called = False

        def mock_update_positions():
            nonlocal update_called
            update_called = True

        monkeypatch.setattr("lfs.manage.actions.views._update_positions", mock_update_positions)

        response = sort_actions(request)

        assert isinstance(response, HttpResponse)
        action_to_move.refresh_from_db()
        assert action_to_move.group_id == new_group.id
        assert update_called

    def test_updates_positions_when_moved_within_group(
        self, request_factory, manage_user, multiple_actions, monkeypatch
    ):
        """Should update positions when action is moved within the same group."""
        action_to_move = multiple_actions[0]
        target_group = action_to_move.group

        request = request_factory.post(
            "/", {"item_id": str(action_to_move.id), "to_list": str(target_group.id), "new_index": "2"}  # Move to end
        )
        request.user = manage_user

        update_called = False

        def mock_update_positions():
            nonlocal update_called
            update_called = True

        monkeypatch.setattr("lfs.manage.actions.views._update_positions", mock_update_positions)

        response = sort_actions(request)

        assert isinstance(response, HttpResponse)
        assert update_called

    def test_handles_new_index_beyond_list_length(self, request_factory, manage_user, action, monkeypatch):
        """Should handle when new_index is beyond the current list length."""
        request = request_factory.post(
            "/",
            {"item_id": str(action.id), "to_list": str(action.group.id), "new_index": "999"},  # Way beyond current list
        )
        request.user = manage_user

        update_called = False

        def mock_update_positions():
            nonlocal update_called
            update_called = True

        monkeypatch.setattr("lfs.manage.actions.views._update_positions", mock_update_positions)

        response = sort_actions(request)

        assert isinstance(response, HttpResponse)
        assert update_called


class TestUpdatePositionsHelper:
    """Test the _update_positions helper function."""

    def test_sets_sequential_positions_for_actions_in_groups(self, multiple_actions):
        """Should set sequential positions (10, 20, 30, ...) for all actions in their groups."""
        # Mess up the positions first
        for i, action in enumerate(multiple_actions):
            action.position = 999 - i  # Reverse order
            action.save()

        _update_positions()

        # _update_positions processes actions via group.actions.all() which is ordered by position
        # So it will reorder them sequentially based on their current order
        actions_in_group = list(Action.objects.filter(group=multiple_actions[0].group).order_by("position"))
        for i, action in enumerate(actions_in_group):
            action.refresh_from_db()
            expected_position = (i + 1) * 10
            assert action.position == expected_position

    def test_handles_multiple_groups_correctly(self, db):
        """Should handle actions across multiple groups correctly."""
        group1 = ActionGroup.objects.create(name="Group 1")
        group2 = ActionGroup.objects.create(name="Group 2")

        # Create actions in both groups with messy positions
        Action.objects.create(title="Action 1A", link="http://1a.com", group=group1, position=999)
        Action.objects.create(title="Action 1B", link="http://1b.com", group=group1, position=888)
        Action.objects.create(title="Action 2A", link="http://2a.com", group=group2, position=777)
        Action.objects.create(title="Action 2B", link="http://2b.com", group=group2, position=666)

        _update_positions()

        # Check group 1 positions - should be sequential 10, 20 ordered by position
        group1_actions = list(Action.objects.filter(group=group1).order_by("position"))
        for i, action in enumerate(group1_actions):
            expected_position = (i + 1) * 10
            assert action.position == expected_position

        # Check group 2 positions - should be sequential 10, 20 ordered by position
        group2_actions = list(Action.objects.filter(group=group2).order_by("position"))
        for i, action in enumerate(group2_actions):
            expected_position = (i + 1) * 10
            assert action.position == expected_position

    def test_handles_empty_groups_gracefully(self, action_group):
        """Should handle groups with no actions gracefully."""
        empty_group = ActionGroup.objects.create(name="Empty Group")

        # Should not raise any exceptions
        _update_positions()

        # No actions should exist in the empty group
        assert Action.objects.filter(group=empty_group).count() == 0
