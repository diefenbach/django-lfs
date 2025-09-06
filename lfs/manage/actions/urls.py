from django.urls import path
import lfs.manage.actions.views

urlpatterns = [
    path("actions/", lfs.manage.actions.views.manage_actions, name="lfs_manage_actions"),
    path("action/<int:pk>/", lfs.manage.actions.views.ActionUpdateView.as_view(), name="lfs_manage_action"),
    path("add-action/", lfs.manage.actions.views.ActionCreateView.as_view(), name="lfs_add_action"),
    path(
        "delete-action-confirm/<int:pk>/",
        lfs.manage.actions.views.ActionDeleteConfirmView.as_view(),
        name="lfs_manage_delete_action_confirm",
    ),
    path("delete-action/<int:pk>/", lfs.manage.actions.views.ActionDeleteView.as_view(), name="lfs_delete_action"),
    path("no-actions/", lfs.manage.actions.views.NoActionsView.as_view(), name="lfs_no_actions"),
    path("sort-actions/", lfs.manage.actions.views.sort_actions, name="lfs_sort_actions"),
]
