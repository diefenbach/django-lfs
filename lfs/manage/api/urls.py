from django.conf.urls.defaults import patterns, url
from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView, InstanceModelView
from handlers import CategorySortView

urlpatterns = patterns('',
    url(r'^categories/sort/$', CategorySortView.as_view(), name="lfs-sort-categories"),
)
