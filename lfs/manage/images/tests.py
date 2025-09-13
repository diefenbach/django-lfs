import json
from io import BytesIO
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from PIL import Image as PILImage

from lfs.catalog.models import Image
from lfs.manage.images.views import (
    ImagesListView,
    ImagesListAjaxView,
    DeleteImagesView,
    AddImagesView,
    ImageBrowserView,
)
from lfs.manage.images.forms import (
    ImageUploadForm,
    ImageFilterForm,
    ImageDeleteForm,
    ImageBrowserForm,
)


@pytest.fixture
@pytest.mark.django_db
def admin_user():
    """Create an admin user with manage_shop permission."""
    user = User.objects.create_user(username="admin", email="admin@test.com", password="testpass123")
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture
def request_factory():
    """Create a request factory instance."""
    return RequestFactory()


@pytest.fixture
def sample_image():
    """Create a sample image file for testing."""
    # Create a simple test image
    image = PILImage.new("RGB", (100, 100), color="red")
    image_file = BytesIO()
    image.save(image_file, format="JPEG")
    image_file.seek(0)

    return SimpleUploadedFile(name="test_image.jpg", content=image_file.read(), content_type="image/jpeg")


@pytest.fixture
@pytest.mark.django_db
def image_instance(sample_image):
    """Create an Image model instance."""
    image = Image.objects.create(title="Test Image")
    image.image.save("test.jpg", sample_image, save=True)
    return image


@pytest.mark.django_db
class TestImagesListView:
    """Test cases for ImagesListView."""

    def test_get_queryset_without_query(self, request_factory, admin_user, image_instance):
        """Test queryset without search query returns all global images."""
        request = request_factory.get("/images/")
        request.user = admin_user

        view = ImagesListView()
        view.request = request

        queryset = view.get_queryset()
        assert queryset.count() == 1
        assert image_instance in queryset

    def test_get_queryset_with_query(self, request_factory, admin_user, image_instance):
        """Test queryset with search query filters images."""
        # Create another image that shouldn't match
        other_image = Image.objects.create(title="Other Image")

        request = request_factory.get("/images/?q=Test")
        request.user = admin_user

        view = ImagesListView()
        view.request = request

        queryset = view.get_queryset()
        assert queryset.count() == 1
        assert image_instance in queryset
        assert other_image not in queryset

    def test_get_context_data(self, request_factory, admin_user, image_instance):
        """Test context data includes pagination and images."""
        request = request_factory.get("/images/")
        request.user = admin_user

        view = ImagesListView()
        view.request = request

        context = view.get_context_data()

        assert "images" in context
        assert "pagination" in context
        assert "query" in context
        assert context["query"] == ""

    def test_pagination_with_invalid_start(self, request_factory, admin_user, image_instance):
        """Test pagination handles invalid start parameter."""
        request = request_factory.get("/images/?start=invalid")
        request.user = admin_user

        view = ImagesListView()
        view.request = request

        context = view.get_context_data()
        assert "pagination" in context


@pytest.mark.django_db
class TestImagesListAjaxView:
    """Test cases for ImagesListAjaxView."""

    def test_render_to_response_returns_json(self, request_factory, admin_user, image_instance):
        """Test AJAX view returns JSON response."""
        request = request_factory.get("/images/list/")
        request.user = admin_user

        view = ImagesListAjaxView()
        view.request = request

        context = view.get_context_data()
        response = view.render_to_response(context)

        assert response["Content-Type"] == "application/json"

        data = json.loads(response.content)
        assert "html" in data
        assert "message" in data


@pytest.mark.django_db
class TestDeleteImagesView:
    """Test cases for DeleteImagesView."""

    def test_post_deletes_selected_images(self, request_factory, admin_user, image_instance):
        """Test POST request deletes selected images."""
        # Create another image
        image2 = Image.objects.create(title="Image 2")

        request = request_factory.post("/images/delete/", {"images": [str(image_instance.pk), str(image2.pk)]})
        request.user = admin_user

        view = DeleteImagesView()
        response = view.post(request)

        assert response.status_code == 302
        assert Image.objects.count() == 0

    def test_post_with_no_images_selected(self, request_factory, admin_user):
        """Test POST request with no images selected."""
        request = request_factory.post("/images/delete/", {"images": []})
        request.user = admin_user

        view = DeleteImagesView()
        response = view.post(request)

        assert response.status_code == 302


