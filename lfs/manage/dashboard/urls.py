from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="lfs_manage_dashboard"),
]
