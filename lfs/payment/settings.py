# django imports
from django.utils.translation import ugettext_lazy as _

DIRECT_DEBIT = 1
CASH_ON_DELIVERY = 2
PAYPAL = 3
PRE_PAYMENT = 4
BY_INVOICE = 5
CREDIT_CARD = 6

CC_AMERICAN_EXPRESS = "AMEX"
CC_MASTERCARD = "MASTER"
CC_VISA = "VISA"

CREDIT_CARD_TYPE_CHOICES = (
    (CC_MASTERCARD, _(u"Mastercard")),
    (CC_VISA, _(u"Visacard")),
)

PM_PLAIN = 0
PM_BANK = 1
PM_CREDIT_CARD = 2

PAYMENT_METHOD_TYPES_CHOICES = (
    (PM_PLAIN, _(u"Plain")),
    (PM_BANK, _(u"Bank")),
    (PM_CREDIT_CARD, _(u"Credit Card")),
)
