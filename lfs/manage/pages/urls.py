from django.urls import re_path
import lfs.manage.pages.views

urlpatterns = [
    re_path(r"^add-page$", lfs.manage.pages.views.PageCreateView.as_view(), name="lfs_add_page"),
    re_path(r"^delete-page/(?P<id>\d*)$", lfs.manage.pages.views.PageDeleteView.as_view(), name="lfs_delete_page"),
    re_path(
        r"^delete-page-confirm/(?P<id>\d*)$",
        lfs.manage.pages.views.PageDeleteConfirmView.as_view(),
        name="lfs_delete_page_confirm",
    ),
    re_path(r"^manage-pages$", lfs.manage.pages.views.ManagePagesView.as_view(), name="lfs_manage_pages"),
    re_path(r"^manage-page/(?P<id>\d*)$", lfs.manage.pages.views.PageDataView.as_view(), name="lfs_manage_page"),
    re_path(r"^manage-page-seo/(?P<id>\d*)$", lfs.manage.pages.views.PageSEOView.as_view(), name="lfs_manage_page_seo"),
    re_path(
        r"^manage-page-portlets/(?P<id>\d*)$",
        lfs.manage.pages.views.PagePortletsView.as_view(),
        name="lfs_manage_page_portlets",
    ),
    re_path(r"^page-by-id/(?P<id>\d*)$", lfs.manage.pages.views.PageViewByIDView.as_view(), name="lfs_page_view_by_id"),
]
