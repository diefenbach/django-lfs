# django imports
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.core.utils import get_default_shop
from lfs.customer.models import BankAccount
        
class AddressForm(forms.Form):
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
    shipping_email = forms.EmailField(label=_(u"Shipping E-mail"), required=False, max_length=50)
    
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        
        shop = get_default_shop()
        self.fields["invoice_country"].choices = [(c.iso, c.name) for c in shop.countries.all()]
        self.fields["shipping_country"].choices = [(c.iso, c.name) for c in shop.countries.all()]
        
class BankForm(forms.ModelForm):
    """Form to edit bank account
    """    
    class Meta:
        model = BankAccount
        exclude = ("customer", "email")

class EmailForm(forms.Form):
    """Form to edit email address
    """    
    email = forms.EmailField(label=_(u"E-mail"), max_length=50)

class RegisterForm(forms.Form):
    """Form to register a customer.
    """
    email = forms.EmailField(label=_(u"E-mail"), max_length=50)
    password_1 = forms.CharField(
        label=_(u"Password"), widget=forms.PasswordInput(), max_length=20)
    password_2 = forms.CharField(
        label=_(u"Confirm password"), widget=forms.PasswordInput(), max_length=20)

    def clean_password_2(self):
        """Validates that password 1 and password 2 are the same.
        """
        p1 = self.cleaned_data.get('password_1')
        p2 = self.cleaned_data.get('password_2')

        if not (p1 and p2 and p1 == p2):
            raise forms.ValidationError(_(u"The two passwords do not match."))

        return p2
    
    def clean_email(self):
        """Validates that the entered e-mail is unique.
        """
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError(
                _(u"That email address is already in use."))

        return email