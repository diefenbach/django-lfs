"""The manufacturer management, tested through real requests as a shop manager: the list and its search, adding,
saving (including the image), SEO, portlets, viewing and deleting a manufacturer, and the search for manufacturers
that product forms use. Assigning products is tested in test_manufacturer_products.py."""

import io

import pytest
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from lfs.catalog.models import Product
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


@pytest.fixture
def acme():
    return Manufacturer.objects.create(name="Acme", slug="acme")


def png() -> SimpleUploadedFile:
    """Return a small PNG upload."""
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), "red").save(buffer, "PNG")
    return SimpleUploadedFile("logo.png", buffer.getvalue(), content_type="image/png")


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


class TestStartAndList:
    def test_shows_the_first_manufacturer(self, manager, acme):
        assert manager.get(reverse("lfs_manage_manufacturers"))["Location"] == reverse(
            "lfs_manage_manufacturer", kwargs={"id": acme.id}
        )

    def test_without_manufacturers_shows_the_empty_page(self, manager):
        assert manager.get(reverse("lfs_manage_manufacturers"))["Location"] == reverse("lfs_manage_no_manufacturers")

    def test_search_filters_the_list_and_the_tabs_keep_it(self, manager, acme):
        Manufacturer.objects.create(name="Globex", slug="globex")

        response = manager.get(reverse("lfs_manage_manufacturer", kwargs={"id": acme.id}), {"q": "ac"})

        assert list(response.context["manufacturers"]) == [acme]
        assert all(url.endswith("?q=ac") for _, url in response.context["tabs"])


class TestManufacturer:
    def test_adds_a_manufacturer(self, manager):
        response = manager.post(reverse("lfs_manage_add_manufacturer"), {"name": "Acme", "slug": "acme"})

        acme = Manufacturer.objects.get()
        assert response["Location"] == reverse("lfs_manage_manufacturer", kwargs={"id": acme.id})
        assert messages_of(response) == ["Manufacturer has been created."]

    def test_a_slug_must_be_unique(self, manager, acme):
        response = manager.post(reverse("lfs_manage_add_manufacturer"), {"name": "Acme 2", "slug": "acme"})

        assert response.context["form"].errors["slug"]
        assert Manufacturer.objects.count() == 1

    def test_saves_the_data_and_the_image(self, manager, acme):
        url = reverse("lfs_manage_manufacturer", kwargs={"id": acme.id})

        response = manager.post(
            url, {"name": "Acme Corp", "slug": "acme", "short_description": "Lamps", "image": png()}
        )

        acme.refresh_from_db()
        assert (acme.name, acme.short_description) == ("Acme Corp", "Lamps")
        assert acme.image.name.endswith(".png")
        assert response["Location"] == url
        assert messages_of(response) == ["Manufacturer data has been saved."]

    def test_saves_the_seo_data(self, manager, acme):
        url = reverse("lfs_manage_manufacturer_seo", kwargs={"id": acme.id})

        manager.post(url, {"meta_title": "Acme", "meta_description": "Lamps", "meta_keywords": "acme"})

        acme.refresh_from_db()
        assert (acme.meta_title, acme.meta_description, acme.meta_keywords) == ("Acme", "Lamps", "acme")

    def test_shows_the_portlets_tab(self, manager, acme):
        response = manager.get(reverse("lfs_manage_manufacturer_portlets", kwargs={"id": acme.id}))

        assert response.context["active_tab"] == "portlets" and response.context["portlets"]

    def test_view_opens_the_manufacturer_in_the_shop(self, manager, acme):
        response = manager.get(reverse("lfs_manufacturer_by_id", kwargs={"id": acme.id}))

        assert response["Location"] == reverse("lfs_manufacturer", kwargs={"slug": "acme"})

    def test_deletes_the_manufacturer_but_keeps_its_products(self, manager, acme):
        lamp = Product.objects.create(name="Lamp", slug="lamp", manufacturer=acme)

        assert (
            manager.get(reverse("lfs_delete_manufacturer_confirm", kwargs={"id": acme.id})).context["manufacturer"]
            == acme
        )
        response = manager.post(reverse("lfs_delete_manufacturer", kwargs={"id": acme.id}))

        assert not Manufacturer.objects.exists()
        assert Product.objects.get(pk=lamp.pk).manufacturer is None
        assert response["Location"] == reverse("lfs_manage_manufacturers")


def test_the_manufacturer_search_finds_names_that_start_with_the_term(manager, acme):
    Manufacturer.objects.create(name="Globex", slug="globex")
    Manufacturer.objects.create(name="Mega Acme", slug="mega-acme")

    response = manager.get(reverse("lfs_manufacturers_ajax"), {"term": "ac"})

    assert response.json() == [{"label": "Acme", "value": acme.id}]
