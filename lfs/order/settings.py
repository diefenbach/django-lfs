from django.utils.translation import gettext_lazy as _
from django.conf import settings

SUBMITTED = 0
PAID = 1
SENT = 2
CLOSED = 3
CANCELED = 4
PAYMENT_FAILED = 5
PAYMENT_FLAGGED = 6
PREPARED = 7

ORDER_STATES = [
    (SUBMITTED, _("Submitted")),
    (PAID, _("Paid")),
    (PREPARED, _("Prepared")),
    (SENT, _("Sent")),
    (CLOSED, _("Closed")),
    (CANCELED, _("Canceled")),
    (PAYMENT_FAILED, _("Payment Failed")),
    (PAYMENT_FLAGGED, _("Payment Flagged")),
]

# use numbers above 20 for custom order states to avoid conflicts if new base states are added to LFS core!
LFS_EXTRA_ORDER_STATES = getattr(settings, "LFS_EXTRA_ORDER_STATES", [])
if LFS_EXTRA_ORDER_STATES:
    ORDER_STATES.extend(LFS_EXTRA_ORDER_STATES)
