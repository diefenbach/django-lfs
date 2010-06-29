# django imports
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.customer.models import Address
from lfs.customer.models import BankAccount

class AddressForm(forms.ModelForm):
    """Form to edit addresses.
    """
    class Meta:
        model = Address
        exclude = ("customer", "email")
        
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
        if email and User.objects.filter(Q(email=email) | Q(username=email)).count() > 0:
            raise forms.ValidationError(
                _(u"That email address is already in use."))

        return email