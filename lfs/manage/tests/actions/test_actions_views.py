"""The action management (links in the shop's tabs and footer), tested through real requests as a shop manager:
the start page, the groups with their actions and the search, adding, saving, sorting by drag and drop, and
deleting. Which links are accepted is tested in test_action_links.py."""

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from lfs.core.models import Action, ActionGroup

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def footer():
    return ActionGroup.objects.create(name="Footer")


@pytest.fixture
def tabs():
    return ActionGroup.objects.create(name="Tabs")


def action(group: ActionGroup, title: str, position: int = 999) -> Action:
    return Action.objects.create(group=group, title=title, link=f"/{title.lower()}", position=position, active=True)


def titles(group: ActionGroup) -> list[tuple[str, int]]:
    """Return the group's actions as (title, position) in their order."""
    return list(group.actions.values_list("title", "position"))


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


class TestStartAndList:
    def test_shows_the_first_action(self, manager, footer):
        imprint = action(footer, "Imprint", 10)
        action(footer, "Terms", 20)

        assert manager.get(reverse("lfs_manage_actions"))["Location"] == reverse(
            "lfs_manage_action", kwargs={"pk": imprint.id}
        )

    def test_without_actions_shows_the_empty_page(self, manager):
        assert manager.get(reverse("lfs_manage_actions"))["Location"] == reverse("lfs_manage_no_actions")

    def test_lists_each_groups_actions_and_the_search_filters_them(self, manager, footer, tabs):
        imprint, terms, shop_tab = action(footer, "Imprint", 10), action(footer, "Terms", 20), action(tabs, "Shop")
        url = reverse("lfs_manage_action", kwargs={"pk": imprint.id})

        groups = {g.name: list(g.filtered_actions) for g in manager.get(url).context["groups"]}
        found = {g.name: list(g.filtered_actions) for g in manager.get(url, {"q": "term"}).context["groups"]}

        assert groups == {"Footer": [imprint, terms], "Tabs": [shop_tab]}
        assert found == {"Footer": [terms], "Tabs": []}


class TestChanges:
    def test_adds_an_action_at_the_end_of_its_group(self, manager, footer):
        action(footer, "Imprint", 10)

        response = manager.post(
            reverse("lfs_manage_add_action"),
            {"create-title": "Terms", "create-link": "/terms", "create-group": footer.id, "create-active": "on"},
        )

        terms = Action.objects.get(title="Terms")
        assert titles(footer) == [("Imprint", 10), ("Terms", 20)]
        assert response["Location"] == reverse("lfs_manage_action", kwargs={"pk": terms.id})
        assert messages_of(response) == ["Action has been added."]

    def test_an_action_needs_a_title_and_a_group(self, manager, footer):
        response = manager.post(reverse("lfs_manage_add_action"), {"create-link": "/terms"})

        assert set(response.context["form"].errors) == {"title", "group"}
        assert not Action.objects.exists()

    def test_saves_an_action_and_keeps_the_search(self, manager, footer):
        imprint = action(footer, "Imprint")

        response = manager.post(
            reverse("lfs_manage_action", kwargs={"pk": imprint.id}),
            {"title": "Legal", "link": "/legal", "q": "leg"},
        )

        imprint.refresh_from_db()
        assert (imprint.title, imprint.link, imprint.active) == ("Legal", "/legal", False)
        assert response["Location"] == reverse("lfs_manage_action", kwargs={"pk": imprint.id}) + "?q=leg"
        assert messages_of(response) == ["Action has been saved."]

    def test_sorting_moves_an_action_within_its_group(self, manager, footer):
        action(footer, "A", 10)
        action(footer, "B", 20)
        c = action(footer, "C", 30)

        manager.post(reverse("lfs_manage_sort_actions"), {"item_id": c.id, "to_list": footer.id, "new_index": 0})

        assert titles(footer) == [("C", 10), ("A", 20), ("B", 30)]

    def test_sorting_moves_an_action_to_another_group(self, manager, footer, tabs):
        imprint = action(footer, "Imprint", 10)
        action(footer, "Terms", 20)
        action(tabs, "Shop", 10)

        manager.post(reverse("lfs_manage_sort_actions"), {"item_id": imprint.id, "to_list": tabs.id, "new_index": 5})

        assert titles(footer) == [("Terms", 10)]
        assert titles(tabs) == [("Shop", 10), ("Imprint", 20)]

    def test_confirmation_names_the_action(self, manager, footer):
        imprint = action(footer, "Imprint")

        assert (
            manager.get(reverse("lfs_manage_delete_action_confirm", kwargs={"pk": imprint.id})).context["action"]
            == imprint
        )

    def test_deleting_shows_the_next_action(self, manager, footer):
        imprint, terms = action(footer, "Imprint", 10), action(footer, "Terms", 20)

        response = manager.post(reverse("lfs_manage_delete_action", kwargs={"pk": imprint.id}))

        assert list(Action.objects.all()) == [terms]
        assert response["Location"] == reverse("lfs_manage_action", kwargs={"pk": terms.id})
        assert messages_of(response) == ["Action has been deleted."]

    def test_deleting_the_last_action_shows_the_empty_page(self, manager, footer):
        imprint = action(footer, "Imprint")

        response = manager.post(reverse("lfs_manage_delete_action", kwargs={"pk": imprint.id}))

        assert response["Location"] == reverse("lfs_manage_no_actions")
