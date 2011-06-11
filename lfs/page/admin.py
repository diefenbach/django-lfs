# django imports
from django.contrib import admin

# lfs imports
from lfs.page.models import Page


class PageAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(Page, PageAdmin)
