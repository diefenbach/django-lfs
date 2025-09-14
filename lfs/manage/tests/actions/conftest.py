"""
Pytest fixtures for Action and ActionGroup testing.

Provides comprehensive test data and utilities for action management tests.
"""

import pytest

from django.contrib.auth import get_user_model

from lfs.core.models import Action, ActionGroup

User = get_user_model()


# Common fixtures are now imported from the main conftest.py


@pytest.fixture
def action_group(db):
    """ActionGroup instance for testing."""
    return ActionGroup.objects.create(name="Test Group")


@pytest.fixture
def action(action_group):
    """Action instance for testing."""
    return Action.objects.create(title="Test Action", link="https://example.com", active=True, group=action_group)


@pytest.fixture
def inactive_action(action_group):
    """Inactive Action instance for testing."""
    return Action.objects.create(title="Inactive Action", link="https://example.com", active=False, group=action_group)


@pytest.fixture
def multiple_actions(action_group):
    """Multiple Action instances for testing."""
    actions = []
    for i in range(3):
        action = Action.objects.create(
            title=f"Action {i+1}",
            link=f"https://example{i+1}.com",
            active=True,
            group=action_group,
            position=(i + 1) * 10,
        )
        actions.append(action)
    return actions


@pytest.fixture
def multiple_action_groups(db):
    """Multiple ActionGroup instances for testing."""
    return [
        ActionGroup.objects.create(name="Group 1"),
        ActionGroup.objects.create(name="Group 2"),
        ActionGroup.objects.create(name="Group 3"),
    ]


@pytest.fixture
def actions_hierarchy(action_group):
    """Action hierarchy for testing parent-child relationships."""
    parent_action = Action.objects.create(
        title="Parent Action", link="https://parent.com", active=True, group=action_group
    )
    child_action = Action.objects.create(
        title="Child Action", link="https://child.com", active=True, group=action_group, parent=parent_action
    )
    grandchild_action = Action.objects.create(
        title="Grandchild Action", link="https://grandchild.com", active=True, group=action_group, parent=child_action
    )
    return parent_action, child_action, grandchild_action


# Common fixtures (mock_session, mock_request, shop, enable_db_access_for_all_tests)
# are now imported from the main conftest.py
