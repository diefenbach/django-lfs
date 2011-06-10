from django.conf.urls.defaults import patterns, url
from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView, InstanceModelView
from lfs.catalog.models import Product

class ProductResource(ModelResource):
    """
    A Rest representation of an LFS Product
    """
    model = Product
    #fields = ['active]

urlpatterns = patterns('',
    url(r'^products/$', ListOrCreateModelView.as_view(resource=ProductResource)),
    url(r'^product/(?P<pk>[^/]+)/$', InstanceModelView.as_view(resource=ProductResource)),
)