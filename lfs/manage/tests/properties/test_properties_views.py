"""The property management, tested through real requests as a shop manager: the list and its search, adding and
saving a property (changing the type drops the stored values), the options of a select property, and deleting."""

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from lfs.catalog.models import Product, ProductPropertyValue, Property, PropertyOption
from lfs.catalog.settings import (
    PROPERTY_NUMBER_FIELD,
    PROPERTY_SELECT_FIELD,
    PROPERTY_TEXT_FIELD,
    PROPERTY_VALUE_TYPE_DEFAULT,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def form_data(response) -> dict:
    """Return the data of the page's form as the browser would send it."""
    form = response.context["form"]
    return {
        name: form[name].value()
        for name in form.fields
        if form[name].value() is not None and form[name].value() is not False
    }


def stored_value(property: Property) -> ProductPropertyValue:
    """Store a value of the property for a product."""
    product = Product.objects.get_or_create(slug="lamp", defaults={"name": "Lamp"})[0]
    return ProductPropertyValue.objects.create(
        product=product, property=property, value="red", type=PROPERTY_VALUE_TYPE_DEFAULT
    )


class TestStartAndList:
    def test_shows_the_first_global_property(self, manager):
        Property.objects.create(name="Local", local=True)
        first = Property.objects.create(name="Colour")

        assert manager.get(reverse("lfs_manage_properties"))["Location"] == reverse(
            "lfs_manage_property", kwargs={"id": first.id}
        )

    def test_without_global_properties_offers_to_add_one(self, manager):
        Property.objects.create(name="Local", local=True)

        assert manager.get(reverse("lfs_manage_properties"))["Location"] == reverse("lfs_add_property")

    def test_search_finds_by_name_or_title_and_leaves_out_local_properties(self, manager):
        colour = Property.objects.create(name="Colour", title="Farbe")
        Property.objects.create(name="Size", title="Größe")
        Property.objects.create(name="Farbe lokal", local=True)

        response = manager.get(reverse("lfs_manage_property", kwargs={"id": colour.id}), {"q": "farb"})

        assert list(response.context["properties"]) == [colour]


class TestAdd:
    def test_creates_the_property_with_its_name_as_title_and_renumbers(self, manager):
        Property.objects.create(name="Colour", position=5)

        response = manager.post(reverse("lfs_add_property"), {"name": "Size"})

        size = Property.objects.get(name="Size")
        assert size.title == "Size"
        assert list(Property.objects.values_list("name", "position")) == [("Colour", 10), ("Size", 20)]
        assert response["Location"] == reverse("lfs_manage_property", kwargs={"id": size.id})
        assert messages_of(response) == ["Property has been created."]

    def test_requires_a_name(self, manager):
        manager.post(reverse("lfs_add_property"), {"name": ""})

        assert not Property.objects.exists()


class TestSave:
    def test_a_property_needs_a_title(self, manager):
        colour = Property.objects.create(name="Colour", title="Colour")
        url = reverse("lfs_manage_property", kwargs={"id": colour.id})

        response = manager.post(url, form_data(manager.get(url)) | {"title": ""})

        assert response.context["form"].errors["title"]
        assert Property.objects.get(pk=colour.pk).title == "Colour"

    def test_saves_the_data(self, manager):
        colour = Property.objects.create(name="Colour", title="Colour", type=PROPERTY_TEXT_FIELD)
        url = reverse("lfs_manage_property", kwargs={"id": colour.id})
        data = form_data(manager.get(url)) | {"title": "Farbe", "unit": "cm", "filterable": "on"}

        response = manager.post(url, data)

        colour.refresh_from_db()
        assert (colour.title, colour.unit, colour.filterable) == ("Farbe", "cm", True)
        assert response["Location"] == url
        assert messages_of(response) == ["Property has been saved."]

    def test_changing_the_type_drops_the_stored_values(self, manager):
        colour = Property.objects.create(name="Colour", title="Colour", type=PROPERTY_TEXT_FIELD)
        stored_value(colour)
        url = reverse("lfs_manage_property", kwargs={"id": colour.id})

        manager.post(url, form_data(manager.get(url)) | {"type": PROPERTY_SELECT_FIELD})

        assert not ProductPropertyValue.objects.exists()

    def test_keeping_the_type_keeps_the_stored_values(self, manager):
        colour = Property.objects.create(name="Colour", title="Colour", type=PROPERTY_TEXT_FIELD)
        stored_value(colour)
        url = reverse("lfs_manage_property", kwargs={"id": colour.id})

        manager.post(url, form_data(manager.get(url)) | {"title": "Farbe"})

        assert ProductPropertyValue.objects.count() == 1

    def test_an_invalid_type_is_refused(self, manager):
        colour = Property.objects.create(name="Colour", title="Colour", type=PROPERTY_NUMBER_FIELD)
        stored_value(colour)
        url = reverse("lfs_manage_property", kwargs={"id": colour.id})

        assert manager.post(url, form_data(manager.get(url)) | {"type": "99"}).context["form"].errors["type"]
        assert Property.objects.get(pk=colour.pk).type == PROPERTY_NUMBER_FIELD
        assert ProductPropertyValue.objects.count() == 1


class TestOptions:
    @pytest.fixture
    def colour(self):
        return Property.objects.create(name="Colour", type=PROPERTY_SELECT_FIELD)

    def test_adds_an_option_with_its_price(self, manager, colour):
        response = manager.post(
            reverse("lfs_add_property_option", kwargs={"property_id": colour.id}), {"name": " Red ", "price": "1.5"}
        )

        assert list(colour.options.values_list("name", "price")) == [("Red", 1.5)]
        assert response["Location"] == reverse("lfs_manage_property", kwargs={"id": colour.id})
        assert messages_of(response) == ["Option has been added."]

    def test_an_option_needs_a_name(self, manager, colour):
        response = manager.post(
            reverse("lfs_add_property_option", kwargs={"property_id": colour.id}), {"name": " ", "price": "1"}
        )

        assert not colour.options.exists()
        assert messages_of(response) == ["Option could not be added. Name is required."]

    def test_updates_an_option(self, manager, colour):
        red = PropertyOption.objects.create(property=colour, name="Red", price=1)

        response = manager.post(
            reverse("lfs_update_property_option", kwargs={"property_id": colour.id}),
            {"option_id": red.id, "name": "Dark red", "price": "2.5"},
        )

        red.refresh_from_db()
        assert (red.name, red.price) == ("Dark red", 2.5)
        assert messages_of(response) == ["Option has been updated."]

    def test_an_option_of_another_property_is_not_updated(self, manager, colour):
        other = PropertyOption.objects.create(property=Property.objects.create(name="Size"), name="XL")

        response = manager.post(
            reverse("lfs_update_property_option", kwargs={"property_id": colour.id}),
            {"option_id": other.id, "name": "Hacked", "price": "0"},
        )

        assert PropertyOption.objects.get(pk=other.pk).name == "XL"
        assert messages_of(response) == ["Option not found."]

    def test_an_updated_option_keeps_its_name_when_none_is_given(self, manager, colour):
        red = PropertyOption.objects.create(property=colour, name="Red")

        manager.post(
            reverse("lfs_update_property_option", kwargs={"property_id": colour.id}), {"option_id": red.id, "name": ""}
        )

        assert PropertyOption.objects.get(pk=red.pk).name == "Red"

    def test_deletes_an_option_and_renumbers_the_others(self, manager, colour):
        red = PropertyOption.objects.create(property=colour, name="Red", position=1)
        PropertyOption.objects.create(property=colour, name="Green", position=2)
        PropertyOption.objects.create(property=colour, name="Blue", position=3)

        manager.delete(reverse("lfs_delete_property_option", kwargs={"option_id": red.id}))

        assert list(colour.options.values_list("name", "position")) == [("Green", 10), ("Blue", 20)]


class TestDelete:
    def test_confirmation_names_the_property(self, manager):
        colour = Property.objects.create(name="Colour")

        response = manager.get(reverse("lfs_delete_property_confirm", kwargs={"id": colour.id}))

        assert response.context["property"] == colour

    def test_deletes_the_property_with_its_options_and_values(self, manager):
        colour = Property.objects.create(name="Colour", type=PROPERTY_SELECT_FIELD)
        PropertyOption.objects.create(property=colour, name="Red")
        stored_value(colour)

        response = manager.post(reverse("lfs_delete_property", kwargs={"id": colour.id}))

        assert not Property.objects.exists()
        assert not PropertyOption.objects.exists()
        assert not ProductPropertyValue.objects.exists()
        assert response["Location"] == reverse("lfs_manage_properties")
        assert messages_of(response) == ["Property has been deleted."]
