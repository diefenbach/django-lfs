# django imports
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class OnePageCheckoutForm(forms.Form):
    requested_delivery_date = forms.DateField(label=_(u"Requested Delivery Date"), required=False)
    payment_method = forms.CharField(required=False, max_length=2)
    no_shipping = forms.BooleanField(label=_(u"Same as invoice"), initial=True, required=False)
    no_invoice = forms.BooleanField(label=_(u"Same as shipping address"), initial=True, required=False)
    message = forms.CharField(label=_(u"Your message to us"), widget=forms.Textarea(attrs={'cols': '80'}),
                              required=False)

    def __init__(self, *args, **kwargs):
        super(OnePageCheckoutForm, self).__init__(*args, **kwargs)
        not_required_address = getattr(settings, 'LFS_CHECKOUT_NOT_REQUIRED_ADDRESS', 'shipping')
        if not_required_address == 'shipping':
            del self.fields['no_invoice']
        else:
            del self.fields['no_shipping']

    def no_address_field(self):
        not_required_address = getattr(settings, 'LFS_CHECKOUT_NOT_REQUIRED_ADDRESS', 'shipping')
        field_name = 'no_%s' % not_required_address
        return self[field_name]
