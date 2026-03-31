from django import forms
from django.utils.translation import gettext_lazy as _


class CustomerFilterForm(forms.Form):
    """Form for filtering customers."""

    name = forms.CharField(
        label=_("Name"),
        max_length=100,  # Keep reasonable limit for form validation
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-sm",
                "placeholder": _("Filter by name..."),
            }
        ),
    )

    start = forms.DateField(
        label=_("Start Date"),
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control form-control-sm dateinput",
                "placeholder": _("Select start date"),
            }
        ),
    )

    end = forms.DateField(
        label=_("End Date"),
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control form-control-sm dateinput",
                "placeholder": _("Select end date"),
            }
        ),
    )
