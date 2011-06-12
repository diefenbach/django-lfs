# django imports
from django.contrib import admin

# lfs imports
from lfs.shipping.models import ShippingMethod
from lfs.shipping.models import ShippingMethodPrice


class ShippingMethodAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(ShippingMethod, ShippingMethodAdmin)


class ShippingMethodPriceAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(ShippingMethodPrice, ShippingMethodPriceAdmin)
