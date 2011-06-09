from piston.handler import BaseHandler
from lfs.catalog.models import Product

class ProductHandler(BaseHandler):
    allowed_methods = ('GET', )
    model = Product