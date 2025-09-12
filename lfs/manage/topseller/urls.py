from django.urls import path
from lfs.manage.topseller import views as topseller_views

urlpatterns = [
    path(
        "topseller",
        topseller_views.ManageTopsellerView.as_view(),
        name="lfs_manage_topseller",
    ),
    path(
        "topseller/add",
        topseller_views.AddTopsellerView.as_view(),
        name="lfs_manage_add_topseller",
    ),
    path(
        "topseller/update",
        topseller_views.RemoveTopsellerView.as_view(),
        name="lfs_manage_delete_topseller",
    ),
    path(
        "topseller/sort",
        topseller_views.SortTopsellerView.as_view(),
        name="lfs_manage_sort_topseller",
    ),
]
