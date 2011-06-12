from django.conf.urls.defaults import patterns, url
from djangorestframework.views import ListOrCreateModelView, InstanceModelView
from handlers import ProductResource

urlpatterns = patterns('',
    url(r'^products/$', ListOrCreateModelView.as_view(resource=ProductResource)),
    url(r'^product/(?P<pk>[^/]+)/$', InstanceModelView.as_view(resource=ProductResource)),
)
