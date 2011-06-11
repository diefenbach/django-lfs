from django.utils.translation import ugettext_lazy as _

CHECKOUT_TYPE_SELECT = 0
CHECKOUT_TYPE_ANON = 1
CHECKOUT_TYPE_AUTH = 2
CHECKOUT_TYPES = (
    (CHECKOUT_TYPE_SELECT, _(u"Anonymous and Authenticated")),
    (CHECKOUT_TYPE_ANON, _(u"Anonymous only")),
    (CHECKOUT_TYPE_AUTH, _(u"Authenticated only")),
)
SHIPPING_PREFIX = "shipping"
INVOICE_PREFIX = "invoice"
