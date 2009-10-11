# django imports
from django.contrib import admin

# lfs imports
from lfs.customer.models import Customer
from lfs.customer.models import Address

class CustomerAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(Customer, CustomerAdmin)

class AddressAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(Address, AddressAdmin)
