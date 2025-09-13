from django.urls import path
from . import views

urlpatterns = [
    path("add-criterion", views.add_criterion, name="lfs_add_criterion"),
    path("change-criterion", views.change_criterion_form, name="lfs_change_criterion_form"),
    path("delete-criterion", views.delete_criterion, name="lfs_delete_criterion"),
]
