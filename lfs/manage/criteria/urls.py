from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^add-criterion$", views.add_criterion, name="lfs_add_criterion"),
    re_path(r"^change-criterion$", views.change_criterion_form, name="lfs_change_criterion_form"),
    re_path(r"^delete-criterion$", views.delete_criterion, name="lfs_delete_criterion"),
]
