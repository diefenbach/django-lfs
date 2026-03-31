from django.urls import path

from .views import TinyMCEImageBrowserView, TinyMCEImageBrowserAPIView, TinyMCEImageBrowserModalView

urlpatterns = [
    path("tinymce/image-browser/", TinyMCEImageBrowserView.as_view(), name="tinymce_image_browser"),
    path("tinymce/image-browser/api/", TinyMCEImageBrowserAPIView.as_view(), name="tinymce_image_browser_api"),
    path("tinymce/image-browser/modal/", TinyMCEImageBrowserModalView.as_view(), name="tinymce_image_browser_modal"),
]
