from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^manufacturers/$", views.manufacturers, name="lfs_manufacturers"),
    re_path(r"^manufacturer-(?P<slug>[-\w]*)/$", views.manufacturer_view, name="lfs_manufacturer"),
]
