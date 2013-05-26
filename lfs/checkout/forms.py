# django imports
from django import forms
from django.utils.translation import ugettext_lazy as _


class OnePageCheckoutForm(forms.Form):
    requested_delivery_date = forms.DateField(label=_(u"Requested Delivery Date"), required=False)
    payment_method = forms.CharField(required=False, max_length=1)
    no_shipping = forms.BooleanField(label=_(u"Same as invoice"), initial=True, required=False)
    message = forms.CharField(label=_(u"Your message to us"), widget=forms.Textarea(attrs={'cols': '80'}), required=False)
