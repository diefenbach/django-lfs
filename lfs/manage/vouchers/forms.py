from django import forms
from django.utils.translation import gettext_lazy as _

from lfs.tax.models import Tax
from lfs.voucher.models import VoucherGroup
from lfs.voucher.models import VoucherOptions
from lfs.voucher.settings import KIND_OF_CHOICES


# Forms
class VoucherOptionsForm(forms.ModelForm):
    """Form to manage voucher options."""

    class Meta:
        model = VoucherOptions
        exclude = ()


class VoucherGroupAddForm(forms.ModelForm):
    """Form to add a VoucherGroup."""

    class Meta:
        model = VoucherGroup
        fields = ("name",)


class VoucherGroupForm(forms.ModelForm):
    """Form to add a VoucherGroup."""

    class Meta:
        model = VoucherGroup
        fields = ("name", "position")


class VoucherForm(forms.Form):
    """Form to add a Voucher."""

    amount = forms.IntegerField(label=_("Amount"), required=True, help_text=_("Number of vouchers to create"))
    value = forms.FloatField(label=_("Value"), required=True)
    start_date = forms.DateField(label=_("Start date"), required=True)
    end_date = forms.DateField(label=_("End date"), required=True)
    kind_of = forms.ChoiceField(label=_("Kind of"), choices=KIND_OF_CHOICES, required=True)
    effective_from = forms.FloatField(
        label=_("Effective from"), required=True, help_text=_("Minimum cart price from which the vouchers are valid")
    )
    tax = forms.ChoiceField(label=_("Tax"), required=False)
    limit = forms.IntegerField(
        label=_("Limit"), initial=1, required=True, help_text=_("How many times voucher can be used")
    )
    sums_up = forms.BooleanField(
        label=_("Sums up"),
        initial=True,
        required=False,
        help_text=_("Determines if voucher can be summed up with other discounts"),
    )

    def __init__(self, *args, **kwargs):
        super(VoucherForm, self).__init__(*args, **kwargs)

        taxes = [["", "---"]]
        taxes.extend([(t.id, t.rate) for t in Tax.objects.all()])
        self.fields["tax"].choices = taxes
        self.fields["start_date"].widget.attrs = {"class": "date-picker"}
        self.fields["end_date"].widget.attrs = {"class": "date-picker"}
