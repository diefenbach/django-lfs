from django.urls import path

from .views import (
    ImagesListView,
    ImagesUploadView,
    ImagesListAjaxView,
    ImagePreviewView,
    DeleteImagesView,
    AddImagesView,
    ImageBrowserView,
)

urlpatterns = [
    path("images/", ImagesListView.as_view(), name="lfs_manage_images_list"),
    path("images/upload/", ImagesUploadView.as_view(), name="lfs_manage_images_upload"),
    path("images/list/", ImagesListAjaxView.as_view(), name="lfs_manage_images_list_ajax"),
    path("images/preview/<int:image_id>/", ImagePreviewView.as_view(), name="lfs_manage_images_preview"),
    path("images/add/", AddImagesView.as_view(), name="lfs_manage_images_add"),
    path("images/delete/", DeleteImagesView.as_view(), name="lfs_manage_images_delete"),
    path("images/browser/", ImageBrowserView.as_view(), name="lfs_manage_imagebrowser"),
]