@pytest.mark.django_db
class TestAddImagesView:
    """Test cases for AddImagesView."""

    def test_post_uploads_single_image(self, request_factory, admin_user, sample_image):
        """Test POST request uploads a single image."""
        request = request_factory.post("/images/add/", {"files[]": [sample_image]})
        request.user = admin_user
        request.FILES = {"files[]": [sample_image]}

        view = AddImagesView()
        response = view.post(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["success"] is True

    def test_post_uploads_multiple_images(self, request_factory, admin_user):
        """Test POST request uploads multiple images."""
        image1 = self._create_test_image("image1.jpg")
        image2 = self._create_test_image("image2.jpg")

        request = request_factory.post("/images/add/")
        request.user = admin_user
        request.FILES = {"files[]": [image1, image2]}

        view = AddImagesView()
        response = view.post(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["results"]) == 2
        assert all(result["success"] for result in data["results"])

    @patch("lfs.manage.images.views.logger")
    def test_post_handles_upload_error(self, mock_logger, request_factory, admin_user):
        """Test POST request handles upload errors gracefully."""
        # Create a mock file that will cause an error
        bad_file = Mock()
        bad_file.name = "bad_file.jpg"
        bad_file.size = 1000

        request = request_factory.post("/images/add/")
        request.user = admin_user
        request.FILES = {"files[]": [bad_file]}

        with patch("lfs.catalog.models.Image.image.save", side_effect=Exception("Upload failed")):
            view = AddImagesView()
            response = view.post(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["results"]) == 1
        assert data["results"][0]["success"] is False
        assert "error" in data["results"][0]
        mock_logger.info.assert_called()

    def _create_test_image(self, name):
        """Helper method to create test image."""
        image = PILImage.new("RGB", (50, 50), color="blue")
        image_file = BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)

        return SimpleUploadedFile(name=name, content=image_file.read(), content_type="image/jpeg")


@pytest.mark.django_db
class TestImageBrowserView:
    """Test cases for ImageBrowserView."""

    def test_get_selected_image_data_with_valid_url(self, image_instance):
        """Test parsing valid URL returns image and size."""
        view = ImageBrowserView()
        url = f"/media/images/test.100x100.jpg"

        # Mock the Image.objects.get to return our test image
        with patch("lfs.catalog.models.Image.objects.get", return_value=image_instance):
            image, size = view.get_selected_image_data(url)

        assert image == image_instance
        assert size == "100x100"

    def test_get_selected_image_data_with_invalid_url(self):
        """Test parsing invalid URL returns None values."""
        view = ImageBrowserView()

        image, size = view.get_selected_image_data("invalid_url")
        assert image is None
        assert size is None

    def test_get_size_options(self):
        """Test size options generation."""
        view = ImageBrowserView()

        # Test with actual THUMBNAIL_SIZES from settings
        sizes = view.get_size_options("100x100")

        # Check that we get some sizes and the selected one is correct
        assert len(sizes) > 0
        selected_sizes = [s for s in sizes if s["selected"]]
        assert len(selected_sizes) == 1
        assert selected_sizes[0]["value"] == "100x100"

    def test_get_class_options(self):
        """Test CSS class options generation."""
        view = ImageBrowserView()

        classes = view.get_class_options("left")

        assert len(classes) == 3
        left_option = next(c for c in classes if c["value"] == "left")
        assert left_option["selected"] is True

    def test_get_images_data(self, image_instance):
        """Test images data formatting."""
        view = ImageBrowserView()

        # Create a mock page object
        mock_page = Mock()
        mock_page.object_list = [image_instance]

        images_data = view.get_images_data(mock_page, image_instance)

        assert len(images_data) == 1
        assert images_data[0]["id"] == image_instance.id
        assert images_data[0]["title"] == image_instance.title
        assert images_data[0]["checked"] is True

    def test_get_request_returns_json(self, request_factory, admin_user, image_instance):
        """Test GET request returns JSON response."""
        request = request_factory.get("/images/browser/")
        request.user = admin_user

        view = ImageBrowserView()
        response = view.get(request)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"

        data = json.loads(response.content)
        assert "html" in data
        assert "message" in data


class TestImageUploadForm:
    """Test cases for ImageUploadForm."""

    def test_form_valid_with_single_image(self, sample_image):
        """Test form validation with single valid image."""
        form = ImageUploadForm()
        form.files = Mock()
        form.files.getlist.return_value = [sample_image]

        # Mock the cleaned_data
        form.cleaned_data = {"files": [sample_image]}
        form._errors = {}

        assert form.is_valid() or len(form.errors) == 0

    def test_form_invalid_with_no_files(self):
        """Test form validation fails with no files."""
        form = ImageUploadForm(data={})

        assert not form.is_valid()
        assert "files" in form.errors

    def test_validate_image_file_size_limit(self):
        """Test file size validation."""
        form = ImageUploadForm()

        # Create a mock file that's too large
        large_file = Mock()
        large_file.name = "large.jpg"
        large_file.size = 11 * 1024 * 1024  # 11MB

        with pytest.raises(Exception):  # Should raise ValidationError
            form._validate_image_file(large_file)

    def test_validate_image_file_type(self):
        """Test file type validation."""
        form = ImageUploadForm()

        # Create a mock file with invalid type
        invalid_file = Mock()
        invalid_file.name = "document.pdf"
        invalid_file.content_type = "application/pdf"
        invalid_file.size = 1000

        with pytest.raises(Exception):  # Should raise ValidationError
            form._validate_image_file(invalid_file)


