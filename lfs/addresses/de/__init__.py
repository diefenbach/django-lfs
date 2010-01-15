""" from http://www.bitboost.com/ref/international-address-formats.html#Great-Britain"""
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.localflavor.de.forms import DEZipCodeField, DEStateSelect

from lfs.addresses.forms import L10NAddress

class DEL10NAddress(L10NAddress):
    
    def get_address_fields(self):
        return [forms.CharField(label=_(u"Company name"), required=False, max_length=50),
                forms.CharField(label=_(u"Street"), max_length=100),
                DEZipCodeField(label=_(u"Zip Code")),
                forms.CharField(label=_(u"City"), max_length=50),
                forms.CharField(label=_(u"State"), widget=DEStateSelect),
               ]
