from django.utils.translation import gettext_lazy as _

ABSOLUTE = 0
PERCENTAGE = 1

KIND_OF_CHOICES = (
    (ABSOLUTE, _(u"Absolute")),
    (PERCENTAGE, _(u"Percentage")),
)