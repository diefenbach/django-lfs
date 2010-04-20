from django.utils.translation import gettext_lazy as _

ACTION_PLACE_TABS = 1
ACTION_PLACE_FOOTER = 2

ACTION_PLACE_CHOICES = [
    (ACTION_PLACE_TABS, _(u"Tabs")),
    (ACTION_PLACE_FOOTER, _(u"Footer")),
]