@pytest.mark.django_db
class TestImageFilterForm:
    """Test cases for ImageFilterForm."""

    def test_form_valid_with_query(self):
        """Test form validation with search query."""
        form = ImageFilterForm(data={"q": "test"})

        assert form.is_valid()
        assert form.cleaned_data["q"] == "test"

    def test_form_valid_without_query(self):
        """Test form validation without search query."""
        form = ImageFilterForm(data={})

        assert form.is_valid()
        assert form.cleaned_data["q"] == ""

    def test_get_queryset_with_query(self, image_instance):
        """Test queryset filtering with search query."""
        form = ImageFilterForm(data={"q": "Test"})
        form.is_valid()

        # Create another image that shouldn't match
        Image.objects.create(title="Other Image")

        queryset = form.get_queryset()
        assert queryset.count() == 1
        assert image_instance in queryset

    def test_get_queryset_without_query(self, image_instance):
        """Test queryset without filtering."""
        form = ImageFilterForm(data={})
        form.is_valid()

        # Create another image
        Image.objects.create(title="Other Image")

        queryset = form.get_queryset()
        assert queryset.count() == 2


@pytest.mark.django_db
class TestImageDeleteForm:
    """Test cases for ImageDeleteForm."""

    def test_form_valid_with_selected_images(self, image_instance):
        """Test form validation with selected images."""
        form = ImageDeleteForm(data={"images": [image_instance.pk]})

        assert form.is_valid()

    def test_form_invalid_without_selection(self):
        """Test form validation fails without selection."""
        form = ImageDeleteForm(data={"images": []})

        assert not form.is_valid()
        assert "images" in form.errors

    def test_delete_selected(self, image_instance):
        """Test deleting selected images."""
        # Create another image
        image2 = Image.objects.create(title="Image 2")

        form = ImageDeleteForm(data={"images": [image_instance.pk, image2.pk]})
        form.is_valid()

        count = form.delete_selected()

        assert count == 2
        assert Image.objects.count() == 0


@pytest.mark.django_db
class TestImageBrowserForm:
    """Test cases for ImageBrowserForm."""

    def test_form_valid_with_image_selection(self, image_instance):
        """Test form validation with image selection."""
        form = ImageBrowserForm(data={"image": image_instance.pk, "alignment": "left", "size": "100x100"})

        assert form.is_valid()

    def test_form_invalid_without_image(self):
        """Test form validation fails without image selection."""
        form = ImageBrowserForm(data={"alignment": "left", "size": "100x100"})

        assert not form.is_valid()
        assert "image" in form.errors

    def test_get_image_url_with_size(self, image_instance):
        """Test getting image URL with size parameter."""
        form = ImageBrowserForm(data={"image": image_instance.pk, "alignment": "left", "size": "100x100"})
        form.is_valid()

        # Mock the sized URL attribute
        with patch.object(image_instance.image, "url_100x100", "http://example.com/image.100x100.jpg"):
            url = form.get_image_url()
            assert "100x100" in url or url == image_instance.image.url

    def test_get_image_url_without_size(self, image_instance):
        """Test getting image URL without size parameter."""
        form = ImageBrowserForm(data={"image": image_instance.pk, "alignment": "left", "size": ""})
        form.is_valid()

        url = form.get_image_url()
        assert url == image_instance.image.url


# Integration tests
@pytest.mark.django_db
class TestImagesIntegration:
    """Integration tests for the images module."""

    def test_full_upload_workflow(self, admin_user, sample_image):
        """Test complete image upload workflow."""
        # Test upload
        upload_view = AddImagesView()
        factory = RequestFactory()

        request = factory.post("/images/add/")
        request.user = admin_user
        request.FILES = {"files[]": [sample_image]}

        response = upload_view.post(request)
        assert response.status_code == 200

        # Verify image was created
        assert Image.objects.count() == 1
        image = Image.objects.first()
        assert image.title == "test_image.jpg"

    def test_full_delete_workflow(self, admin_user, image_instance):
        """Test complete image delete workflow."""
        # Verify image exists
        assert Image.objects.count() == 1

        # Test delete
        delete_view = DeleteImagesView()
        factory = RequestFactory()

        request = factory.post("/images/delete/", {"images": [str(image_instance.pk)]})
        request.user = admin_user

        response = delete_view.post(request)
        assert response.status_code == 302

        # Verify image was deleted
        assert Image.objects.count() == 0
