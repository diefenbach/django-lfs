from django.contrib import admin

from lfs.shipping.models import ShippingMethod
from lfs.shipping.models import ShippingMethodPrice


class ShippingMethodAdmin(admin.ModelAdmin):
    pass


class ShippingMethodPriceAdmin(admin.ModelAdmin):
    pass


admin.site.register(ShippingMethodPrice, ShippingMethodPriceAdmin)
admin.site.register(ShippingMethod, ShippingMethodAdmin)
