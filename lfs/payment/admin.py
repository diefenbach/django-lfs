# django imports
from django.contrib import admin

# lfs imports
from lfs.payment.models import PaymentMethod
from lfs.payment.models import PaymentMethodPrice


class PaymentMethodAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(PaymentMethod, PaymentMethodAdmin)


class PaymentMethodPriceAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(PaymentMethodPrice, PaymentMethodPriceAdmin)
