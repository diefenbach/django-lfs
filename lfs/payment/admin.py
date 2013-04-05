# django imports
from django.contrib import admin

# lfs imports
from lfs.payment.models import PaymentMethod
from lfs.payment.models import PaymentMethodPrice
from lfs.payment.models import PaymentMethodDelivery


class PaymentMethodAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(PaymentMethod, PaymentMethodAdmin)


class PaymentMethodPriceAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(PaymentMethodPrice, PaymentMethodPriceAdmin)


class PaymentMethodDeliveryAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(PaymentMethodDelivery, PaymentMethodDeliveryAdmin)
