# django imports
from django.forms import ModelForm

# lfs imports
from lfs.core.widgets.image import LFSImageInput
from lfs.payment.models import PaymentMethod


class PaymentMethodForm(ModelForm):
    """Form to edit a payment method."""

    def __init__(self, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        self.fields["image"].widget = LFSImageInput()

    class Meta:
        model = PaymentMethod
        exclude = ("deletable", "priority")


class PaymentMethodAddForm(ModelForm):
    """Form to add a payment method."""

    class Meta:
        model = PaymentMethod
        fields = ("name",)
