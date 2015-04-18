# django imports
from django import forms
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.customer_tax.models import CustomerTax


class CustomerTaxForm(forms.ModelForm):
    """
    Form to add and edit a customer tax.
    """
    class Meta:
        model = CustomerTax
        exclude = ()
