# django imports
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.customer.models import Address
from lfs.customer.models import BankAccount
from lfs.core.settings import ADDRESS_LOCALIZATION
from lfs.core.models import Country
from lfs.addresses.views import get_l10n

class AddressForm(forms.ModelForm):
    """Form to edit addresses.
    """
    class Meta:
        model = Address
        exclude = ("customer", "email")
        
    
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)        
        
        if ADDRESS_LOCALIZATION:
            # set correct country fields and labels
            initial_data = kwargs.get('initial', None) 
            if  initial_data is not None:
                country_id = initial_data.get(self.prefix + '-country', None)
                if  country_id is not None:
                    country = Country.objects.get(id=country_id)
                    self.set_address_fields(country.code)    
    
    def set_address_fields(self, country_code):
        l10n_obj = get_l10n(country_code)
        if l10n_obj is not None:
            self.change_address_fields(["company_name", "street", "zip_code", "city", "state"], 
                l10n_obj.get_address_fields())
            self.change_address_fields(['-phone'], l10n_obj.get_phone_fields())
            self.change_address_fields(['-email'], l10n_obj.get_email_fields())
            
    def change_address_fields(self, field_names,  fields):
        assert(len(field_names) == len(fields))
        i = 0
        for field in fields:
            if field is not None:      
                field_name = field_names[i]       
                if self.fields.get(field_name, None) is not None:
                    self.fields[field_name] = field                        
            i = i + 1
    
        
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