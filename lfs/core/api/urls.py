from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from handlers import ProductHandler


product_resource = Resource(handler=ProductHandler)
urlpatterns = patterns('',
    url(r'^products/(?P<product_slug>[^/]+)/$', product_resource),
    )