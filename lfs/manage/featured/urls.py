from django.urls import path
from lfs.manage.featured import views as featured_views

urlpatterns = [
    path(
        "featured",
        featured_views.ManageFeaturedView.as_view(),
        name="lfs_manage_featured",
    ),
    path(
        "featured/add",
        featured_views.add_featured,
        name="lfs_manage_add_featured",
    ),
    path(
        "featured/update",
        featured_views.update_featured,
        name="lfs_manage_update_featured",
    ),
    path(
        "featured/sort",
        featured_views.sort_featured,
        name="lfs_manage_sort_featured",
    ),
]
