from django import forms
from lfs.customer_tax.models import CustomerTax


class CustomerTaxForm(forms.ModelForm):
    """
    Form to add and edit a customer tax.
    """
    class Meta:
        model = CustomerTax
        exclude = ()
