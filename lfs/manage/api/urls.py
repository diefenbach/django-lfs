from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView, InstanceModelView
from handlers import CategorySortView

urlpatterns = patterns('',
    url(r'^categories/sort/$', login_required(CategorySortView.as_view()), name="lfs-sort-categories"),
)