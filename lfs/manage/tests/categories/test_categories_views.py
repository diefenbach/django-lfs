"""The category management, tested through real requests as a shop manager: the tree and its search, saving the
data (including the image), the view settings, the products, SEO, portlets, viewing in the shop, and sorting the tree
by drag and drop. Levels of new categories are tested in test_category_level.py, deleting in
lfs/manage/tests/test_delete_views.py."""

import io
import os

import pytest
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from lfs.catalog.models import Category, Product
from lfs.manufacturer.models import Manufacturer

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    """Store uploaded files in a temporary folder."""
    settings.MEDIA_ROOT = str(tmp_path)


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def category(name: str, parent=None, position: int = 10) -> Category:
    level = parent.level + 1 if parent else 1
    return Category.objects.create(
        name=name, slug=name.lower().replace(" ", "-"), parent=parent, position=position, level=level
    )


def png() -> SimpleUploadedFile:
    """Return a small PNG upload."""
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), "red").save(buffer, "PNG")
    return SimpleUploadedFile("banner.png", buffer.getvalue(), content_type="image/png")


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def tree(nodes) -> list:
    """Return the hierarchy of the navigation as nested (name, [children]) tuples."""
    return [(n.name, tree(n.children)) for n in nodes]


class TestStartAndTree:
    def test_shows_the_first_category(self, manager):
        lights = category("Lights")

        assert manager.get(reverse("lfs_manage_categories"))["Location"] == reverse(
            "lfs_manage_category", kwargs={"id": lights.id}
        )

    def test_without_categories_shows_the_empty_page(self, manager):
        assert manager.get(reverse("lfs_manage_categories"))["Location"] == reverse("lfs_manage_no_categories")

    def test_shows_the_tree_in_its_order_and_the_search_as_a_flat_list(self, manager):
        lights = category("Lights", position=20)
        category("Lamps", parent=lights)
        category("Furniture", position=10)
        url = reverse("lfs_manage_category", kwargs={"id": lights.id})

        full = manager.get(url).context
        found = manager.get(url, {"q": "lamp"}).context

        assert tree(full["hierarchical_categories"]) == [("Furniture", []), ("Lights", [("Lamps", [])])]
        assert tree(found["hierarchical_categories"]) == [("Lamps", [])]
        assert all(u.endswith("?q=lamp") for _, u in found["tabs"])


class TestCategory:
    def test_saves_the_data_and_the_image(self, manager):
        lights = category("Lights")
        url = reverse("lfs_manage_category", kwargs={"id": lights.id})

        response = manager.post(
            url, {"name": "Lighting", "slug": "lighting", "description": "All lamps", "image": png()}
        )

        lights.refresh_from_db()
        assert (lights.name, lights.slug, lights.description) == ("Lighting", "lighting", "All lamps")
        assert lights.image.name.endswith(".png")
        assert response["Location"] == url
        assert messages_of(response) == ["Category data has been saved."]

    def test_deleting_the_image_removes_it(self, manager):
        lights = category("Lights")
        url = reverse("lfs_manage_category", kwargs={"id": lights.id})
        data = {"name": "Lights", "slug": "lights"}
        manager.post(url, data | {"image": png()})
        path = Category.objects.get(pk=lights.pk).image.path

        manager.post(url, data | {"delete_image": "on"})

        assert not Category.objects.get(pk=lights.pk).image
        assert not os.path.exists(path)

    def test_saves_the_view_settings(self, manager):
        lights = category("Lights")
        url = reverse("lfs_manage_category_view", kwargs={"id": lights.id})

        response = manager.post(url, {"template": 1, "show_all_products": "on"})

        lights.refresh_from_db()
        assert (lights.template, lights.show_all_products) == (1, True)
        assert messages_of(response) == ["View data has been saved."]

    def test_saves_the_seo_data(self, manager):
        lights = category("Lights")

        manager.post(
            reverse("lfs_manage_category_seo", kwargs={"id": lights.id}),
            {"meta_title": "Lights", "meta_description": "Lamps", "meta_keywords": "lamp"},
        )

        lights.refresh_from_db()
        assert (lights.meta_title, lights.meta_description, lights.meta_keywords) == ("Lights", "Lamps", "lamp")

    def test_shows_the_portlets_tab(self, manager):
        response = manager.get(reverse("lfs_manage_category_portlets", kwargs={"id": category("Lights").id}))

        assert response.context["active_tab"] == "portlets" and response.context["portlets"]

    def test_view_opens_the_category_in_the_shop(self, manager):
        response = manager.get(reverse("lfs_manage_category_by_id", kwargs={"id": category("Lights").id}))

        assert response["Location"] == reverse("lfs_category", kwargs={"slug": "lights"})

    def test_adding_offers_the_parents_name(self, manager):
        lights = category("Lights")

        response = manager.get(reverse("lfs_manage_add_category", kwargs={"parent_id": lights.id}))

        assert response.context["parent_name"] == "Lights"


class TestProducts:
    def url(self, c: Category) -> str:
        return reverse("lfs_manage_category_products", kwargs={"id": c.id})

    def test_assigns_and_removes_the_checked_products(self, manager):
        lights = category("Lights")
        lamp, shade, chair = (Product.objects.create(name=n, slug=n.lower()) for n in ("Lamp", "Shade", "Chair"))

        manager.post(
            self.url(lights), {"assign_products": "1", f"product-{lamp.id}": "on", f"product-{shade.id}": "on"}
        )
        assert set(lights.products.all()) == {lamp, shade}

        response = manager.post(self.url(lights), {"remove_products": "1", f"product-{shade.id}": "on"})
        assert list(lights.products.all()) == [lamp]
        assert response["Location"] == self.url(lights)
        assert messages_of(response)[-1] == "Products have been removed."

    def test_offers_unassigned_products_filtered_by_name_category_and_manufacturer(self, manager):
        lights, furniture = category("Lights"), category("Furniture")
        acme = Manufacturer.objects.create(name="Acme", slug="acme")
        desk_lamp = Product.objects.create(name="Desk lamp", slug="desk-lamp", manufacturer=acme)
        floor_lamp = Product.objects.create(name="Floor lamp", slug="floor-lamp")
        desk_lamp.categories.add(furniture)
        floor_lamp.categories.add(furniture)

        def offered(**params):
            return list(manager.get(self.url(lights), params).context["page"].object_list)

        assert offered(filter="lamp", products_category_filter=furniture.id, products_manufacturer_filter=acme.id) == [
            desk_lamp
        ]
        assert offered(filter="lamp", products_manufacturer_filter="None") == [floor_lamp]


class TestSort:
    def test_stores_the_new_order_parents_and_levels(self, manager):
        lights, furniture = category("Lights", position=10), category("Furniture", position=20)
        lamps = category("Lamps", parent=lights)

        response = manager.post(
            reverse("lfs_manage_sort_categories"),
            {
                "categories": f"category[{furniture.id}]=root&category[{lights.id}]=root&category[{lamps.id}]={furniture.id}"
            },
        )

        assert response.json()["message"] == "The categories have been sorted."
        lamps.refresh_from_db()
        assert (lamps.parent, lamps.level) == (furniture, 2)
        assert list(Category.objects.filter(parent=None).order_by("position").values_list("name", flat=True)) == [
            "Furniture",
            "Lights",
        ]

    def test_without_data_changes_nothing(self, manager):
        response = manager.post(reverse("lfs_manage_sort_categories"))

        assert response.json()["message"] == "No category data received."
