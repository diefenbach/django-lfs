from django.urls import path

from .views import (
    ImagesListView,
    ImagesUploadView,
    ImagePreviewView,
    DeleteImagesConfirmView,
    DeleteImagesView,
    AddImagesView,
    ImageBrowserView,
)

urlpatterns = [
    path("images/", ImagesListView.as_view(), name="lfs_manage_images_list"),
    path("images/upload/", ImagesUploadView.as_view(), name="lfs_manage_images_upload"),
    path("images/preview/<int:image_id>/", ImagePreviewView.as_view(), name="lfs_manage_images_preview"),
    path("images/delete/confirm/", DeleteImagesConfirmView.as_view(), name="lfs_manage_images_delete_confirm"),
    path("images/add/", AddImagesView.as_view(), name="lfs_manage_images_add"),
    path("images/delete/", DeleteImagesView.as_view(), name="lfs_manage_images_delete"),
    path("images/browser/", ImageBrowserView.as_view(), name="lfs_manage_imagebrowser"),
]
