"""
Unit tests for Action and ActionGroup models.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Parametrization for variations
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from lfs.core.models import Action, ActionGroup


@pytest.mark.django_db
class TestActionGroup:
    """Tests for ActionGroup model behavior."""

    @pytest.mark.parametrize(
        "name,expected_str",
        [
            ("Main Menu", "Main Menu"),
            ("Footer Links", "Footer Links"),
            ("", ""),  # Blank names allowed
        ],
    )
    def test_str_representation(self, name, expected_str):
        """Should return the name as string representation."""
        action_group = ActionGroup.objects.create(name=name)
        assert str(action_group) == expected_str

    def test_name_field_constraints(self):
        """Should enforce name field constraints."""
        # Test max_length
        long_name = "x" * 101  # Exceeds 100 char limit
        action_group = ActionGroup(name=long_name)

        with pytest.raises(ValidationError):
            action_group.full_clean()

    def test_name_uniqueness_constraint(self, action_group):
        """Should enforce unique constraint on name field."""
        with pytest.raises(IntegrityError):
            ActionGroup.objects.create(name=action_group.name)

    def test_default_ordering_by_name(self):
        """Should order ActionGroups by name by default."""
        group_z = ActionGroup.objects.create(name="Z Group")
        group_a = ActionGroup.objects.create(name="A Group")
        group_m = ActionGroup.objects.create(name="M Group")

        groups = list(ActionGroup.objects.all())
        names = [group.name for group in groups]

        assert names == ["A Group", "M Group", "Z Group"]

    def test_blank_name_allowed(self):
        """Should allow blank names."""
        action_group = ActionGroup.objects.create(name="")
        assert action_group.name == ""
        assert str(action_group) == ""

    def test_get_actions_returns_only_active_actions(self, action_group):
        """Should return only active actions from the group."""
        # Create active and inactive actions
        active_action1 = Action.objects.create(
            title="Active 1", link="https://example.com", active=True, group=action_group
        )
        active_action2 = Action.objects.create(
            title="Active 2", link="https://example2.com", active=True, group=action_group
        )
        inactive_action = Action.objects.create(
            title="Inactive", link="https://example3.com", active=False, group=action_group
        )

        actions = action_group.get_actions()

        assert actions.count() == 2
        assert active_action1 in actions
        assert active_action2 in actions
        assert inactive_action not in actions

    def test_get_actions_respects_position_ordering(self, action_group):
        """Should return actions ordered by position."""
        action_30 = Action.objects.create(
            title="Position 30", link="https://example.com", active=True, group=action_group, position=30
        )
        action_10 = Action.objects.create(
            title="Position 10", link="https://example2.com", active=True, group=action_group, position=10
        )
        action_20 = Action.objects.create(
            title="Position 20", link="https://example3.com", active=True, group=action_group, position=20
        )

        actions = list(action_group.get_actions())

        assert actions == [action_10, action_20, action_30]

    def test_get_actions_returns_empty_when_no_active_actions(self, action_group):
        """Should return empty queryset when no active actions exist."""
        # Create only inactive actions
        Action.objects.create(title="Inactive", link="https://example.com", active=False, group=action_group)

        actions = action_group.get_actions()

        assert actions.count() == 0


@pytest.mark.django_db
class TestAction:
    """Tests for Action model behavior."""

    @pytest.mark.parametrize(
        "title,expected_str",
        [
            ("Home", "Home"),
            ("About Us", "About Us"),
            ("Contact", "Contact"),
        ],
    )
    def test_str_representation(self, title, expected_str, action_group):
        """Should return the title as string representation."""
        action = Action.objects.create(title=title, link="https://example.com", group=action_group)
        assert str(action) == expected_str

    @pytest.mark.parametrize(
        "field,value,should_raise",
        [
            ("title", "x" * 41, True),  # Exceeds 40 char limit
            ("title", "x" * 40, False),  # Within limit
            ("link", "x" * 101, True),  # Exceeds 100 char limit
            ("link", "https://example.com", False),  # Valid URL
        ],
    )
    def test_field_constraints(self, field, value, should_raise, action_group):
        """Should enforce field constraints."""
        kwargs = {"title": "Test Action", "link": "https://example.com", "group": action_group, field: value}
        action = Action(**kwargs)

        if should_raise:
            with pytest.raises(ValidationError):
                action.full_clean()
        else:
            action.full_clean()  # Should not raise

    def test_default_values(self, action_group):
        """Should set correct default values."""
        action = Action.objects.create(title="Test Action", link="https://example.com", group=action_group)

        assert action.active is False
        assert action.position == 999
        assert action.parent is None

    def test_default_ordering_by_position(self, action_group):
        """Should order Actions by position by default."""
        action_30 = Action.objects.create(
            title="Position 30", link="https://example.com", group=action_group, position=30
        )
        action_10 = Action.objects.create(
            title="Position 10", link="https://example2.com", group=action_group, position=10
        )
        action_20 = Action.objects.create(
            title="Position 20", link="https://example3.com", group=action_group, position=20
        )

        actions = list(Action.objects.all())

        assert actions == [action_10, action_20, action_30]

    def test_foreign_key_relationship_with_group(self, action_group):
        """Should properly relate to ActionGroup via foreign key."""
        action = Action.objects.create(title="Test Action", link="https://example.com", group=action_group)

        assert action.group == action_group
        assert action in action_group.actions.all()

    def test_cascade_delete_from_group(self, action_group):
        """Should be deleted when parent group is deleted."""
        action = Action.objects.create(title="Test Action", link="https://example.com", group=action_group)
        action_id = action.id

        action_group.delete()

        assert not Action.objects.filter(id=action_id).exists()

    def test_self_referential_parent_relationship(self, action_group):
        """Should support self-referential parent relationship."""
        parent_action = Action.objects.create(title="Parent", link="https://example.com", group=action_group)
        child_action = Action.objects.create(
            title="Child", link="https://example2.com", group=action_group, parent=parent_action
        )

        assert child_action.parent == parent_action

    def test_parent_set_null_on_delete(self, action_group):
        """Should set parent to NULL when parent action is deleted."""
        parent_action = Action.objects.create(title="Parent", link="https://example.com", group=action_group)
        child_action = Action.objects.create(
            title="Child", link="https://example2.com", group=action_group, parent=parent_action
        )

        parent_action.delete()
        child_action.refresh_from_db()

        assert child_action.parent is None

    @pytest.mark.parametrize(
        "url,is_valid",
        [
            ("https://example.com", True),
            ("http://example.com", True),
            ("ftp://example.com", True),
            ("invalid-url", False),
            ("", False),
        ],
    )
    def test_url_field_validation(self, url, is_valid, action_group):
        """Should validate URL field properly."""
        action = Action(title="Test", link=url, group=action_group)

        if is_valid:
            action.full_clean()  # Should not raise
        else:
            with pytest.raises(ValidationError):
                action.full_clean()


@pytest.mark.django_db
class TestActionGroupActionRelationship:
    """Tests for the relationship between ActionGroup and Action models."""

    def test_related_name_actions_works(self, action_group):
        """Should access actions via related_name 'actions'."""
        action1 = Action.objects.create(title="Action 1", link="https://example.com", group=action_group)
        action2 = Action.objects.create(title="Action 2", link="https://example2.com", group=action_group)

        group_actions = action_group.actions.all()

        assert action1 in group_actions
        assert action2 in group_actions
        assert group_actions.count() == 2

    def test_multiple_groups_can_have_actions(self, multiple_action_groups):
        """Should support multiple groups each having their own actions."""
        group1, group2, group3 = multiple_action_groups

        action1 = Action.objects.create(title="Group 1 Action", link="https://example.com", group=group1)
        action2 = Action.objects.create(title="Group 2 Action", link="https://example.com", group=group2)

        assert action1 in group1.actions.all()
        assert action1 not in group2.actions.all()
        assert action2 in group2.actions.all()
        assert action2 not in group1.actions.all()

    def test_action_group_queryset_optimization(self, action_group):
        """Should allow efficient querying of related actions."""
        # Create actions
        for i in range(5):
            Action.objects.create(title=f"Action {i}", link="https://example.com", group=action_group, active=True)

        # Test that we can efficiently get active actions
        active_actions = action_group.get_actions()

        assert active_actions.count() == 5
        # Should be able to iterate without additional queries (depends on usage)
        titles = [action.title for action in active_actions]
        assert len(titles) == 5
