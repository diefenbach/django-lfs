from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class CartFilterForm(forms.Form):
    """Form for filtering carts by date range."""

    start = forms.DateField(
        label=_("Start Date"),
        required=False,
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-sm dateinput", "placeholder": _("Select start date")}
        ),
        input_formats=getattr(settings, "DATE_INPUT_FORMATS", ["%Y-%m-%d"]),
    )
    end = forms.DateField(
        label=_("End Date"),
        required=False,
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-sm dateinput", "placeholder": _("Select end date")}
        ),
        input_formats=getattr(settings, "DATE_INPUT_FORMATS", ["%Y-%m-%d"]),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Set initial values from session if available
        if hasattr(self, "initial") and self.initial:
            self.fields["start"].initial = self.initial.get("start")
            self.fields["end"].initial = self.initial.get("end")
