from django.contrib import admin
from lfs.catalog.models import Product
from lfs.catalog.models import StaticBlock

admin.site.register(Product)
admin.site.register(StaticBlock)
