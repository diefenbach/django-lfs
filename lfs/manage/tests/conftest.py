"""
Pytest configuration and fixtures for LFS manage package tests.
"""

import os
import django
from django.conf import settings

# Configure Django settings before importing other Django modules
if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings.testing")
    django.setup()

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from lfs.catalog.models import StaticBlock
from lfs.core.models import Action, ActionGroup
from lfs.catalog.models import File


User = get_user_model()


@pytest.fixture
def request_factory():
    """Django RequestFactory for creating test requests."""
    return RequestFactory()


@pytest.fixture
def manage_user(db):
    """User with manage_shop permission."""
    user = User.objects.create_user(username="testmanager", email="manager@test.com", password="testpass123")

    # Create superuser to bypass permission check for testing
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def regular_user(db):
    """Regular user without manage permissions."""
    return User.objects.create_user(username="testuser", email="user@test.com", password="testpass123")


@pytest.fixture
def static_block(db):
    """Sample StaticBlock for testing."""
    return StaticBlock.objects.create(name="Test Block", html="<p>Test content</p>", position=10)


@pytest.fixture
def multiple_static_blocks(db):
    """Multiple StaticBlocks for list testing."""
    blocks = []
    for i in range(3):
        block = StaticBlock.objects.create(
            name=f"Test Block {i+1}", html=f"<p>Test content {i+1}</p>", position=(i + 1) * 10
        )
        blocks.append(block)
    return blocks


@pytest.fixture
def authenticated_request(request_factory, manage_user):
    """Factory for creating authenticated requests."""

    def _make_request(method="GET", path="/", data=None, **kwargs):
        if method.upper() == "GET":
            request = request_factory.get(path, data or {}, **kwargs)
        elif method.upper() == "POST":
            request = request_factory.post(path, data or {}, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")

        request.user = manage_user
        return request

    return _make_request


@pytest.fixture
def action_group(db):
    """Sample ActionGroup for testing."""
    return ActionGroup.objects.create(name="Test Group")


@pytest.fixture
def action(db, action_group):
    """Sample Action for testing."""
    return Action.objects.create(
        title="Test Action", link="https://example.com", active=True, group=action_group, position=10
    )


@pytest.fixture
def multiple_actions(db, action_group):
    """Multiple Actions for list testing."""
    actions = []
    for i in range(3):
        action = Action.objects.create(
            title=f"Test Action {i+1}",
            link=f"https://example{i+1}.com",
            active=True,
            group=action_group,
            position=(i + 1) * 10,
        )
        actions.append(action)
    return actions


@pytest.fixture
def multiple_action_groups(db):
    """Multiple ActionGroups for testing."""
    groups = []
    for i in range(3):
        group = ActionGroup.objects.create(name=f"Test Group {i+1}")
        groups.append(group)
    return groups


@pytest.fixture
def action_with_mixed_groups(db, multiple_action_groups):
    """Actions distributed across multiple groups."""
    actions = []
    for i, group in enumerate(multiple_action_groups):
        for j in range(2):  # 2 actions per group
            action = Action.objects.create(
                title=f"Action {i+1}-{j+1}",
                link=f"https://example{i+1}-{j+1}.com",
                active=True,
                group=group,
                position=(j + 1) * 10,
            )
            actions.append(action)
    return actions


@pytest.fixture
def files_for_static_block(db, static_block):
    """Multiple Files attached to a StaticBlock for testing."""
    files = []
    for i in range(3):
        file_obj = File.objects.create(
            content=static_block,
            title=f"Test File {i+1}",
            position=(i + 1) * 10,
        )
        files.append(file_obj)
    return files


@pytest.fixture
def single_file(db, static_block):
    """Single File for testing."""
    return File.objects.create(
        content=static_block,
        title="Test File",
        position=10,
    )
