from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="lfs_manage_dashboard"),
]
