# django imports
from django.contrib import admin
from lfs.addresses.models import Address


class AddressAdmin(admin.ModelAdmin):
    search_fields = ('firstname', 'lastname', 'customer__user__email')
    list_display = ('firstname', 'lastname', 'customer', 'order')
admin.site.register(Address, AddressAdmin)
