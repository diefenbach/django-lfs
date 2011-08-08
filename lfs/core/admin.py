# django imports
from django.contrib import admin

# lfs imports
from lfs.core.models import Action
from lfs.core.models import ActionGroup
from lfs.core.models import Shop
from lfs.core.models import Country

admin.site.register(Shop)
admin.site.register(Action)
admin.site.register(ActionGroup)
admin.site.register(Country)
