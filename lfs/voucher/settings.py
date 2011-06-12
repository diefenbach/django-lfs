from django.utils.translation import ugettext_lazy as _

ABSOLUTE = 0
PERCENTAGE = 1

KIND_OF_CHOICES = (
    (ABSOLUTE, _(u"Absolute")),
    (PERCENTAGE, _(u"Percentage")),
)

MESSAGES = (
    _(u"The voucher is valid."),
    _(u"The voucher is not active."),
    _(u"The voucher has been already used."),
    _(u"The voucher is not active yet."),
    _(u"The voucher is not active any more."),
    _(u"The voucher is not valid for this cart price."),
    _(u"The voucher doesn't exist."),
)
