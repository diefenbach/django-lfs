"""
# django imports
from django.contrib import admin

# lfs imports
from lfs.addresses.models import Address

class AddressAdmin(admin.ModelAdmin):
    pass
   
admin.site.register(Address, AddressAdmin)
"""