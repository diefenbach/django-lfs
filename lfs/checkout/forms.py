# django imports
from django import forms
from django.utils.translation import ugettext_lazy as _

from lfs.addresses.settings import CHECKOUT_NOT_REQUIRED_ADDRESS


class OnePageCheckoutForm(forms.Form):
    requested_delivery_date = forms.DateField(label=_(u"Requested Delivery Date"), required=False)
    payment_method = forms.CharField(required=False, max_length=2)
    no_shipping = forms.BooleanField(label=_(u"Same as invoice"), initial=True, required=False)
    no_invoice = forms.BooleanField(label=_(u"Same as shipping address"), initial=True, required=False)
    message = forms.CharField(label=_(u"Your message to us"), widget=forms.Textarea(attrs={'cols': '80'}),
                              required=False)

    def __init__(self, *args, **kwargs):
        super(OnePageCheckoutForm, self).__init__(*args, **kwargs)
        if CHECKOUT_NOT_REQUIRED_ADDRESS == 'shipping':
            del self.fields['no_invoice']
        else:
            del self.fields['no_shipping']

    def no_address_field(self):
        field_name = 'no_%s' % CHECKOUT_NOT_REQUIRED_ADDRESS
        return self[field_name]
