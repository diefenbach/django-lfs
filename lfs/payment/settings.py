# django imports
from django.utils.translation import gettext_lazy as _

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
    (CC_MASTERCARD, _("Mastercard")),
    (CC_VISA, _("Visacard")),
)

PM_PLAIN = 0
PM_BANK = 1
PM_CREDIT_CARD = 2

PAYMENT_METHOD_TYPES_CHOICES = (
    (PM_PLAIN, _("Plain")),
    (PM_BANK, _("Bank")),
    (PM_CREDIT_CARD, _("Credit Card")),
)

PM_ORDER_IMMEDIATELY = 0
PM_ORDER_ACCEPTED = 1

PM_MSG_TOP = 10
PM_MSG_FORM = 11
