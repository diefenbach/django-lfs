import pytest
from django.urls import reverse

from lfs.catalog.models import Image


@pytest.mark.django_db
class TestTinyMCEImageBrowserView:
    """Test the TinyMCE image browser API."""

    def test_get_images_success(self, client, admin_user):
        """Test successful retrieval of images."""
        # Create test images
        Image.objects.create(title="Test Image 1", alt="Alt text 1", image="test1.jpg")
        Image.objects.create(title="Test Image 2", alt="Alt text 2", image="test2.jpg")

        client.force_login(admin_user)
        response = client.get(reverse("tinymce_image_browser_api"))

        assert response.status_code == 200
        data = response.json()
        assert "images" in data
        assert "pagination" in data
        assert len(data["images"]) == 2
        assert data["images"][0]["text"] == "Test Image 1"
        assert data["images"][1]["text"] == "Test Image 2"

    def test_get_images_with_search(self, client, admin_user):
        """Test image search functionality."""
        Image.objects.create(title="Red Car", alt="A red car", image="red_car.jpg")
        Image.objects.create(title="Blue House", alt="A blue house", image="blue_house.jpg")

        client.force_login(admin_user)
        response = client.get(reverse("tinymce_image_browser_api"), {"q": "red"})

        assert response.status_code == 200
        data = response.json()
        assert len(data["images"]) == 1
        assert data["images"][0]["text"] == "Red Car"

    def test_get_images_pagination(self, client, admin_user):
        """Test pagination functionality."""
        # Create 25 test images
        for i in range(25):
            Image.objects.create(title=f"Test Image {i}", alt=f"Alt text {i}", image=f"test{i}.jpg")

        client.force_login(admin_user)
        response = client.get(reverse("tinymce_image_browser_api"), {"page": 2})

        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["current_page"] == 2
        assert data["pagination"]["total_pages"] == 2  # 25 images / 20 per page = 2 pages
        assert len(data["images"]) == 5  # 5 images on second page


@pytest.mark.django_db
class TestTinyMCEImageBrowserModalView:
    """Test the TinyMCE image browser modal view."""

    def test_modal_view_success(self, client, admin_user, shop):
        """Test successful modal view rendering."""
        client.force_login(admin_user)
        response = client.get(reverse("tinymce_image_browser_modal"))

        assert response.status_code == 200
        assert "Select Image" in response.content.decode()
        assert "imageBrowserModal" in response.content.decode()


@pytest.mark.django_db
class TestTinyMCEImageBrowserHTMXView:
    """Test the HTMX TinyMCE image browser view."""

    def test_htmx_view_success(self, client, admin_user, shop):
        """Test successful HTMX view rendering."""
        # Create test images
        Image.objects.create(title="Test Image 1", alt="Alt text 1", image="test1.jpg")
        Image.objects.create(title="Test Image 2", alt="Alt text 2", image="test2.jpg")

        client.force_login(admin_user)
        response = client.get(reverse("tinymce_image_browser"))

        assert response.status_code == 200
        content = response.content.decode()
        assert "Test Image 1" in content
        assert "Test Image 2" in content
        assert "image-card" in content

    def test_htmx_view_with_search(self, client, admin_user, shop):
        """Test HTMX view with search functionality."""
        Image.objects.create(title="Red Car", alt="A red car", image="red_car.jpg")
        Image.objects.create(title="Blue House", alt="A blue house", image="blue_house.jpg")

        client.force_login(admin_user)
        response = client.get(reverse("tinymce_image_browser"), {"q": "red"})

        assert response.status_code == 200
        content = response.content.decode()
        assert "Red Car" in content
        assert "Blue House" not in content


@pytest.mark.django_db
def test_the_browser_offers_only_library_images_not_product_images(client, admin_user, shop):
    from lfs.catalog.models import Product

    Image.objects.create(title="Beach", image="beach.jpg")
    Image.objects.create(title="Lamp photo", image="lamp.jpg", content=Product.objects.create(name="Lamp", slug="lamp"))
    client.force_login(admin_user)

    api = client.get(reverse("tinymce_image_browser_api")).json()
    grid = client.get(reverse("tinymce_image_browser")).context["images"]

    assert [i["text"] for i in api["images"]] == ["Beach"]
    assert [i["title"] for i in grid] == ["Beach"]


@pytest.mark.django_db
def test_the_browser_shows_the_pages_around_the_current_one(client, admin_user, shop):
    Image.objects.bulk_create(Image(title=f"Image {i}", image=f"image-{i}.jpg") for i in range(200))
    client.force_login(admin_user)

    pagination = client.get(reverse("tinymce_image_browser"), {"page": 5}).context["pagination"]

    assert pagination["page_range"] == [1, None, 3, 4, 5, 6, 7, None, 10]
