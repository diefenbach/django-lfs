"""URLs for django-lfs's tests: the storefront, the management interface, and what LFS's pages link to."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("lfs.core.urls")),
    path("manage/", include("lfs.manage.urls")),
    path("admin/", admin.site.urls),
    path("reviews/", include("reviews.urls")),
    path("captcha/", include("captcha.urls")),
    path("theme/", include("lfs_theme.urls")),
]
