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

    def test_requires_permission(self, client):
        """Test that view requires proper permissions."""
        response = client.get(reverse("tinymce_image_browser_api"))
        assert response.status_code == 302  # Redirect to login


@pytest.mark.django_db
class TestTinyMCEImageBrowserModalView:
    """Test the TinyMCE image browser modal view."""

    def test_modal_view_success(self, client, admin_user):
        """Test successful modal view rendering."""
        client.force_login(admin_user)
        response = client.get(reverse("tinymce_image_browser_modal"))

        assert response.status_code == 200
        assert "Select Image" in response.content.decode()
        assert "imageBrowserModal" in response.content.decode()

    def test_modal_view_requires_permission(self, client):
        """Test that modal view requires proper permissions."""
        response = client.get(reverse("tinymce_image_browser_modal"))
        assert response.status_code == 302  # Redirect to login
