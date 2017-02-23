from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^manufacturers/$', views.manufacturers, name="lfs_manufacturers"),
    url(r'^manufacturer-(?P<slug>[-\w]*)/$', views.manufacturer_view, name="lfs_manufacturer"),
]
