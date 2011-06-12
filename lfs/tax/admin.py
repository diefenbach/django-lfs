# django imports
from django.contrib import admin

# lfs imports
from lfs.tax.models import Tax


# Taxes
class TaxAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(Tax, TaxAdmin)
