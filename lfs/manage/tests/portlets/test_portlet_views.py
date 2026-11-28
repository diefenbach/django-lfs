"""The portlet management, tested through real requests as a shop manager: the portlets of a page, blocking the
parent's slots, adding, editing, deleting and sorting portlets. The same views serve the portlets of the shop,
categories and manufacturers."""

import pytest
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from django.urls import reverse
from portlets.models import PortletAssignment, PortletBlocking, PortletRegistration, Slot
from portlets.utils import register_portlet

from lfs.catalog.models import Category
from lfs.page.models import Page
from lfs.core.utils import get_default_shop
from lfs.manufacturer.models import Manufacturer
from lfs.portlet.models import LatestPortlet, TextPortlet

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def text_portlets():
    """Text portlets are registered and there are a left and a right slot."""
    register_portlet(TextPortlet, "Text")
    register_portlet(LatestPortlet, "Latest")
    Slot.objects.get_or_create(name="Left")
    Slot.objects.get_or_create(name="Right")


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def page():
    Page.objects.get_or_create(pk=1, defaults={"title": "Root", "slug": "root"})
    return Page.objects.create(title="Imprint", slug="imprint")


def slot(name: str) -> Slot:
    return Slot.objects.get(name=name)


def assign(obj, title: str, slot_name: str = "Left", position: int = 10) -> PortletAssignment:
    """Put a text portlet with the given title into the slot of ``obj``."""
    return PortletAssignment.objects.create(
        slot=slot(slot_name), content=obj, portlet=TextPortlet.objects.create(title=title), position=position
    )


def titles(obj, slot_name: str = "Left") -> list[tuple[str, int]]:
    """Return the titles and positions of the portlets in the slot of ``obj``."""
    ct = ContentType.objects.get_for_model(obj)
    return [
        (pa.portlet.title, pa.position)
        for pa in PortletAssignment.objects.filter(content_type=ct, content_id=obj.id, slot=slot(slot_name)).order_by(
            "position"
        )
    ]


def object_kwargs(obj) -> dict:
    return {"object_type_id": ContentType.objects.get_for_model(obj).id, "object_id": obj.id}


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def test_the_portlets_tab_shows_the_slots_with_their_portlets(manager, page):
    assign(page, "Opening hours")

    content = manager.get(reverse("lfs_manage_page_portlets", kwargs={"id": page.id})).context["portlets"]

    assert "Opening hours" in content and "Left" in content and "Right" in content


