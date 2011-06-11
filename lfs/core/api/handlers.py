from piston.handler import BaseHandler
from lfs.catalog.models import Product, Category


class ProductHandler(BaseHandler):
    allowed_methods = ('GET', )
    model = Product


class CategoryHandler(BaseHandler):
    allowed_methods = ('GET', )
    model = Category
