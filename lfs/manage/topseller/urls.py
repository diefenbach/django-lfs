from django.urls import path, re_path
import lfs.manage.topseller.views

urlpatterns = [
    path(
        "topseller",
        lfs.manage.topseller.views.ManageTopsellerView.as_view(),
        name="lfs_manage_topseller",
    ),
    path(
        "add-topseller",
        lfs.manage.topseller.views.add_topseller,
        name="lfs_manage_add_topseller",
    ),
    path(
        "update-topseller",
        lfs.manage.topseller.views.update_topseller,
        name="lfs_manage_update_topseller",
    ),
    path(
        "sort-topseller",
        lfs.manage.topseller.views.sort_topseller,
        name="lfs_manage_sort_topseller",
    ),
    re_path(
        r"^topseller-inline$",
        lfs.manage.topseller.views.manage_topseller_inline,
        name="lfs_manage_topseller_inline",
    ),
]
