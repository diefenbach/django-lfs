# python imports
from datetime import datetime

# django imports
from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.payment.settings
from lfs.payment.models import PaymentMethod
from lfs.core.utils import get_default_shop
from lfs.core.models import Country


class OnePageCheckoutForm(forms.Form):
    """
    """
    invoice_firstname = forms.CharField(label=_(u"First Name"), max_length=50)
    invoice_lastname = forms.CharField(label=_(u"Last Name"), max_length=50)
    invoice_phone = forms.CharField(label=_(u"Invoice Phone"), max_length=20, required=False)
    invoice_email = forms.EmailField(label=_(u"Invoice E-mail"), required=False, max_length=50)

    shipping_firstname = forms.CharField(label=_(u"First Name"), required=False, max_length=50)
    shipping_lastname = forms.CharField(label=_(u"Last Name"), required=False, max_length=50)
    shipping_phone = forms.CharField(label=_(u"Shipping Phone"), required=False, max_length=20)
    shipping_email = forms.EmailField(label=_(u"Shipping E-mail"), required=False, max_length=50)

    requested_delivery_date = forms.DateField(label=_(u"Requested Delivery Date"), required=False)

    account_number = forms.CharField(label=_(u"Account Number"), required=False, max_length=30)
    bank_identification_code = forms.CharField(label=_(u"Bank Indentification Code"), required=False, max_length=30)
    bank_name = forms.CharField(label=_(u"Bankname"), required=False, max_length=100)
    depositor = forms.CharField(label=_(u"Depositor"), required=False, max_length=100)

    payment_method = forms.CharField(required=False, max_length=1)

    credit_card_type = forms.ChoiceField(label=_(u"Credit Card Type"), choices=lfs.payment.settings.CREDIT_CARD_TYPE_CHOICES, required=False)
    credit_card_owner = forms.CharField(label=_(u"Credit Card Owner"), max_length=100, required=False)
    credit_card_number = forms.CharField(label=_(u"Credit Card Number"), max_length=30, required=False)
    credit_card_expiration_date_month = forms.ChoiceField(label=_(u"Expiration Date Month"), required=False)
    credit_card_expiration_date_year = forms.ChoiceField(label=_(u"Expiration Date Year"), required=False)
    credit_card_verification = forms.CharField(label=_(u"Verification Number"), max_length=4, required=False, widget=forms.TextInput(attrs={"size": 4}))

    no_shipping = forms.BooleanField(label=_(u"Same as invoice"), initial=True, required=False)
    message = forms.CharField(label=_(u"Your message to us"), widget=forms.Textarea(attrs={'cols': '80'}), required=False)

    def __init__(self, *args, **kwargs):
        super(OnePageCheckoutForm, self).__init__(*args, **kwargs)

        year = datetime.now().year
        self.fields["credit_card_expiration_date_month"].choices = [(i, i) for i in range(1, 13)]
        self.fields["credit_card_expiration_date_year"].choices = [(i, i) for i in range(year, year + 10)]

    def clean(self):
        """
        """
        msg = _(u"This field is required.")

        if self.data.get("is_anonymous") == "1" and \
           not self.cleaned_data.get("invoice_email"):
            self._errors["invoice_email"] = ErrorList([msg])

        if not self.cleaned_data.get("no_shipping"):
            if self.cleaned_data.get("shipping_firstname", "") == "":
                self._errors["shipping_firstname"] = ErrorList([msg])

            if self.cleaned_data.get("shipping_lastname", "") == "":
                self._errors["shipping_lastname"] = ErrorList([msg])

        # check that shipping country is in the shops shipping countries list
        shop = get_default_shop()
        shipping_countries = shop.shipping_countries.all()
        shipping_country = None
        if not self.cleaned_data.get("no_shipping"):
            shipping_country_code = self.data.get("shipping-country", None)
            if shipping_country_code:
                shipping_country = Country.objects.get(code=shipping_country_code.lower())
        else:
            shipping_country_code = self.data.get("invoice-country", None)
            if shipping_country_code:
                shipping_country = Country.objects.get(code=shipping_country_code.lower())
        if shipping_country:
            if shipping_country not in shipping_countries:
                msg = _(u"Invalid shipping country.")
                #self._errors["all"] = ErrorList([msg])
                raise forms.ValidationError("Invalid Shipping Country")

        # Check data of selected payment method
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

        elif payment_method.type == lfs.payment.settings.PM_CREDIT_CARD:
            if self.cleaned_data.get("credit_card_owner", "") == "":
                self._errors["credit_card_owner"] = ErrorList([msg])

            if self.cleaned_data.get("credit_card_number", "") == "":
                self._errors["credit_card_number"] = ErrorList([msg])

            if self.cleaned_data.get("credit_card_verification", "") == "":
                self._errors["credit_card_verification"] = ErrorList([msg])

        return self.cleaned_data
