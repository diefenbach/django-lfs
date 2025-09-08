from django.urls import re_path
from lfs.manage.portlets import views as lfs_portlets

urlpatterns = [
    # Portlets
    re_path(
        r"^add-portlet/(?P<object_type_id>\d+)/(?P<object_id>\d+)$",
        lfs_portlets.AddPortletView.as_view(),
        name="lfs_add_portlet",
    ),
    re_path(
        r"^update-portlets/(?P<object_type_id>\d+)/(?P<object_id>\d+)$",
        lfs_portlets.UpdatePortletsView.as_view(),
        name="lfs_update_portlets",
    ),
    re_path(
        r"^delete-portlet/(?P<portletassignment_id>\d+)$",
        lfs_portlets.DeletePortletView.as_view(),
        name="lfs_delete_portlet",
    ),
    re_path(
        r"^edit-portlet/(?P<portletassignment_id>\d+)$", lfs_portlets.EditPortletView.as_view(), name="lfs_edit_portlet"
    ),
    re_path(
        r"^move-portlet/(?P<portletassignment_id>\d+)$", lfs_portlets.MovePortletView.as_view(), name="lfs_move_portlet"
    ),
    re_path(r"^sort-portlets$", lfs_portlets.SortPortletsView.as_view(), name="lfs_sort_portlets"),
]
