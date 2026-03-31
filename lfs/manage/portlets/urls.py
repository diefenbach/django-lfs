from django.urls import path
from lfs.manage.portlets import views as lfs_portlets

urlpatterns = [
    path(
        "portlets/add/<int:object_type_id>/<int:object_id>",
        lfs_portlets.AddPortletView.as_view(),
        name="lfs_add_portlet",
    ),
    path(
        "portlets/update/<int:object_type_id>/<int:object_id>",
        lfs_portlets.UpdatePortletsView.as_view(),
        name="lfs_update_portlets",
    ),
    path(
        "portlets/delete/<int:portletassignment_id>",
        lfs_portlets.DeletePortletView.as_view(),
        name="lfs_delete_portlet",
    ),
    path(
        "portlets/edit/<int:portletassignment_id>",
        lfs_portlets.EditPortletView.as_view(),
        name="lfs_edit_portlet",
    ),
    path(
        "portlets/move-portlet/<int:portletassignment_id>",
        lfs_portlets.MovePortletView.as_view(),
        name="lfs_move_portlet",
    ),
    path(
        "portlets/sort",
        lfs_portlets.SortPortletsView.as_view(),
        name="lfs_sort_portlets",
    ),
]
