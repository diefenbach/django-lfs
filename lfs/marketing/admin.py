# django imports
from django.contrib import admin

# lfs imports
from lfs.marketing.models import Topseller, FeaturedProduct

admin.site.register(Topseller)
admin.site.register(FeaturedProduct)
