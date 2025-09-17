from django.urls import path

from .views import TinyMCEImageBrowserView, TinyMCEImageBrowserModalView

urlpatterns = [
    path("tinymce/image-browser/api/", TinyMCEImageBrowserView.as_view(), name="tinymce_image_browser_api"),
    path("tinymce/image-browser/modal/", TinyMCEImageBrowserModalView.as_view(), name="tinymce_image_browser_modal"),
]
