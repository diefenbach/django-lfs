# django imports
from django.forms import ModelForm

# lfs imports
from lfs.core.widgets.image import LFSImageInput
from lfs.shipping.models import ShippingMethod


class ShippingMethodForm(ModelForm):
    """Form to edit a shipping method."""

    def __init__(self, *args, **kwargs):
        super(ShippingMethodForm, self).__init__(*args, **kwargs)
        self.fields["image"].widget = LFSImageInput()

    class Meta:
        model = ShippingMethod
        exclude = ("deletable", "priority")


class ShippingMethodAddForm(ModelForm):
    """Form to add a shipping method."""

    class Meta:
        model = ShippingMethod
        fields = ("name",)
