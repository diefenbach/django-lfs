# django imports
from django.contrib import admin

# lfs imports
from lfs.supplier.models import Supplier


class SupplierAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(Supplier, SupplierAdmin)
