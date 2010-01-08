""" from http://www.bitboost.com/ref/international-address-formats.html#Great-Britain"""
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.localflavor.uk.forms import UKPostcodeField, UKCountySelect

from lfs.addresses.forms import L10NAddress

class GBL10NAddress(L10NAddress):
    
    def get_address_fields(self):
        return [forms.CharField(label=_(u"Company name"), required=False, max_length=50),
                forms.CharField(label=_(u"Street"), max_length=50),
                forms.CharField(label=_(u"Town"), max_length=50),
                UKPostcodeField(label=_(u"Postcode")),
                forms.CharField(label=_(u"County"), widget=UKCountySelect, max_length=50),
           ]
