"""The topseller management, tested through real requests as a shop manager: the list of topsellers and of the
products that can be added (search, category, paging), adding, removing and sorting."""

import json

import pytest
from django.urls import reverse

from lfs.catalog.models import Category, Product
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS, VARIANT
from lfs.marketing.models import Topseller

pytestmark = pytest.mark.django_db

PAGE = reverse("lfs_manage_topseller")


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def product(name: str, **kwargs) -> Product:
    return Product.objects.create(name=name, slug=name.lower().replace(" ", "-"), **kwargs)


def entries() -> list[tuple[str, int]]:
    """Return the topsellers as (product name, position)."""
    return list(Topseller.objects.order_by("position").values_list("product__name", "position"))


class TestList:
    def test_offers_the_products_that_are_not_yet_topsellers(self, manager):
        lamp, chair = product("Lamp"), product("Chair")
        Topseller.objects.create(product=lamp)

        context = manager.get(PAGE).context

        assert [e.product for e in context["topseller"]] == [lamp]
        assert list(context["page"]) == [chair]

    def test_search_finds_by_name_sku_and_a_variants_inherited_name_or_sku(self, manager):
        lamp = product("Lamp", sku="L-1", sub_type=PRODUCT_WITH_VARIANTS)
        red = product("Red", parent=lamp, sub_type=VARIANT, active_name=False, active_sku=False)
        by_sku = product("Something", sku="lamp-2")
        product("Chair")

        page = manager.get(PAGE, {"filter": "lamp"}).context["page"]
        by_parent_sku = manager.get(PAGE, {"filter": "L-1"}).context["page"]

        assert set(page) == {lamp, red, by_sku}
        assert set(by_parent_sku) == {lamp, red}

    def test_filters_by_a_category_with_its_subcategories_or_by_no_category(self, manager):
        lights = Category.objects.create(name="Lights", slug="lights")
        lamps = Category.objects.create(name="Lamps", slug="lamps", parent=lights)
        desk_lamp, chair = product("Desk lamp"), product("Chair")
        desk_lamp.categories.add(lamps)

        assert list(manager.get(PAGE, {"topseller_category_filter": lights.id}).context["page"]) == [desk_lamp]
        assert list(manager.get(PAGE, {"topseller_category_filter": "None"}).context["page"]) == [chair]

    def test_paging_keeps_the_filters_in_the_session(self, manager):
        for i in range(51):
            product(f"Lamp {i}")
        product("Chair")
        manager.get(PAGE, {"filter": "lamp"})

        page = manager.get(PAGE, {"page": 2}).context["page"]

        assert len(page) == 1 and page[0].name.startswith("Lamp")

    def test_a_page_beyond_the_last_shows_no_products(self, manager):
        product("Lamp")

        assert manager.get(PAGE, {"page": 5}).context["page"] == 0


class TestChanges:
    def test_adds_the_checked_products_and_renumbers(self, manager):
        lamp, chair, table = product("Lamp"), product("Chair"), product("Table")
        Topseller.objects.create(product=lamp, position=10)

        response = manager.post(
            reverse("lfs_manage_add_topseller"), {f"product-{chair.id}": "on", f"product-{table.id}": "on"}
        )

        assert {name for name, _ in entries()} == {"Lamp", "Chair", "Table"}
        assert [position for _, position in entries()] == [10, 20, 30]
        assert response["Location"] == PAGE

    def test_removes_the_checked_topsellers_and_renumbers_the_rest(self, manager):
        lamp, chair, table = (
            Topseller.objects.create(product=product(n), position=p) for p, n in enumerate(("Lamp", "Chair", "Table"))
        )

        response = manager.post(
            reverse("lfs_manage_delete_topseller"), {"action": "remove", f"product-{chair.id}": "on"}
        )

        assert entries() == [("Lamp", 10), ("Table", 20)]
        assert Product.objects.count() == 3
        assert response["Location"] == PAGE

    def test_removes_nothing_without_the_remove_action(self, manager):
        lamp = Topseller.objects.create(product=product("Lamp"))

        manager.post(reverse("lfs_manage_delete_topseller"), {f"product-{lamp.id}": "on"})

        assert Topseller.objects.count() == 1

    def test_other_fields_and_unknown_ids_are_ignored(self, manager):
        lamp = Topseller.objects.create(product=product("Lamp"), position=10)
        chair = product("Chair")

        manager.post(reverse("lfs_manage_add_topseller"), {"csrfmiddlewaretoken": "x", f"product-{chair.id}": "on"})
        manager.post(
            reverse("lfs_manage_delete_topseller"),
            {"action": "remove", "product-999999": "on", "product-abc": "on", "filter": "x"},
        )
        manager.post(
            reverse("lfs_manage_sort_topseller"),
            json.dumps({"topseller_ids": [999999, lamp.id]}),
            content_type="application/json",
        )

        assert set(dict(entries())) == {"Lamp", "Chair"}
        assert dict(entries())["Lamp"] == 20  # second in the sorted list, after the unknown id

    def test_sorting_stores_the_new_order(self, manager):
        lamp, chair = (Topseller.objects.create(product=product(n), position=p) for p, n in ((1, "Lamp"), (2, "Chair")))

        manager.post(
            reverse("lfs_manage_sort_topseller"),
            json.dumps({"topseller_ids": [chair.id, lamp.id]}),
            content_type="application/json",
        )

        assert entries() == [("Chair", 10), ("Lamp", 20)]


def test_the_shop_shows_added_and_removed_topsellers_at_once(manager):
    """The shop caches its topsellers; changes in the management must reach it without waiting for the cache."""
    from lfs.marketing.utils import get_topseller

    lamp, chair = product("Lamp", active=True), product("Chair", active=True)
    Topseller.objects.create(product=lamp)
    assert get_topseller() == [lamp]

    manager.post(reverse("lfs_manage_add_topseller"), {f"product-{chair.id}": "on"})
    assert set(get_topseller()) == {lamp, chair}

    manager.post(
        reverse("lfs_manage_delete_topseller"),
        {"action": "remove", f"product-{Topseller.objects.get(product=lamp).id}": "on"},
    )
    assert get_topseller() == [chair]
