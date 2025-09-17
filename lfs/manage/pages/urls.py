import lfs.manage.pages.views

from django.urls import path

urlpatterns = [
    path(
        "add-page",
        lfs.manage.pages.views.PageCreateView.as_view(),
        name="lfs_add_page",
    ),
    path(
        "page/<int:id>/delete",
        lfs.manage.pages.views.PageDeleteView.as_view(),
        name="lfs_delete_page",
    ),
    path(
        "page/<int:id>/delete-confirm",
        lfs.manage.pages.views.PageDeleteConfirmView.as_view(),
        name="lfs_delete_page_confirm",
    ),
    path(
        "pages",
        lfs.manage.pages.views.ManagePagesView.as_view(),
        name="lfs_manage_pages",
    ),
    path(
        "page/<int:id>/data",
        lfs.manage.pages.views.PageDataView.as_view(),
        name="lfs_manage_page",
    ),
    path(
        "page/<int:id>/seo",
        lfs.manage.pages.views.PageSEOView.as_view(),
        name="lfs_manage_page_seo",
    ),
    path(
        "page/<int:id>/portlets",
        lfs.manage.pages.views.PagePortletsView.as_view(),
        name="lfs_manage_page_portlets",
    ),
    path(
        "page/<int:id>/view-by-id",
        lfs.manage.pages.views.PageViewByIDView.as_view(),
        name="lfs_page_view_by_id",
    ),
]
