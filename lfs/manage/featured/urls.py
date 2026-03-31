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
        featured_views.AddFeaturedView.as_view(),
        name="lfs_manage_add_featured",
    ),
    path(
        "featured/update",
        featured_views.RemoveFeaturedView.as_view(),
        name="lfs_manage_delete_featured",
    ),
    path(
        "featured/sort",
        featured_views.SortFeaturedView.as_view(),
        name="lfs_manage_sort_featured",
    ),
]
