"""The property group management, tested through real requests as a shop manager: the list and its search, adding,
saving and deleting a group, assigning and removing products (removing drops their values of the group) and
properties."""

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from lfs.catalog.models import (
    Category,
    GroupsPropertiesRelation,
    Product,
    ProductPropertyValue,
    Property,
    PropertyGroup,
)
from lfs.catalog.settings import PROPERTY_SELECT_FIELD, PROPERTY_TEXT_FIELD, PROPERTY_VALUE_TYPE_DEFAULT

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def group():
    return PropertyGroup.objects.create(name="Lamps")


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def product(name: str, **kwargs) -> Product:
    return Product.objects.create(name=name, slug=name.lower().replace(" ", "-"), **kwargs)


class TestStartAndList:
    def test_shows_the_first_group_by_name(self, manager):
        PropertyGroup.objects.create(name="Tables")
        lamps = PropertyGroup.objects.create(name="Lamps")

        assert manager.get(reverse("lfs_manage_property_groups"))["Location"] == reverse(
            "lfs_manage_property_group", kwargs={"id": lamps.id}
        )

    def test_without_groups_shows_the_empty_page(self, manager):
        assert manager.get(reverse("lfs_manage_property_groups"))["Location"] == reverse(
            "lfs_manage_no_property_groups"
        )

    def test_search_filters_the_list_and_the_tabs_keep_it(self, manager, group):
        PropertyGroup.objects.create(name="Tables")

        response = manager.get(reverse("lfs_manage_property_group", kwargs={"id": group.id}), {"q": "lam"})

        assert list(response.context["property_groups"]) == [group]
        assert all(url.endswith("?q=lam") for _, url in response.context["tabs"])


class TestAddSaveDelete:
    def test_adds_a_group(self, manager):
        response = manager.post(reverse("lfs_manage_add_property_group"), {"name": " Lamps "})

        lamps = PropertyGroup.objects.get()
        assert lamps.name == "Lamps"
        assert response["Location"] == reverse("lfs_manage_property_group", kwargs={"id": lamps.id})
        assert messages_of(response) == ["Property group has been created."]

    def test_a_group_needs_a_name(self, manager):
        manager.post(reverse("lfs_manage_add_property_group"), {"name": "  "})

        assert not PropertyGroup.objects.exists()

    def test_saves_the_name(self, manager, group):
        url = reverse("lfs_manage_property_group", kwargs={"id": group.id})

        response = manager.post(url, {"name": "Lights"})

        assert PropertyGroup.objects.get(pk=group.pk).name == "Lights"
        assert response["Location"] == url
        assert messages_of(response) == ["Property group has been saved."]

    def test_confirmation_names_the_group(self, manager, group):
        response = manager.get(reverse("lfs_delete_property_group_confirm", kwargs={"id": group.id}))

        assert response.context["property_group"] == group

    def test_deletes_the_group_but_not_its_products_and_properties(self, manager, group):
        group.products.add(product("Lamp"))
        GroupsPropertiesRelation.objects.create(group=group, property=Property.objects.create(name="Colour"))

        response = manager.post(reverse("lfs_delete_property_group", kwargs={"id": group.id}))

        assert not PropertyGroup.objects.exists()
        assert not GroupsPropertiesRelation.objects.exists()
        assert (Product.objects.count(), Property.objects.count()) == (1, 1)
        assert response["Location"] == reverse("lfs_manage_property_groups")


class TestProducts:
    def url(self, group) -> str:
        return reverse("lfs_manage_property_group_products", kwargs={"id": group.id})

    def test_assigns_the_checked_products(self, manager, group):
        lamp, table = product("Lamp"), product("Table")
        product("Chair")

        response = manager.post(
            self.url(group), {"assign_products": "1", f"product-{lamp.id}": "on", f"product-{table.id}": "on"}
        )

        assert set(group.products.all()) == {lamp, table}
        assert response["Location"] == self.url(group)
        assert messages_of(response) == ["Products have been assigned."]

    def test_removing_a_product_drops_its_values_of_this_group_only(self, manager, group):
        lamp = product("Lamp")
        other_group = PropertyGroup.objects.create(name="Lights")
        group.products.add(lamp)
        other_group.products.add(lamp)
        colour = Property.objects.create(name="Colour")
        for g in (group, other_group):
            ProductPropertyValue.objects.create(
                product=lamp, property=colour, property_group=g, value="red", type=PROPERTY_VALUE_TYPE_DEFAULT
            )

        response = manager.post(self.url(group), {"remove_products": "1", f"product-{lamp.id}": "on"})

        assert not group.products.exists()
        assert list(ProductPropertyValue.objects.values_list("property_group", flat=True)) == [other_group.id]
        assert messages_of(response) == ["Products have been removed."]

    def test_lists_unassigned_products_filtered_by_name_and_category_with_its_subcategories(self, manager, group):
        lights = Category.objects.create(name="Lights", slug="lights")
        lamps = Category.objects.create(name="Lamps", slug="lamps", parent=lights)
        desk_lamp, floor_lamp, lamp_shade = product("Desk lamp"), product("Floor lamp"), product("Lamp shade")
        desk_lamp.categories.add(lamps)
        floor_lamp.categories.add(lamps)
        group.products.add(floor_lamp)

        page = manager.get(self.url(group), {"filter": "lamp", "products_category_filter": lights.id}).context["page"]
        uncategorized = manager.get(self.url(group), {"products_category_filter": "None"}).context["page"]

        assert list(page) == [desk_lamp]
        assert list(uncategorized) == [lamp_shade]


class TestProperties:
    def url(self, group) -> str:
        return reverse("lfs_manage_property_group_properties", kwargs={"id": group.id})

    def test_assigns_the_checked_properties_and_numbers_them(self, manager, group):
        colour, size = Property.objects.create(name="Colour"), Property.objects.create(name="Size")
        Property.objects.create(name="Weight")

        response = manager.post(
            self.url(group), {"assign_properties": "1", f"property-{colour.id}": "on", f"property-{size.id}": "on"}
        )

        assert set(group.groupproperties.values_list("property__name", flat=True)) == {"Colour", "Size"}
        assert sorted(group.groupproperties.values_list("position", flat=True)) == [10, 20]
        assert response["Location"] == self.url(group)
        assert messages_of(response) == ["Properties have been assigned."]

    def test_removes_the_checked_properties_and_renumbers_the_rest(self, manager, group):
        colour, size, weight = (Property.objects.create(name=n) for n in ("Colour", "Size", "Weight"))
        for position, p in enumerate((colour, size, weight)):
            GroupsPropertiesRelation.objects.create(group=group, property=p, position=position)

        response = manager.post(self.url(group), {"remove_properties": "1", f"property-{colour.id}": "on"})

        assert list(group.groupproperties.values_list("property__name", "position")) == [("Size", 10), ("Weight", 20)]
        assert messages_of(response) == ["Properties have been removed."]

    def test_offers_global_properties_not_yet_in_the_group_filtered_by_name_and_type(self, manager, group):
        colour = Property.objects.create(name="Colour", type=PROPERTY_SELECT_FIELD)
        Property.objects.create(name="Colour code", type=PROPERTY_TEXT_FIELD)
        Property.objects.create(name="Colour local", type=PROPERTY_SELECT_FIELD, local=True)
        assigned = Property.objects.create(name="Colour assigned", type=PROPERTY_SELECT_FIELD)
        GroupsPropertiesRelation.objects.create(group=group, property=assigned)

        response = manager.get(self.url(group), {"filter": "colour", "properties_type_filter": PROPERTY_SELECT_FIELD})

        assert list(response.context["page"]) == [colour]
