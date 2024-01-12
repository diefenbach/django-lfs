from django.utils.translation import gettext_lazy as _

ABSOLUTE = 0
PERCENTAGE = 1

KIND_OF_CHOICES = (
    (ABSOLUTE, _("Absolute")),
    (PERCENTAGE, _("Percentage")),
)

MESSAGES = (
    _("The voucher is valid."),
    _("The voucher is not active."),
    _("The voucher has been already used."),
    _("The voucher is not active yet."),
    _("The voucher is not active any more."),
    _("The voucher is not valid for this cart price."),
    _("The voucher doesn't exist."),
)
