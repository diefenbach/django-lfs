"""The tabs tag marks the tab whose link belongs to the current page, and no other."""

import pytest
from django.test import RequestFactory

from lfs.catalog.models import Category
from lfs.core.models import Action, ActionGroup
from lfs.core.templatetags.lfs_tags import tabs


@pytest.fixture
def tab_group(db):
    return ActionGroup.objects.create(pk=1, name="Tabs")


def add_tab(group, title, link, position):
    return Action.objects.create(group=group, title=title, link=link, position=position, active=True)


def selected_titles(path, obj=None):
    context = {"request": RequestFactory().get(path)}
    return [tab.title for tab in tabs(context, obj)["tabs"] if getattr(tab, "selected", False)]


def test_home_tab_is_selected_only_on_the_home_page(tab_group):
    add_tab(tab_group, "Home", "/", 1)
    add_tab(tab_group, "Contact", "/contact", 2)

    assert selected_titles("/") == ["Home"]
    assert selected_titles("/contact") == ["Contact"]
    assert selected_titles("/page/imprint") == []


def test_tab_is_selected_on_its_subpages_but_not_on_similar_paths(tab_group):
    add_tab(tab_group, "Pages", "/page", 1)

    assert selected_titles("/page/imprint") == ["Pages"]
    assert selected_titles("/pages-archive") == []


def test_home_tab_is_not_selected_on_a_category(tab_group):
    garden = Category.objects.create(name="Garden", slug="garden")
    add_tab(tab_group, "Home", "/", 1)
    add_tab(tab_group, "Garden", garden.get_absolute_url(), 2)

    assert selected_titles(garden.get_absolute_url(), garden) == ["Garden"]
