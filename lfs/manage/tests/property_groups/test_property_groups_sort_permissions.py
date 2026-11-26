"""The property group sort endpoints change data only for users with the manage_shop permission."""

import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.catalog.models import GroupsPropertiesRelation, Property, PropertyGroup

User = get_user_model()


@pytest.fixture
def groups():
    first = PropertyGroup.objects.create(name="First", position=10)
    second = PropertyGroup.objects.create(name="Second", position=20)
    return first, second


@pytest.fixture
def relations(groups):
    group = groups[0]
    first = GroupsPropertiesRelation.objects.create(
        group=group, property=Property.objects.create(name="Color"), position=10
    )
    second = GroupsPropertiesRelation.objects.create(
        group=group, property=Property.objects.create(name="Size"), position=20
    )
    return first, second


def _sort_groups(client, groups):
    first, second = groups
    return client.post(
        reverse("lfs_manage_sort_property_groups"),
        {"serialized": f"group={second.pk}&group={first.pk}"},
    )


def _sort_properties(client, relations):
    first, second = relations
    return client.post(
        reverse("lfs_manage_sort_property_group_properties", args=[first.group_id]),
        data=json.dumps({"property_ids": [second.property_id, first.property_id]}),
        content_type="application/json",
    )


def _positions(objects):
    return [type(obj).objects.get(pk=obj.pk).position for obj in objects]


@pytest.fixture
def regular_client(client):
    client.force_login(User.objects.create_user(username="user", email="user@example.com", password="x"))
    return client


@pytest.fixture
def admin_client(client):
    client.force_login(
        User.objects.create_user(username="admin", email="admin@example.com", password="x", is_superuser=True)
    )
    return client


@pytest.mark.django_db
def test_anonymous_user_cannot_sort_property_groups(client, groups):
    _sort_groups(client, groups)
    assert _positions(groups) == [10, 20]


@pytest.mark.django_db
def test_user_without_permission_cannot_sort_property_groups(regular_client, groups):
    _sort_groups(regular_client, groups)
    assert _positions(groups) == [10, 20]


@pytest.mark.django_db
def test_shop_manager_can_sort_property_groups(admin_client, groups):
    _sort_groups(admin_client, groups)
    assert _positions(groups) == [20, 10]


@pytest.mark.django_db
def test_anonymous_user_cannot_sort_properties_of_a_group(client, relations):
    _sort_properties(client, relations)
    assert _positions(relations) == [10, 20]


@pytest.mark.django_db
def test_user_without_permission_cannot_sort_properties_of_a_group(regular_client, relations):
    _sort_properties(regular_client, relations)
    assert _positions(relations) == [10, 20]


@pytest.mark.django_db
def test_shop_manager_can_sort_properties_of_a_group(admin_client, relations):
    _sort_properties(admin_client, relations)
    assert _positions(relations) == [20, 10]
