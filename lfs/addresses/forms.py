from django import forms
from django.utils.translation import ugettext_lazy as _

"""
from lfs.addresses.models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ("email")
"""

class L10NAddress():
    """ The default address format """

    def get_address_fields(self):
        """ We are making the assumption that all countries will supply 5 address fields
        """
        
        return [forms.CharField(label=_(u"Company name"), required=False, max_length=50),
                forms.CharField(label=_(u"Street"), max_length=100),
                forms.CharField(label=_(u"Zip Code"), max_length=10),
                forms.CharField(label=_(u"City"), max_length=50),
                forms.CharField(label=_(u"State"), max_length=50),
               ]
        
    def get_phone_fields(self):
        return [forms.CharField(label=_(u"Phone"), max_length=20)]
    
    def get_email_fields(self):
        return [forms.EmailField(label=_(u"E-mail"), required=False, max_length=50)]
