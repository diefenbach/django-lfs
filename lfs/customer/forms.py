import time

from django import forms
from django.core import signing
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms.utils import ErrorList
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import lfs.payment.settings
from lfs.customer.models import BankAccount
from lfs.customer.models import CreditCard
from lfs.payment.models import PaymentMethod


class BankAccountForm(forms.ModelForm):
    """
    The default bank account form which is displayed within the checkout form
    if a shop customer selects a payment method of type ``bank``.
    """

    class Meta:
        model = BankAccount
        exclude = ("customer",)

    def clean(self):
        msg = _("This field is required.")

        payment_method_id = self.data.get("payment_method")
        payment_method = PaymentMethod.objects.get(pk=payment_method_id)

        if payment_method.type == lfs.payment.settings.PM_BANK:
            if self.cleaned_data.get("account_number", "") == "":
                self._errors["account_number"] = ErrorList([msg])

            if self.cleaned_data.get("bank_identification_code", "") == "":
                self._errors["bank_identification_code"] = ErrorList([msg])

            if self.cleaned_data.get("bank_name", "") == "":
                self._errors["bank_name"] = ErrorList([msg])

            if self.cleaned_data.get("depositor", "") == "":
                self._errors["depositor"] = ErrorList([msg])

        return self.cleaned_data


class CreditCardForm(forms.ModelForm):
    """
    The default credit card form which is displayed within the checkout form
    if a shop customer selects a payment method of type ``credit card``.
    """

    verification = forms.CharField(
        label=_("Verification Number"), max_length=4, required=False, widget=forms.TextInput(attrs={"size": 4})
    )

    class Meta:
        model = CreditCard
        exclude = ("customer",)

    def __init__(self, *args, **kwargs):
        super(CreditCardForm, self).__init__(*args, **kwargs)

        year = timezone.now().year
        self.fields["type"].widget = forms.Select(choices=lfs.payment.settings.CREDIT_CARD_TYPE_CHOICES)
        self.fields["expiration_date_month"].widget = forms.Select(choices=[(i, i) for i in range(1, 13)])
        self.fields["expiration_date_year"].widget = forms.Select(choices=[(i, i) for i in range(year, year + 10)])

    def clean(self):
        msg = _("This field is required.")

        # Check data of selected payment method
        payment_method_id = self.data.get("payment_method")
        payment_method = PaymentMethod.objects.get(pk=payment_method_id)

        if payment_method.type == lfs.payment.settings.PM_CREDIT_CARD:
            if self.cleaned_data.get("owner", "") == "":
                self._errors["owner"] = ErrorList([msg])

            if self.cleaned_data.get("number", "") == "":
                self._errors["number"] = ErrorList([msg])

            if self.cleaned_data.get("verification", "") == "":
                self._errors["verification"] = ErrorList([msg])

        return self.cleaned_data


class EmailForm(forms.Form):
    """Form to edit email address"""

    email = forms.EmailField(label=_("E-mail"), max_length=75)


class CustomerAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_("E-mail"), max_length=75)


# A person needs at least this long to fill in the registration form; bots are faster.
REGISTER_MIN_SECONDS = 3
_FORM_START_SALT = "lfs.customer.register-form-start"


def sign_form_start(timestamp: float) -> str:
    """Return ``timestamp`` (seconds since the epoch) signed, to be sent with the registration form."""
    return signing.dumps(timestamp, salt=_FORM_START_SALT)


class RegisterForm(forms.Form):
    """Form to register a customer.

    Instead of a captcha it keeps bots out with a honeypot field ``website``, which is hidden from people and stays
    empty, and a signed start time ``started``: a form sent back sooner than ``REGISTER_MIN_SECONDS`` after it was
    shown, or without a valid start time, is refused.
    """

    email = forms.EmailField(label=_("E-mail"), max_length=75)
    password_1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(), max_length=20)
    password_2 = forms.CharField(label=_("Confirm password"), widget=forms.PasswordInput(), max_length=20)
    website = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "tabindex": "-1",
                "aria-hidden": "true",
                "style": "position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden",
            }
        ),
    )
    started = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.initial["started"] = sign_form_start(time.time())

    def clean(self) -> dict:
        """Refuses the registration of bots: honeypot filled, start time missing, forged or too recent."""
        cleaned_data = super().clean()
        refused = forms.ValidationError(_("Your registration could not be processed. Please try again."))
        if cleaned_data.get("website"):
            raise refused
        try:
            started = signing.loads(cleaned_data.get("started") or "", salt=_FORM_START_SALT)
        except signing.BadSignature:
            raise refused
        if time.time() - float(started) < REGISTER_MIN_SECONDS:
            raise refused
        return cleaned_data

    def clean_password_2(self):
        """Validates that password 1 and password 2 are the same."""
        p1 = self.cleaned_data.get("password_1")
        p2 = self.cleaned_data.get("password_2")

        if not (p1 and p2 and p1 == p2):
            raise forms.ValidationError(_("The two passwords do not match."))

        return p2

    def clean_email(self):
        """Validates that the entered e-mail is unique."""
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(Q(email=email) | Q(username=email)).count() > 0:
            raise forms.ValidationError(_("That email address is already in use."))

        return email
