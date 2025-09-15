from django.urls import path
from . import views

urlpatterns = [
    path(
        "tools",
        views.ToolsView.as_view(),
        name="lfs_manage_tools",
    ),
    path(
        "clear-cache",
        views.clear_cache,
        name="lfs_clear_cache",
    ),
    path(
        "set-category-levels",
        views.set_category_levels,
        name="lfs_set_category_levels",
    ),
    path(
        "update-effective-price",
        views.update_effective_price,
        name="lfs_update_effective_price",
    ),
    path(
        "reindex-topseller",
        views.reindex_topseller,
        name="lfs_reindex_topseller",
    ),
]
