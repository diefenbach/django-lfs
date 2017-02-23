from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^page/(?P<slug>[-\w]*)/$', views.page_view, name="lfs_page_view"),
    url(r'^pages/$', views.pages_view, name="lfs_pages"),
    url(r'^popup/(?P<slug>[-\w]*)/$', views.popup_view, name="lfs_popup_view"),
]
