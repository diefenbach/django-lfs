# django imports
from django.forms import ModelForm

# lfs imports
from lfs.discounts.models import Discount


class DiscountForm(ModelForm):
    """
    Form to manage discount data.
    """
    class Meta:
        model = Discount
        fields = ('name', 'active', 'value', 'type', 'tax', 'sku', 'sums_up')
