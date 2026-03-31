import pytest
from django.urls import reverse

from lfs.core.models import Action, ActionGroup
from lfs.manage.actions.views import (
    ManageActionsView,
    ActionUpdateView,
    ActionCreateView,
    ActionDeleteConfirmView,
    ActionDeleteView,
    SortActionsView,
    _update_positions,
)

# No direct need for get_user_model in these tests


class TestManageActionsView:
    """Test the ManageActionsView redirect view."""

    def test_redirects_to_first_action_when_actions_exist(self, mock_request, action, monkeypatch):
        """Should redirect to first action when actions exist."""

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_manage_action" and kwargs and kwargs.get("pk") == action.id:
                return f"/manage/action/{action.id}/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.actions.views.reverse", mock_reverse)

        view = ManageActionsView()
        view.request = mock_request
        url = view.get_redirect_url()

        assert f"/manage/action/{action.id}/" in url

    def test_redirects_to_no_actions_when_none_exist(self, mock_request, monkeypatch):
        """Should redirect to no actions view when no actions exist."""
        # Delete all actions
        Action.objects.all().delete()

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_manage_no_actions":
                return "/manage/no-actions/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.actions.views.reverse", mock_reverse)

        view = ManageActionsView()
        view.request = mock_request
        url = view.get_redirect_url()

        assert url == "/manage/no-actions/"


class TestActionUpdateView:
    """Test the ActionUpdateView class-based view."""

    def test_get_success_url_without_search_query(self, request_factory, manage_user, action):
        """Should return URL without query parameter when no search query."""
        # Arrange
        request = request_factory.post("/", {})
        request.user = manage_user
        view = ActionUpdateView()
        view.request = request
        view.object = action

        # Act
        url = view.get_success_url()

        # Assert
        assert f"/manage/action/{action.id}/" in url
        assert "?q=" not in url

    def test_get_success_url_with_search_query(self, request_factory, manage_user, action):
        """Should return URL with query parameter when search query provided."""
        # Arrange
        request = request_factory.post("/", {"q": "test search"})
        request.user = manage_user
        view = ActionUpdateView()
        view.request = request
        view.object = action

        # Act
        url = view.get_success_url()

        # Assert
        assert f"/manage/action/{action.id}/" in url
        assert "?q=test search" in url  # Django doesn't URL encode in reverse_lazy

    def test_get_action_groups_queryset_without_search(self, request_factory, manage_user, action_group, action):
        """Should return all groups with all actions when no search query."""
        # Arrange
        request = request_factory.get("/")
        request.user = manage_user
        view = ActionUpdateView()
        view.request = request

        # Act
        groups = view.get_action_groups_queryset()

        # Assert
        assert len(groups) == 1
        assert groups[0] == action_group
        assert hasattr(groups[0], "filtered_actions")
        assert action in groups[0].filtered_actions

    def test_get_action_groups_queryset_with_search(self, request_factory, manage_user, action_group, action):
        """Should return filtered actions when search query provided."""
        # Arrange
        request = request_factory.get("/?q=nonexistent")
        request.user = manage_user
        view = ActionUpdateView()
        view.request = request

        # Act
        groups = view.get_action_groups_queryset()

        # Assert
        assert len(groups) == 1
        assert groups[0] == action_group
        assert hasattr(groups[0], "filtered_actions")
        # Should be empty since action title doesn't contain "nonexistent"
        assert len(groups[0].filtered_actions) == 0

    def test_get_context_data_includes_groups_and_search(self, request_factory, manage_user, action_group, action):
        """Should include groups and search query in context."""
        # Arrange
        request = request_factory.get("/?q=test")
        request.user = manage_user
        view = ActionUpdateView()
        view.request = request
        view.object = action  # Set object for UpdateView

        # Act
        context = view.get_context_data()

        # Assert
        assert "groups" in context
        assert "search_query" in context
        assert context["search_query"] == "test"
        assert len(context["groups"]) == 1

    def test_form_valid_updates_positions_and_shows_message(self, request_factory, manage_user, action, monkeypatch):
        """Should update positions and show success message on form valid."""
        # Arrange
        request = request_factory.post("/", {"active": "on", "title": "Updated Action"})
        request.user = manage_user
        view = ActionUpdateView()
        view.request = request
        view.object = action

        # Mock the form
        mock_form = type("MockForm", (), {"save": lambda commit=True: action, "is_valid": lambda: True})()

        # Track if _update_positions was called
        update_positions_called = False

        def mock_update_positions():
            nonlocal update_positions_called
            update_positions_called = True

        monkeypatch.setattr("lfs.manage.actions.views._update_positions", mock_update_positions)

        # Mock messages.success to avoid middleware requirement
        messages_called = False

        def mock_messages_success(request, message):
            nonlocal messages_called
            messages_called = True
            assert "Action has been saved" in message

        monkeypatch.setattr("lfs.manage.actions.views.messages.success", mock_messages_success)

        # Act
        response = view.form_valid(mock_form)

        # Assert
        assert update_positions_called
        assert messages_called


