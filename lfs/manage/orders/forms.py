from django import forms
from django.utils.translation import gettext_lazy as _
from lfs.order.settings import ORDER_STATES


class OrderFilterForm(forms.Form):
    """Form for filtering orders by various criteria."""

    name = forms.CharField(
        label=_("Customer Name"),
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control form-control-sm", "placeholder": _("Customer name")}),
    )

    state = forms.ChoiceField(
        label=_("Order State"),
        required=False,
        choices=[("", _("All States"))] + list(ORDER_STATES),
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )

    start = forms.DateField(
        label=_("Start Date"),
        required=False,
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-sm dateinput", "placeholder": _("Select start date")}
        ),
    )

    end = forms.DateField(
        label=_("End Date"),
        required=False,
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-sm dateinput", "placeholder": _("Select end date")}
        ),
    )
