# django imports
from django import forms
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.voucher.models import VoucherGroup
from lfs.voucher.settings import KIND_OF_CHOICES

class VoucherGroupForm(forms.ModelForm):
    """Form to add a VoucherGroup.
    """
    class Meta:
        model = VoucherGroup
        fields = ("name", "position")

class VoucherForm(forms.Form):
    """Form to add a Voucher.
    """
    amount = forms.IntegerField(label=_(u"Amount"), required=True)
    value = forms.FloatField(label=_(u"Value"), required=True)
    start_date = forms.DateTimeField(label=_(u"Start date"), required=True)
    end_date = forms.DateTimeField(label=_(u"End date"), required=True)
    kind_of = forms.ChoiceField(label=_(u"Kind of"), choices=KIND_OF_CHOICES, required=True)
