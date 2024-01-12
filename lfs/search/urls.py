from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^search/$", views.search, name="lfs_search"),
    re_path(r"^livesearch/$", views.livesearch, name="lfs_livesearch"),
]