class TestNoActionsView:
    """Test the NoActionsView template view."""


class TestActionCreateView:
    """Test the ActionCreateView class-based view."""

    def test_get_success_url_without_search_query(self, request_factory, manage_user, action):
        """Should return URL without query parameter when no search query."""
        # Arrange
        request = request_factory.post("/", {})
        request.user = manage_user
        view = ActionCreateView()
        view.request = request
        view.object = action

        # Act
        url = view.get_success_url()

        # Assert
        assert f"/manage/action/{action.id}/" in url
        assert "?q=" not in url

    def test_get_success_url_with_search_query(self, request_factory, manage_user, action):
        """Should return URL with query parameter when search query provided."""
        # Arrange
        request = request_factory.post("/", {"q": "test search"})
        request.user = manage_user
        view = ActionCreateView()
        view.request = request
        view.object = action

        # Act
        url = view.get_success_url()

        # Assert
        assert f"/manage/action/{action.id}/" in url
        assert "?q=test search" in url  # Django doesn't URL encode in reverse_lazy

    def test_get_form_kwargs_adds_prefix(self, request_factory, manage_user):
        """Should add 'create' prefix to form kwargs."""
        # Arrange
        request = request_factory.get("/")
        request.user = manage_user
        view = ActionCreateView()
        view.request = request

        # Act
        kwargs = view.get_form_kwargs()

        # Assert
        assert "prefix" in kwargs
        assert kwargs["prefix"] == "create"

    def test_get_context_data_includes_groups_and_came_from(self, request_factory, manage_user, action_group):
        """Should include groups and came_from in context."""
        # Arrange
        request = request_factory.post("/", {"came_from": "/custom/path/"})
        request.user = manage_user
        view = ActionCreateView()
        view.request = request
        view.object = None  # CreateView doesn't need object

        # Act
        context = view.get_context_data()

        # Assert
        assert "groups" in context
        assert "came_from" in context
        assert context["groups"].count() == 1
        assert context["came_from"] == "/custom/path/"

    def test_get_context_data_uses_default_came_from(self, request_factory, manage_user, action_group):
        """Should use default came_from when not provided in POST."""
        # Arrange
        request = request_factory.post("/", {})
        request.user = manage_user
        view = ActionCreateView()
        view.request = request
        view.object = None  # CreateView doesn't need object

        # Act
        context = view.get_context_data()

        # Assert
        assert "came_from" in context
        assert context["came_from"] == "/manage/actions/"

    def test_form_valid_updates_positions_and_shows_message(
        self, request_factory, manage_user, action_group, monkeypatch
    ):
        """Should update positions and show success message on form valid."""
        # Arrange
        request = request_factory.post("/", {"active": "on", "title": "New Action", "group": action_group.id})
        request.user = manage_user
        view = ActionCreateView()
        view.request = request

        # Create a new action for the object
        new_action = Action.objects.create(title="New Action", group=action_group)
        view.object = new_action

        # Track if _update_positions was called
        update_positions_called = False

        def mock_update_positions():
            nonlocal update_positions_called
            update_positions_called = True

        monkeypatch.setattr("lfs.manage.actions.views._update_positions", mock_update_positions)

        # Mock messages.success to avoid middleware requirement
        messages_called = False

        def mock_messages_success(request, message):
            nonlocal messages_called
            messages_called = True
            assert "Action has been added" in message

        monkeypatch.setattr("lfs.manage.actions.views.messages.success", mock_messages_success)

        # Mock the form
        mock_form = type("MockForm", (), {"save": lambda commit=True: new_action, "is_valid": lambda: True})()

        # Act
        response = view.form_valid(mock_form)

        # Assert
        assert update_positions_called
        assert messages_called


