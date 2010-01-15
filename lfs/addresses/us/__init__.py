""" http://www.bitboost.com/ref/international-address-formats.html """
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.localflavor.us.forms import USPhoneNumberField, USStateField, USStateSelect, USZipCodeField

from lfs.addresses.forms import L10NAddress

class USL10NAddress(L10NAddress):
    
    def get_address_fields(self):
        return [forms.CharField(label=_(u"Company name"), required=False, max_length=50),
                forms.CharField(label=_(u"Street"), max_length=100),
                USZipCodeField(label=_(u"Zip Code")),
                forms.CharField(label=_(u"City"), max_length=50),
                USStateField(label=_(u"US State"), widget=USStateSelect),
               ]

    
    def get_phone_fields(self):
        return [USPhoneNumberField(label=_(u"Phone"))]