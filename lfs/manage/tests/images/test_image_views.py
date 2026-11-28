import pytest
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.test import RequestFactory
from django.urls import reverse

from lfs.catalog.models import Image
from lfs.manage.images.views import (
    ImagesListView,
    ImagePreviewView,
    DeleteImagesConfirmView,
    DeleteImagesView,
    AddImagesView,
    ImagesUploadView,
    ImagesTabMixin,
)

User = get_user_model()


class TestImagesTabMixin:
    """Test the ImagesTabMixin functionality."""


    def test_mixin_has_tab_name_attribute(self):
        """Should have tab_name attribute."""
        assert hasattr(ImagesTabMixin, "tab_name")
        assert ImagesTabMixin.tab_name is None

    def test_get_tabs_method_exists(self):
        """Should have _get_tabs method."""
        assert hasattr(ImagesTabMixin, "_get_tabs")
        assert callable(getattr(ImagesTabMixin, "_get_tabs"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(ImagesTabMixin, "get_context_data")
        assert callable(getattr(ImagesTabMixin, "get_context_data"))


class TestImagesListView:
    """Test the ImagesListView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from PermissionRequiredMixin, ImagesTabMixin, and TemplateView."""
        from django.contrib.auth.mixins import PermissionRequiredMixin
        from django.views.generic.base import TemplateView

        assert issubclass(ImagesListView, PermissionRequiredMixin)
        assert issubclass(ImagesListView, ImagesTabMixin)
        assert issubclass(ImagesListView, TemplateView)





    def test_get_queryset_method_exists(self):
        """Should have get_queryset method."""
        assert hasattr(ImagesListView, "get_queryset")
        assert callable(getattr(ImagesListView, "get_queryset"))

    def test_render_to_response_method_exists(self):
        """Should have render_to_response method."""
        assert hasattr(ImagesListView, "render_to_response")
        assert callable(getattr(ImagesListView, "render_to_response"))

    @pytest.mark.django_db
    def test_get_queryset_without_search(self, admin_user, multiple_images):
        """Should return all images when no search query."""
        factory = RequestFactory()
        request = factory.get("/images/")
        request.user = admin_user
        request.session = {}

        view = ImagesListView()
        view.request = request
        queryset = view.get_queryset()

        assert queryset.count() == 3
        assert all(img.content_id is None for img in queryset)

    @pytest.mark.django_db
    def test_get_queryset_with_search(self, admin_user, multiple_images):
        """Should filter images by search query."""
        factory = RequestFactory()
        request = factory.get("/images/?q=Image")
        request.user = admin_user
        request.session = {}

        view = ImagesListView()
        view.request = request
        queryset = view.get_queryset()

        assert queryset.count() == 2  # "Image 1" and "Image 2"
        assert all("Image" in img.title for img in queryset)

    @pytest.mark.django_db
    def test_get_context_data_includes_pagination(self, admin_user, multiple_images):
        """Should include pagination data in context."""
        factory = RequestFactory()
        request = factory.get("/images/")
        request.user = admin_user
        request.session = {}

        view = ImagesListView()
        view.request = request
        context = view.get_context_data()

        assert "images" in context
        assert "pagination" in context
        assert "pagination_data" in context
        assert "query" in context
        assert "tabs" in context
        assert "active_tab" in context

    @pytest.mark.django_db
    def test_render_to_response_htmx_request(self, admin_user, multiple_images, mock_session):
        """Should return partial HTML for HTMX requests."""
        factory = RequestFactory()
        request = factory.get("/images/")
        request.user = admin_user
        request.session = mock_session
        request.META["HTTP_HX_REQUEST"] = "true"

        view = ImagesListView()
        view.request = request
        response = view.render_to_response(view.get_context_data())

        assert isinstance(response, HttpResponse)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_render_to_response_regular_request(self, admin_user, multiple_images, mock_request):
        """Should return full page for regular requests."""
        view = ImagesListView()
        view.request = mock_request
        response = view.render_to_response(view.get_context_data())

        assert isinstance(response, HttpResponse)
        assert response.status_code == 200


class TestImagePreviewView:
    """Test the ImagePreviewView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from PermissionRequiredMixin and View."""
        from django.contrib.auth.mixins import PermissionRequiredMixin
        from django.views.generic.base import View

        assert issubclass(ImagePreviewView, PermissionRequiredMixin)
        assert issubclass(ImagePreviewView, View)



    @pytest.mark.django_db
    def test_get_existing_image(self, admin_user, image, mock_session):
        """Should return preview for existing image."""
        factory = RequestFactory()
        request = factory.get(f"/images/preview/{image.id}/")
        request.user = admin_user
        request.session = mock_session

        view = ImagePreviewView()
        response = view.get(request, image_id=image.id)

        assert isinstance(response, HttpResponse)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_get_nonexistent_image(self, admin_user, mock_session):
        """Should handle nonexistent image gracefully."""
        factory = RequestFactory()
        request = factory.get("/images/preview/999/")
        request.user = admin_user
        request.session = mock_session

        view = ImagePreviewView()
        response = view.get(request, image_id=999)

        assert isinstance(response, HttpResponse)
        assert response.status_code == 200


class TestDeleteImagesConfirmView:
    """Test the DeleteImagesConfirmView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from PermissionRequiredMixin and View."""
        from django.contrib.auth.mixins import PermissionRequiredMixin
        from django.views.generic.base import View

        assert issubclass(DeleteImagesConfirmView, PermissionRequiredMixin)
        assert issubclass(DeleteImagesConfirmView, View)



    @pytest.mark.django_db
    def test_get_with_selected_images(self, admin_user, multiple_images, mock_session):
        """Should return confirmation modal for selected images."""
        factory = RequestFactory()
        image_ids = [str(img.id) for img in multiple_images[:2]]
        request = factory.get(f"/images/delete-confirm/?images={'&images='.join(image_ids)}")
        request.user = admin_user
        request.session = mock_session

        view = DeleteImagesConfirmView()
        response = view.get(request)

        assert isinstance(response, HttpResponse)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_get_without_selected_images(self, admin_user, mock_session):
        """Should handle no selected images gracefully."""
        factory = RequestFactory()
        request = factory.get("/images/delete-confirm/")
        request.user = admin_user
        request.session = mock_session

        view = DeleteImagesConfirmView()
        response = view.get(request)

        assert isinstance(response, HttpResponse)
        assert response.status_code == 200


class TestDeleteImagesView:
    """Test the DeleteImagesView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from PermissionRequiredMixin and View."""
        from django.contrib.auth.mixins import PermissionRequiredMixin
        from django.views.generic.base import View

        assert issubclass(DeleteImagesView, PermissionRequiredMixin)
        assert issubclass(DeleteImagesView, View)



    @pytest.mark.django_db
    def test_post_deletes_selected_images(self, admin_user, multiple_images, monkeypatch):
        """Should delete selected images and redirect."""
        # Mock the messages framework
        mock_messages_success = monkeypatch.setattr(
            "lfs.manage.images.views.messages.success", lambda request, message: None
        )
        mock_messages_warning = monkeypatch.setattr(
            "lfs.manage.images.views.messages.warning", lambda request, message: None
        )

        factory = RequestFactory()
        image_ids = [str(img.id) for img in multiple_images[:2]]
        request = factory.post("/images/delete/", {"images": image_ids})
        request.user = admin_user

        view = DeleteImagesView()
        response = view.post(request)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse("lfs_manage_images_list")
        assert Image.objects.count() == 1  # Only one image should remain

    @pytest.mark.django_db
    def test_post_with_no_images(self, admin_user, monkeypatch):
        """Should handle no images selected gracefully."""
        # Mock the messages framework
        mock_messages_success = monkeypatch.setattr(
            "lfs.manage.images.views.messages.success", lambda request, message: None
        )
        mock_messages_warning = monkeypatch.setattr(
            "lfs.manage.images.views.messages.warning", lambda request, message: None
        )

        factory = RequestFactory()
        request = factory.post("/images/delete/", {})
        request.user = admin_user

        view = DeleteImagesView()
        response = view.post(request)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse("lfs_manage_images_list")


class TestAddImagesView:
    """Test the AddImagesView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from PermissionRequiredMixin and View."""
        from django.contrib.auth.mixins import PermissionRequiredMixin
        from django.views.generic.base import View

        assert issubclass(AddImagesView, PermissionRequiredMixin)
        assert issubclass(AddImagesView, View)



    def test_dispatch_has_csrf_exempt(self):
        """Should have csrf_exempt decorator on dispatch."""

        assert hasattr(AddImagesView.dispatch, "__wrapped__")

    @pytest.mark.django_db
    def test_post_uploads_images(self, admin_user, test_image_file):
        """Should upload images and return JSON response."""
        factory = RequestFactory()
        request = factory.post("/images/add/", {"files[]": [test_image_file]})
        request.user = admin_user

        view = AddImagesView()
        response = view.post(request)

        assert isinstance(response, JsonResponse)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_post_handles_upload_errors(self, admin_user, invalid_file):
        """Should handle upload errors gracefully."""
        factory = RequestFactory()
        request = factory.post("/images/add/", {"files[]": [invalid_file]})
        request.user = admin_user

        view = AddImagesView()
        response = view.post(request)

        assert isinstance(response, JsonResponse)
        assert response.status_code == 200


class TestImagesUploadView:
    """Test the ImagesUploadView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from PermissionRequiredMixin, ImagesTabMixin, and TemplateView."""
        from django.contrib.auth.mixins import PermissionRequiredMixin
        from django.views.generic.base import TemplateView

        assert issubclass(ImagesUploadView, PermissionRequiredMixin)
        assert issubclass(ImagesUploadView, ImagesTabMixin)
        assert issubclass(ImagesUploadView, TemplateView)



