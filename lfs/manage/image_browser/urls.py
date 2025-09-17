from django.urls import path
from .views import TinyMCEImageBrowserView, TinyMCEImageBrowserModalView

urlpatterns = [
    path("api/images/", TinyMCEImageBrowserView.as_view(), name="tinymce_image_browser_api"),
    path("modal/", TinyMCEImageBrowserModalView.as_view(), name="tinymce_image_browser_modal"),
]
