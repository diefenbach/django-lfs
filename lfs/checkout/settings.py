from django.conf import settings
from django.utils.translation import gettext_lazy as _

CHECKOUT_TYPE_SELECT = 0
CHECKOUT_TYPE_ANON = 1
CHECKOUT_TYPE_AUTH = 2
CHECKOUT_TYPES = (
    (CHECKOUT_TYPE_SELECT, _("Anonymous and Authenticated")),
    (CHECKOUT_TYPE_ANON, _("Anonymous only")),
    (CHECKOUT_TYPE_AUTH, _("Authenticated only")),
)
SHIPPING_PREFIX = "shipping"
INVOICE_PREFIX = "invoice"

ONE_PAGE_CHECKOUT_FORM = getattr(settings, "LFS_ONE_PAGE_CHECKOUT_FORM", "lfs.checkout.forms.OnePageCheckoutForm")
