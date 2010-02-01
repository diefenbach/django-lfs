# python imports
from datetime import datetime

# django imports
from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.payment.settings import CREDIT_CARD_TYPE_CHOICES
from lfs.core.utils import get_default_shop

class OnePageCheckoutForm(forms.Form):
    """
    """
    invoice_firstname = forms.CharField(label=_(u"Invoice Firstname"), max_length=50)
    invoice_lastname = forms.CharField(label=_(u"Invoice Lastname"), max_length=50)
    invoice_line1 = forms.CharField(label=_(u"Invoice Address Line 1"), required=False, max_length=100)
    invoice_line2 = forms.CharField(label=_(u"Invoice Address Line 2"), required=False, max_length=100)
    invoice_line3 = forms.CharField(label=_(u"Invoice Address Line 3"), required=False, max_length=100)
    invoice_line4 = forms.CharField(label=_(u"Invoice Address Line 4"), required=False, max_length=100)
    invoice_line5 = forms.CharField(label=_(u"Invoice Address Line 5"), required=False, max_length=100)
    invoice_country = forms.ChoiceField(label=_(u"Country"), required=False)
    invoice_phone = forms.CharField(label=_(u"Invoice Phone"), max_length=20, required=False)
    invoice_email = forms.EmailField(label=_(u"Invoice E-mail"), required=False, max_length=50)
    
    shipping_firstname = forms.CharField(label=_(u"Shipping Firstname"), required=False, max_length=50)
    shipping_lastname = forms.CharField(label=_(u"Shipping Lastname"), required=False, max_length=50)
    shipping_line1 = forms.CharField(label=_(u"Shipping Address Line 1"), required=False, max_length=100)
    shipping_line2 = forms.CharField(label=_(u"Shipping Address Line 2"), required=False, max_length=100)
    shipping_line3 = forms.CharField(label=_(u"Shipping Address Line 3"), required=False, max_length=100)
    shipping_line4 = forms.CharField(label=_(u"Shipping Address Line 4"), required=False, max_length=100)
    shipping_line5 = forms.CharField(label=_(u"Shipping Address Line 5"), required=False, max_length=100)
    shipping_country = forms.ChoiceField(label=_(u"Country"), required=False)
    shipping_phone = forms.CharField(label=_(u"Shipping Phone"), required=False, max_length=20)

    account_number = forms.CharField(label=_(u"Account Number"), required=False, max_length=30)
    bank_identification_code = forms.CharField(label=_(u"Bank Indentification Code"), required=False, max_length=30)
    bank_name = forms.CharField(label=_(u"Bankname"), required=False, max_length=100)
    depositor = forms.CharField(label=_(u"Depositor"), required=False, max_length=100)
    
    payment_method = forms.CharField(required=False, max_length=1)
    
    credit_card_type = forms.ChoiceField(label=_(u"Credit Card Type"), choices=CREDIT_CARD_TYPE_CHOICES, required=False)
    credit_card_owner = forms.CharField(label=_(u"Credit Card Owner"), max_length=100, required=False)
    credit_card_number = forms.CharField(label=_(u"Credit Card Number"), max_length=30, required=False)
    credit_card_expiration_date_month = forms.ChoiceField(label=_(u"Expiration Date Month"), required=False)
    credit_card_expiration_date_year = forms.ChoiceField(label=_(u"Expiration Date Year"), required=False)
    credit_card_verification = forms.CharField(label=_(u"Verification Number"), max_length=4, required=False, widget=forms.TextInput(attrs={"size" : 4}))
    
    no_shipping = forms.BooleanField(label=_(u"Same as invoice"), initial=True, required=False)
    message = forms.CharField(label=_(u"Your message to us"), widget=forms.Textarea(attrs={'cols':'80;'}), required=False)

    def __init__(self, *args, **kwargs):
        super(OnePageCheckoutForm, self).__init__(*args, **kwargs)
        
        shop = get_default_shop()
        self.fields["invoice_country"].choices = [(c.iso, c.name) for c in shop.countries.all()]
        self.fields["shipping_country"].choices = [(c.iso, c.name) for c in shop.countries.all()]
        
        year = datetime.now().year
        self.fields["credit_card_expiration_date_month"].choices = [(i, i) for i in range(1, 13)]
        self.fields["credit_card_expiration_date_year"].choices = [(i, i) for i in range(year, year+10)]
        
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

            if self.cleaned_data.get("shipping_line1", "") == "":
                self._errors["shipping_line1"] = ErrorList([msg])

            if self.cleaned_data.get("shipping_line2", "") == "":
                self._errors["shipping_line2"] = ErrorList([msg])

            if self.cleaned_data.get("shipping_line3", "") == "":
                self._errors["shipping_line3"] = ErrorList([msg])
                
        # 1 == Direct Debit
        if self.data.get("payment_method") == "1":
            if self.cleaned_data.get("account_number", "") == "":
                self._errors["account_number"] = ErrorList([msg])
            
            if self.cleaned_data.get("bank_identification_code", "") == "":
                self._errors["bank_identification_code"] = ErrorList([msg])

            if self.cleaned_data.get("bank_name", "") == "":
                self._errors["bank_name"] = ErrorList([msg])

            if self.cleaned_data.get("depositor", "") == "":
                self._errors["depositor"] = ErrorList([msg])
        # 6 == Credit Card
        elif self.data.get("payment_method") == "6":
            if self.cleaned_data.get("credit_card_owner", "") == "":
                self._errors["credit_card_owner"] = ErrorList([msg])
            
            if self.cleaned_data.get("credit_card_number", "") == "":
                self._errors["credit_card_number"] = ErrorList([msg])
            
            if self.cleaned_data.get("credit_card_verification", "") == "":
                self._errors["credit_card_verification"] = ErrorList([msg])
        
        return self.cleaned_data