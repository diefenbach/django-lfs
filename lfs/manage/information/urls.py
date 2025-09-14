from django.urls import path
from . import views

urlpatterns = [
    path(
        "environment",
        views.EnvironmentView.as_view(),
        name="lfs_manage_environment",
    ),
]
