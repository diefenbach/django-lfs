"""The image library of the management, tested through real requests as a shop manager: the list with its search
and paging, the preview, uploading and deleting. The library holds the images that belong to no product."""

import io

import pytest
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image as PILImage

from lfs.catalog.models import Image, Product

pytestmark = pytest.mark.django_db

LIST = reverse("lfs_manage_images_list")


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    """Store uploaded files in a temporary folder."""
    settings.MEDIA_ROOT = str(tmp_path)


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def png(name: str = "photo.png") -> SimpleUploadedFile:
    """Return a small PNG upload."""
    buffer = io.BytesIO()
    PILImage.new("RGB", (4, 4), "red").save(buffer, "PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def library_image(title: str) -> Image:
    return Image.objects.create(title=title)


def product_image(title: str) -> Image:
    return Image.objects.create(title=title, content=Product.objects.create(name="Lamp", slug=f"lamp-{len(title)}"))


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


class TestList:
    def test_lists_the_library_newest_first_without_product_images(self, manager):
        first, second = library_image("Beach"), library_image("Forest")
        product_image("Lamp photo")

        assert list(manager.get(LIST).context["images"]) == [second, first]

    def test_search_finds_titles_that_start_with_the_term(self, manager):
        beach = library_image("Beach")
        library_image("Sunny beach")

        assert list(manager.get(LIST, {"q": "bea"}).context["images"]) == [beach]

    def test_htmx_search_returns_only_the_list(self, manager):
        library_image("Beach")

        response = manager.get(LIST, {"q": "bea"}, HTTP_HX_REQUEST="true")

        assert response.content.decode().startswith('<div id="files-list"')

    def test_shows_50_per_page_and_the_last_page_for_a_page_beyond_it(self, manager):
        for i in range(52):
            library_image(f"Image {i}")

        assert len(manager.get(LIST).context["images"]) == 50
        assert len(manager.get(LIST, {"page": 9}).context["images"]) == 2
        assert len(manager.get(LIST, {"page": "x"}).context["images"]) == 50

    def test_the_tabs_keep_the_search(self, manager):
        tabs = manager.get(LIST, {"q": "a & b"}).context["tabs"]

        assert all(url.endswith("?q=a+%26+b") for _, url in tabs)


class TestPreview:
    def test_shows_a_library_image(self, manager):
        beach = library_image("Beach")
        beach.image.save("beach.png", png(), save=True)

        response = manager.get(reverse("lfs_manage_images_preview", kwargs={"image_id": beach.id}))

        assert response.context["image"] == beach

    def test_does_not_show_a_product_image(self, manager):
        lamp = product_image("Lamp photo")

        response = manager.get(reverse("lfs_manage_images_preview", kwargs={"image_id": lamp.id}))

        assert "image" not in response.context and response.context["error"] == "Image not found"


class TestUpload:
    def test_stores_the_uploaded_images_in_the_library(self, manager):
        response = manager.post(reverse("lfs_manage_images_add"), {"files[]": [png("a.png"), png("b.png")]})

        assert sorted(Image.objects.filter(content_id=None).values_list("title", flat=True)) == ["a.png", "b.png"]
        assert [r["success"] for r in response.json()["results"]] == [True, True]

    def test_refuses_a_file_that_is_not_an_image(self, manager):
        response = manager.post(
            reverse("lfs_manage_images_add"), {"files[]": [SimpleUploadedFile("notes.txt", b"just text")]}
        )

        assert not Image.objects.exists()
        assert response.json()["results"][0]["success"] is False


class TestDelete:
    def test_confirmation_counts_the_selected_images(self, manager):
        a, b = library_image("A"), library_image("B")

        response = manager.get(reverse("lfs_manage_images_delete_confirm"), {"images": [a.id, b.id]})

        assert response.context["selected_count"] == 2

    def test_deletes_the_selected_images(self, manager):
        a, b, c = library_image("A"), library_image("B"), library_image("C")

        response = manager.post(reverse("lfs_manage_images_delete"), {"images": [a.id, c.id]})

        assert list(Image.objects.all()) == [b]
        assert response["Location"] == LIST
        assert messages_of(response) == ["2 images have been successfully deleted."]

    def test_without_a_selection_deletes_nothing(self, manager):
        library_image("A")

        response = manager.post(reverse("lfs_manage_images_delete"))

        assert Image.objects.count() == 1
        assert messages_of(response) == ["No images were selected for deletion."]

    def test_does_not_delete_product_images(self, manager):
        """Only library images are listed; a posted id of a product image must not delete it."""
        lamp = product_image("Lamp photo")
        beach = library_image("Beach")

        response = manager.post(reverse("lfs_manage_images_delete"), {"images": [lamp.id, beach.id]})

        assert list(Image.objects.all()) == [lamp]
        assert messages_of(response) == ["1 image has been successfully deleted."]


def test_uploading_without_a_csrf_token_is_refused(admin_user, shop):
    """Another site could otherwise make a logged-in manager's browser upload images; the page sends the token."""
    from django.test import Client

    client = Client(enforce_csrf_checks=True)
    client.force_login(admin_user)

    response = client.post(reverse("lfs_manage_images_add"), {"files[]": [png()]})

    assert response.status_code == 403
    assert not Image.objects.exists()


def test_uploading_with_the_pages_csrf_token_works(admin_user, shop):
    from django.test import Client

    client = Client(enforce_csrf_checks=True)
    client.force_login(admin_user)
    token = client.get(reverse("lfs_manage_images_upload")).context["csrf_token"]

    client.post(reverse("lfs_manage_images_add"), {"files[]": [png()], "csrfmiddlewaretoken": str(token)})

    assert Image.objects.count() == 1
