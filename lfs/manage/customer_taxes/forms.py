# django imports
from django.forms import ModelForm

# lfs imports
from lfs.customer_tax.models import CustomerTax


class CustomerTaxForm(ModelForm):
    """
    Form to manage customer tax data.
    """

    class Meta:
        model = CustomerTax
        fields = ("rate", "description")
