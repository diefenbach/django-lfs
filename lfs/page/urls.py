from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^page/(?P<slug>[-\w]*)/$', views.page_view, name="lfs_page_view"),
    re_path(r'^pages/$', views.pages_view, name="lfs_pages"),
    re_path(r'^popup/(?P<slug>[-\w]*)/$', views.popup_view, name="lfs_popup_view"),
]
