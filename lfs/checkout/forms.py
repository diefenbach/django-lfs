# python imports
from datetime import datetime

# django imports
from django import forms
from django.conf import settings
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.payment.settings
from lfs.payment.models import PaymentMethod
from lfs.core.utils import get_default_shop
from lfs.core.models import Country


class OnePageCheckoutForm(forms.Form):
    requested_delivery_date = forms.DateField(label=_(u"Requested Delivery Date"), required=False)
    payment_method = forms.CharField(required=False, max_length=1)
    no_shipping = forms.BooleanField(label=_(u"Same as invoice"), initial=True, required=False)
    message = forms.CharField(label=_(u"Your message to us"), widget=forms.Textarea(attrs={'cols': '80'}), required=False)
