from django import forms
from django.utils.translation import gettext_lazy as _

from lfs.order.settings import ORDER_STATES
from lfs.payment.models import PaymentMethod


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

    payment_method = forms.ChoiceField(
        label=_("Payment Method"),
        required=False,
        choices=[],
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )

    start = forms.DateField(
        label=_("Start Date"),
        required=False,
        input_formats=["%d.%m.%Y", "%Y-%m-%d"],
        widget=forms.DateInput(
            format="%d.%m.%Y",
            attrs={"class": "form-control form-control-sm dateinput", "placeholder": _("Select start date")},
        ),
    )

    end = forms.DateField(
        label=_("End Date"),
        required=False,
        input_formats=["%d.%m.%Y", "%Y-%m-%d"],
        widget=forms.DateInput(
            format="%d.%m.%Y",
            attrs={"class": "form-control form-control-sm dateinput", "placeholder": _("Select end date")},
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [("", _("All Payment Methods"))]
        for pm in PaymentMethod.objects.all().order_by("name"):
            choices.append((str(pm.id), pm.name))
        self.fields["payment_method"].choices = choices
