from django import forms
from django.utils.translation import gettext_lazy as _


class CartFilterForm(forms.Form):
    """Form for filtering carts by date range."""

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