class TestBlocking:
    def test_blocks_the_checked_slots_and_unblocks_the_others(self, manager, page):
        url = reverse("lfs_update_portlets", kwargs=object_kwargs(page))
        manager.post(url, {"block_slot": [slot("Left").id, slot("Right").id]})

        response = manager.post(url, {"block_slot": [slot("Right").id]})

        assert list(PortletBlocking.objects.values_list("slot__name", flat=True)) == ["Right"]
        assert response["Location"] == reverse("lfs_manage_page_portlets", kwargs={"id": page.id})
        assert messages_of(response)[-1] == "Portlet has been updated."

    def test_an_ajax_request_gets_the_new_portlets_html(self, manager, page):
        response = manager.post(
            reverse("lfs_update_portlets", kwargs=object_kwargs(page)), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        assert response.json()["html"][0][0] == "#portlets"


class TestAdd:
    def test_shows_the_form_of_the_chosen_type(self, manager, page):
        response = manager.get(reverse("lfs_add_portlet", kwargs=object_kwargs(page)), {"portlet_type": "textportlet"})

        assert response.context["portlet_type_name"] == "Text"
        assert "portlet-title" in response.content.decode()

    def test_adds_the_portlet_to_the_slot_at_the_end(self, manager, page):
        assign(page, "First", position=10)

        response = manager.post(
            reverse("lfs_add_portlet", kwargs=object_kwargs(page)),
            {"portlet_type": "textportlet", "slot": slot("Left").id, "portlet-title": "Second", "portlet-text": "Hi"},
        )

        assert titles(page) == [("First", 10), ("Second", 20)]
        assert response["Location"] == reverse("lfs_manage_page_portlets", kwargs={"id": page.id})
        assert messages_of(response) == ["Portlet has been added."]

    @pytest.mark.parametrize("owner", ["category", "manufacturer", "shop"])
    def test_returns_to_the_owners_own_portlets_tab(self, manager, owner: str):
        if owner == "category":
            obj = Category.objects.create(name="Lights", slug="lights")
            tab = reverse("lfs_manage_category_portlets", kwargs={"id": obj.id})
        elif owner == "manufacturer":
            obj = Manufacturer.objects.create(name="Acme", slug="acme")
            tab = reverse("lfs_manage_manufacturer_portlets", kwargs={"id": obj.id})
        else:
            obj, tab = get_default_shop(), reverse("lfs_manage_shop_portlets")

        response = manager.post(
            reverse("lfs_add_portlet", kwargs=object_kwargs(obj)),
            {"portlet_type": "textportlet", "slot": slot("Right").id, "portlet-title": "Tip"},
        )

        assert titles(obj, "Right") == [("Tip", 10)]
        assert response["Location"] == tab

    def test_an_invalid_portlet_form_is_shown_again(self, manager, page):
        response = manager.post(
            reverse("lfs_add_portlet", kwargs=object_kwargs(page)),
            {"portlet_type": "latestportlet", "slot": slot("Left").id, "portlet-limit": "many"},
        )

        assert response.context["form"].errors["limit"]
        assert response.context["portlet_type_name"] == PortletRegistration.objects.get(type="latestportlet").name
        assert not PortletAssignment.objects.exists()

    @pytest.mark.parametrize("portlet_type", ["user", "page", "nosuchportlet"])
    def test_only_registered_portlet_types_are_offered(self, manager, page, portlet_type: str):
        """The type comes from the request; other models must not be used as portlets."""
        url = reverse("lfs_add_portlet", kwargs=object_kwargs(page))

        shown = manager.get(url, {"portlet_type": portlet_type})
        posted = manager.post(url, {"portlet_type": portlet_type, "slot": slot("Left").id, "portlet-title": "X"})

        assert "Invalid portlet type." in shown.content.decode()
        assert "Invalid portlet type." in posted.content.decode()
        assert not PortletAssignment.objects.exists()

    def test_a_deactivated_portlet_type_is_not_offered(self, manager, page):
        PortletRegistration.objects.filter(type="textportlet").update(active=False)

        response = manager.get(reverse("lfs_add_portlet", kwargs=object_kwargs(page)), {"portlet_type": "textportlet"})

        assert "Invalid portlet type." in response.content.decode()

    def test_without_a_type_asks_for_one(self, manager, page):
        response = manager.get(reverse("lfs_add_portlet", kwargs=object_kwargs(page)))

        assert "Please select a portlet type." in response.content.decode()


class TestEditAndDelete:
    def test_edits_the_portlet_and_moves_it_to_another_slot(self, manager, page):
        pa = assign(page, "Opening hours")
        url = reverse("lfs_edit_portlet", kwargs={"portletassignment_id": pa.id})
        assert manager.get(url).context["form"].initial["title"] == "Opening hours"

        response = manager.post(url, {"slot": slot("Right").id, "portlet-title": "Hours", "portlet-text": "9-5"})

        pa.refresh_from_db()
        assert (pa.slot.name, pa.portlet.title, pa.portlet.text) == ("Right", "Hours", "9-5")
        assert response["Location"] == reverse("lfs_manage_page_portlets", kwargs={"id": page.id})
        assert messages_of(response) == ["Portlet has been saved."]

    def test_an_invalid_edit_is_shown_again(self, manager, page):
        pa = PortletAssignment.objects.create(
            slot=slot("Left"), content=page, portlet=LatestPortlet.objects.create(title="New", limit=5), position=10
        )

        response = manager.post(
            reverse("lfs_edit_portlet", kwargs={"portletassignment_id": pa.id}),
            {"slot": slot("Right").id, "portlet-title": "New", "portlet-limit": "many"},
        )

        assert response.context["form"].errors["limit"]
        assert PortletAssignment.objects.get(pk=pa.pk).slot == slot("Left")

    def test_editing_an_unknown_portlet_shows_an_error(self, manager):
        url = reverse("lfs_edit_portlet", kwargs={"portletassignment_id": 99999})

        assert "Portlet not found." in manager.get(url, HTTP_HX_REQUEST="true").content.decode()

    def test_deletes_the_portlet_and_renumbers_the_slot(self, manager, page):
        assign(page, "A", position=10)
        second = assign(page, "B", position=20)
        assign(page, "C", position=30)
        url = reverse("lfs_delete_portlet", kwargs={"portletassignment_id": second.id})
        assert manager.get(url, HTTP_HX_REQUEST="true").context["portlet_assignment"] == second

        response = manager.post(url)

        assert titles(page) == [("A", 10), ("C", 20)]
        assert response["Location"] == reverse("lfs_manage_page_portlets", kwargs={"id": page.id})
        assert messages_of(response) == ["Portlet has been deleted."]

    def test_deleting_an_unknown_portlet_shows_an_error(self, manager):
        response = manager.post(reverse("lfs_delete_portlet", kwargs={"portletassignment_id": 99999}))

        assert messages_of(response) == ["Portlet not found."]


class TestSort:
    def sort(self, manager, pa, to_slot: str, new_index: int) -> None:
        manager.post(
            reverse("lfs_sort_portlets"),
            {"portlet_id": pa.id, "to_slot": slot(to_slot).id, "new_index": new_index},
        )

    def test_moves_a_portlet_to_the_top_of_its_slot(self, manager, page):
        assign(page, "A", position=10)
        assign(page, "B", position=20)
        c = assign(page, "C", position=30)

        self.sort(manager, c, "Left", 1)

        assert titles(page) == [("C", 10), ("A", 20), ("B", 30)]

    def test_moves_a_portlet_into_the_middle_of_another_slot(self, manager, page):
        a = assign(page, "A", position=10)
        assign(page, "X", "Right", position=10)
        assign(page, "Y", "Right", position=20)

        self.sort(manager, a, "Right", 2)

        assert titles(page) == []
        assert titles(page, "Right") == [("X", 10), ("A", 20), ("Y", 30)]

    def test_moves_a_portlet_to_the_end(self, manager, page):
        a = assign(page, "A", position=10)
        assign(page, "B", position=20)

        self.sort(manager, a, "Left", 5)

        assert titles(page) == [("B", 10), ("A", 20)]