class TestActionDeleteView:
    """Test the ActionDeleteView class-based view."""

    def test_get_success_url_with_remaining_actions(self, request_factory, manage_user, action_group):
        """Should redirect to first remaining action when other actions exist."""
        # Arrange
        action1 = Action.objects.create(title="Action 1", group=action_group)
        action2 = Action.objects.create(title="Action 2", group=action_group)
        request = request_factory.delete("/")
        request.user = manage_user
        view = ActionDeleteView()
        view.request = request
        view.object = action1  # Deleting action1

        # Act
        url = view.get_success_url()

        # Assert
        assert f"/manage/action/{action2.id}/" in url

    def test_get_success_url_with_no_remaining_actions(self, request_factory, manage_user, action_group):
        """Should redirect to no actions view when no other actions exist."""
        # Arrange
        action = Action.objects.create(title="Only Action", group=action_group)
        request = request_factory.delete("/")
        request.user = manage_user
        view = ActionDeleteView()
        view.request = request
        view.object = action  # Deleting the only action

        # Act
        url = view.get_success_url()

        # Assert
        assert "/manage/actions/no" in url


class TestActionDeleteConfirmView:
    """Test the ActionDeleteConfirmView template view."""

    def test_get_context_data_includes_action(self, request_factory, manage_user, action):
        """Should include action in context."""
        # Arrange
        request = request_factory.get(f"/delete/{action.id}/")
        request.user = manage_user
        view = ActionDeleteConfirmView()
        view.request = request
        view.kwargs = {"pk": action.id}

        # Act
        context = view.get_context_data()

        # Assert
        assert "action" in context
        assert context["action"] == action


class TestSortActionsView:
    """Test the SortActionsView drag and drop functionality."""

    def test_sort_actions_moves_action_to_new_position(self, request_factory, manage_user, action_group):
        """Should move action to new position within same group."""
        # Arrange
        action1 = Action.objects.create(title="Action 1", group=action_group, position=10)
        action2 = Action.objects.create(title="Action 2", group=action_group, position=20)
        action3 = Action.objects.create(title="Action 3", group=action_group, position=30)

        request = request_factory.post(
            "/",
            {
                "item_id": str(action1.id),
                "to_list": str(action_group.id),
                "new_index": "1",  # Move to position 1 (between action2 and action3)
            },
        )
        request.user = manage_user

        # Act
        view = SortActionsView()
        view.request = request
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        action1.refresh_from_db()
        action2.refresh_from_db()
        action3.refresh_from_db()

        # Action1 should be between action2 and action3
        assert action2.position < action1.position < action3.position

    def test_sort_actions_moves_action_to_different_group(self, request_factory, manage_user, action_group):
        """Should move action to different group."""
        # Arrange
        group1 = ActionGroup.objects.create(name="Group 1")
        group2 = ActionGroup.objects.create(name="Group 2")
        action1 = Action.objects.create(title="Action 1", group=group1, position=10)
        action2 = Action.objects.create(title="Action 2", group=group2, position=20)

        request = request_factory.post(
            "/", {"item_id": str(action1.id), "to_list": str(group2.id), "new_index": "1"}  # Move to end of group2
        )
        request.user = manage_user

        # Act
        view = SortActionsView()
        view.request = request
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        action1.refresh_from_db()
        action2.refresh_from_db()
        assert action1.group == group2
        # After _update_positions(), positions are reset to 10, 20, 30...
        assert action1.position == 20  # Second position in group2
        assert action2.position == 10  # First position in group2

    def test_sort_actions_moves_action_to_end_of_group(self, request_factory, manage_user, action_group):
        """Should move action to end of group when new_index is beyond group size."""
        # Arrange
        action1 = Action.objects.create(title="Action 1", group=action_group, position=10)
        action2 = Action.objects.create(title="Action 2", group=action_group, position=20)

        request = request_factory.post(
            "/",
            {
                "item_id": str(action1.id),
                "to_list": str(action_group.id),
                "new_index": "5",  # Beyond group size, should go to end
            },
        )
        request.user = manage_user

        # Act
        view = SortActionsView()
        view.request = request
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        action1.refresh_from_db()
        action2.refresh_from_db()
        # After _update_positions(), action1 should be at the end (position 20)
        assert action1.position == 20  # Last position
        assert action2.position == 10  # First position

    def test_sort_actions_handles_empty_group(self, request_factory, manage_user, action_group):
        """Should handle moving action to empty group."""
        # Arrange
        empty_group = ActionGroup.objects.create(name="Empty Group")
        action = Action.objects.create(title="Action", group=action_group, position=10)

        request = request_factory.post(
            "/", {"item_id": str(action.id), "to_list": str(empty_group.id), "new_index": "0"}
        )
        request.user = manage_user

        # Act
        view = SortActionsView()
        view.request = request
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        action.refresh_from_db()
        assert action.group == empty_group
        assert action.position == 10  # Should get default position


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


