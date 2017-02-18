from django.utils.translation import ugettext_lazy as _
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
    (SUBMITTED, _(u"Submitted")),
    (PAID, _(u"Paid")),
    (PREPARED, _(u"Prepared")),
    (SENT, _(u"Sent")),
    (CLOSED, _(u"Closed")),
    (CANCELED, _(u"Canceled")),
    (PAYMENT_FAILED, _(u"Payment Failed")),
    (PAYMENT_FLAGGED, _(u"Payment Flagged")),
]

# use numbers above 20 for custom order states to avoid conflicts if new base states are added to LFS core!
LFS_EXTRA_ORDER_STATES = getattr(settings, 'LFS_EXTRA_ORDER_STATES', [])
if LFS_EXTRA_ORDER_STATES:
    ORDER_STATES.extend(LFS_EXTRA_ORDER_STATES)
