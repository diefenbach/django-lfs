from lfs.catalog.models import Product

from djangorestframework.resources import ModelResource


class ProductResource(ModelResource):
    """
    A Rest representation of an LFS Product
    """
    model = Product
    #fields = ['active]
