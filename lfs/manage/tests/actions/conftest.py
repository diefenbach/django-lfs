import pytest

from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.core.models import Action, ActionGroup, Shop

User = get_user_model()


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def admin_user(db):
    """Admin user with proper permissions."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def regular_user(db):
    """Regular user without admin permissions."""
    return User.objects.create_user(username="user", email="user@example.com", password="testpass123")


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


@pytest.fixture
def mock_session():
    """Mock session for testing."""
    return {}


@pytest.fixture
def mock_request(admin_user, request_factory):
    """Mock request with admin user."""
    request = request_factory.get("/")
    request.user = admin_user
    request.session = {}
    return request


@pytest.fixture
def shop(db):
    """Shop instance for testing."""
    return Shop.objects.create(name="Test Shop", shop_owner="Test Owner", from_email="test@example.com")


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db, shop):
    """Enable database access for all tests."""
    pass
