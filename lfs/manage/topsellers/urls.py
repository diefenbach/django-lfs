from django.urls import path
from lfs.manage.topsellers import views as topseller_views

urlpatterns = [
    path(
        "topsellers",
        topseller_views.ManageTopsellerView.as_view(),
        name="lfs_manage_topseller",
    ),
    path(
        "topsellers/add",
        topseller_views.AddTopsellerView.as_view(),
        name="lfs_manage_add_topseller",
    ),
    path(
        "topsellers/update",
        topseller_views.RemoveTopsellerView.as_view(),
        name="lfs_manage_delete_topseller",
    ),
    path(
        "topsellers/sort",
        topseller_views.SortTopsellerView.as_view(),
        name="lfs_manage_sort_topseller",
    ),
]
