from django.utils.translation import gettext_lazy as _

DISCOUNT_TYPE_ABSOLUTE = 0
DISCOUNT_TYPE_PERCENTAGE = 1

DISCOUNT_TYPE_CHOICES = (
    (DISCOUNT_TYPE_ABSOLUTE, _("Absolute")),
    (DISCOUNT_TYPE_PERCENTAGE, _("Percentage")),
)
