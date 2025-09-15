from django.urls import path
import lfs.manage.actions.views

urlpatterns = [
    path(
        "actions/",
        lfs.manage.actions.views.manage_actions,
        name="lfs_manage_actions",
    ),
    path(
        "action/<int:pk>/",
        lfs.manage.actions.views.ActionUpdateView.as_view(),
        name="lfs_manage_action",
    ),
    path(
        "action/add",
        lfs.manage.actions.views.ActionCreateView.as_view(),
        name="lfs_manage_add_action",
    ),
    path(
        "action/<int:pk>/delete-confirm",
        lfs.manage.actions.views.ActionDeleteConfirmView.as_view(),
        name="lfs_manage_delete_action_confirm",
    ),
    path(
        "action/<int:pk>/delete",
        lfs.manage.actions.views.ActionDeleteView.as_view(),
        name="lfs_manage_delete_action",
    ),
    path(
        "actions/no",
        lfs.manage.actions.views.NoActionsView.as_view(),
        name="lfs_manage_no_actions",
    ),
    path(
        "actions/sort",
        lfs.manage.actions.views.sort_actions,
        name="lfs_manage_sort_actions",
    ),
]
