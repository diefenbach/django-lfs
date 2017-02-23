from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^test/$', views.test),
    url(r'^upload-test/$', views.upload_test),
]
