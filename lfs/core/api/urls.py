from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from handlers import ProductHandler, CategoryHandler


product_resource = Resource(handler=ProductHandler)
category_resource = Resource(handler=CategoryHandler)

urlpatterns = patterns('',
    url(r'^products/$', product_resource),
    url(r'^product/(?P<product_slug>[^/]+)/$', product_resource),
    url(r'^categories/$', category_resource),
    url(r'^category/(?P<product_slug>[^/]+)/$', category_resource),
    )