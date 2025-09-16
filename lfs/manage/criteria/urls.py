from django.urls import path
from . import views

urlpatterns = [
    path("add-criterion", views.AddCriterionView.as_view(), name="lfs_manage_add_criterion"),
    path("change-criterion", views.ChangeCriterionFormView.as_view(), name="lfs_manage_change_criterion_form"),
    path("delete-criterion", views.DeleteCriterionView.as_view(), name="lfs_manage_delete_criterion"),
]
