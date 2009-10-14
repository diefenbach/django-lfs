# django imports
from django.contrib.admin import widgets
from django.forms import ModelForm

# lfs imports
from lfs.voucher.models import VoucherGroup

class VoucherGroupForm(ModelForm):
    """Form to add a VoucherGroup.
    """
    class Meta:
        model = VoucherGroup
        fields = ("name", "position")