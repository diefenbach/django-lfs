""" from http://homepages.iol.ie/~discover/mail.htm"""
from django import forms
from django.utils.translation import ugettext_lazy as _

from lfs.addresses.forms import L10NAddress

try:
    from django.contrib.localflavor.ie.forms import IECountySelect# only available in django 1.2 and later
except ImportError, e:
    from django.forms.fields import Select
    IE_COUNTY_CHOICES = (
    ('antrim', _('Antrim')),
    ('armagh', _('Armagh')),
    ('carlow', _('Carlow')),
    ('cavan', _('Cavan')),
    ('clare', _('Clare')),
    ('cork', _('Cork')),
    ('derry', _('Derry')),
    ('donegal', _('Donegal')),
    ('down', _('Down')),
    ('dublin', _('Dublin')),
    ('fermanagh', _('Fermanagh')),
    ('galway', _('Galway')),
    ('kerry', _('Kerry')),
    ('kildare', _('Kildare')),
    ('kilkenny', _('Kilkenny')),
    ('laois', _('Laois')),
    ('leitrim', _('Leitrim')),
    ('limerick', _('Limerick')),
    ('longford', _('Longford')),
    ('louth', _('Louth')),
    ('mayo', _('Mayo')),
    ('meath', _('Meath')),
    ('monaghan', _('Monaghan')),
    ('offaly', _('Offaly')),
    ('roscommon', _('Roscommon')),
    ('sligo', _('Sligo')),
    ('tipperary', _('Tipperary')),
    ('tyrone', _('Tyrone')),
    ('waterford', _('Waterford')),
    ('westmeath', _('Westmeath')),
    ('wexford', _('Wexford')),
    ('wicklow', _('Wicklow')),
    )

    class IECountySelect(Select):
        """
        A Select widget that uses a list of Irish Counties as its choices.
        """
        def __init__(self, attrs=None):
            from ie_counties import IE_COUNTY_CHOICES
            super(IECountySelect, self).__init__(attrs, choices=IE_COUNTY_CHOICES)


class IEL10NAddress(L10NAddress):
    
    def get_address_fields(self):
        return [forms.CharField(label=_(u"Address 1"), max_length=50),
                forms.CharField(label=_(u"Address 2"), max_length=50),
                forms.CharField(label=_(u"Address 3"), max_length=50),
                forms.CharField(label=_(u"Town"), max_length=50),
                forms.CharField(label=_(u"County"), widget=IECountySelect(), max_length=50),
               ] 