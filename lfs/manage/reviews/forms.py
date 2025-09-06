from django import forms
from django.utils.translation import gettext_lazy as _


class ReviewFilterForm(forms.Form):
    """Form for filtering reviews."""

    name = forms.CharField(
        label=_("Name"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control form-control-sm", "placeholder": _("Filter by name...")}),
    )

    active = forms.ChoiceField(
        label=_("Active"),
        choices=[
            ("", _("All")),
            ("1", _("Yes")),
            ("0", _("No")),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )


class ReviewStateForm(forms.Form):
    """Form for changing review state."""

    active = forms.ChoiceField(
        label=_("Active"),
        choices=[
            ("1", _("Yes")),
            ("0", _("No")),
        ],
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
