from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="lfs_manage_dashboard"), name="lfs_manage"),
    path("dashboard/", views.dashboard, name="lfs_manage_dashboard"),
]
