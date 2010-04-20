# django imports
from django.contrib import admin

# lfs imports
from lfs.core.models import Country
from lfs.core.models import Action
from lfs.core.models import ActionGroup
from lfs.core.models import Shop

admin.site.register(Shop)
admin.site.register(Country)
admin.site.register(Action)
admin.site.register(ActionGroup)
