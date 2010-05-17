from django.utils.translation import gettext_lazy as _
from django.conf import settings

ACTION_PLACE_TABS = 1
ACTION_PLACE_CHOICES = [
    (ACTION_PLACE_TABS, _(u"Top Menu")),
]
POSTAL_ADDRESS_L10N = getattr(settings, 'POSTAL_ADDRESS_L10N', True)