class TestActionsPermissionsIntegration:
    """Integration-style tests for authentication and permissions on actions routes."""

    @pytest.mark.parametrize(
        "route, needs_pk",
        [
            ("lfs_manage_actions", False),
            ("lfs_manage_action", True),
            ("lfs_manage_add_action", False),
            ("lfs_manage_delete_action_confirm", True),
            ("lfs_manage_no_actions", False),
        ],
    )
    def test_requires_authentication_get_routes(self, client, action, route, needs_pk):
        # Unauthenticated requests should redirect to login or return 403 depending on setup
        kwargs = {"pk": action.id} if needs_pk else {}
        url = reverse(route, kwargs=kwargs)
        resp = client.get(url)
        assert resp.status_code in (302, 403)

    def test_requires_authentication_sort_get(self, client):
        # SortActionsView requires POST; GET should be 405 or auth redirect
        resp = client.get(reverse("lfs_manage_sort_actions"))
        assert resp.status_code in (302, 403, 405)

    @pytest.mark.parametrize(
        "route, needs_pk",
        [
            ("lfs_manage_actions", False),
            ("lfs_manage_action", True),
            ("lfs_manage_add_action", False),
            ("lfs_manage_delete_action_confirm", True),
            ("lfs_manage_no_actions", False),
        ],
    )
    def test_requires_manage_shop_permission_get_routes(self, client, regular_user, action, route, needs_pk):
        client.force_login(regular_user)
        kwargs = {"pk": action.id} if needs_pk else {}
        url = reverse(route, kwargs=kwargs)
        resp = client.get(url)
        assert resp.status_code == 403

    def test_requires_manage_shop_permission_sort_post(self, client, regular_user, action):
        client.force_login(regular_user)
        resp = client.post(
            reverse("lfs_manage_sort_actions"),
            {"item_id": str(action.id), "to_list": str(action.group.id), "new_index": "0"},
        )
        assert resp.status_code == 403

    def test_sort_actions_view_allows_post_for_admin(self, client, admin_user, action):
        client.force_login(admin_user)
        resp = client.post(
            reverse("lfs_manage_sort_actions"),
            {"item_id": str(action.id), "to_list": str(action.group.id), "new_index": "0"},
        )
        assert resp.status_code == 200


class TestActionsTemplatesIntegration:
    """Lightweight rendering checks for key templates via the client."""

    def test_no_actions_renders_template(self, client, admin_user):
        client.force_login(admin_user)
        resp = client.get(reverse("lfs_manage_no_actions"))
        assert resp.status_code == 200
        assert "manage/actions/no_actions.html" in [t.name for t in resp.templates]

    def test_delete_confirm_renders_template(self, client, admin_user, action):
        client.force_login(admin_user)
        resp = client.get(reverse("lfs_manage_delete_action_confirm", kwargs={"pk": action.id}))
        assert resp.status_code == 200
        assert action.title.encode("utf-8") in resp.content
