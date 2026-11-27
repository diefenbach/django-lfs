"""A category added in the management interface gets the level of its place in the tree: 1 at the top, one more
than its parent below it. The category tree (menus, category portlet) starts at level 1."""

import pytest
from django.urls import reverse

from lfs.catalog.models import Category
from lfs.core.utils import CategoryTree


def add(client, url: str, name: str) -> Category:
    """Add the category ``name`` through the management form at ``url`` and return it."""
    client.post(url, {"name": name, "slug": name.lower()})
    return Category.objects.get(slug=name.lower())


@pytest.mark.django_db
def test_top_level_category_gets_level_1_and_shows_in_the_category_tree(client, admin_user):
    client.force_login(admin_user)

    garden = add(client, reverse("lfs_manage_add_top_category"), "Garden")

    assert garden.level == 1
    tree = CategoryTree(currents=[], start_level=1, expand_level=1).get_category_tree()
    assert [node["category"] for node in tree] == [garden]


@pytest.mark.django_db
def test_child_category_gets_one_level_more_than_its_parent(client, admin_user):
    client.force_login(admin_user)
    garden = add(client, reverse("lfs_manage_add_top_category"), "Garden")

    tools = add(client, reverse("lfs_manage_add_category", kwargs={"parent_id": garden.id}), "Tools")

    assert tools.level == 2
