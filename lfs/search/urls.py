from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^search/$', views.search, name="lfs_search"),
    url(r'^livesearch/$', views.livesearch, name="lfs_livesearch"),
]
