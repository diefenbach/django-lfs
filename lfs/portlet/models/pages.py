# django imports
from django import forms
from django.core.cache import cache
from django.template.loader import render_to_string

# portlets imports
from portlets.models import Portlet
from portlets.utils import register_portlet

# lfs imports
from lfs.page.models import Page

class PagesPortlet(Portlet):
    """A portlet to display pages.
    """
    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        cache_key = "pages"
        pages = cache.get(cache_key)
        if pages is None:
            pages = Page.objects.filter(active=True, exclude_from_navigation=False)
            cache.set(cache_key, pages)
        
        return render_to_string("lfs/portlets/pages.html", {
            "title" : self.title,
            "pages" : pages,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        })

    def form(self, **kwargs):
        """
        """
        return PagesForm(instance=self, **kwargs)

class PagesForm(forms.ModelForm):
    """
    """
    class Meta:
        model = PagesPortlet
