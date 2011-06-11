# django imports
from django import forms
from django.conf import settings
from django.core.cache import cache
from django.template import RequestContext
from django.template.loader import render_to_string

# portlets imports
from portlets.models import Portlet

# lfs imports
from lfs.page.models import Page


class PagesPortlet(Portlet):
    """Portlet to display pages.
    """
    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        request = context.get("request")

        cache_key = "%s-pages" % settings.CACHE_MIDDLEWARE_KEY_PREFIX
        pages = cache.get(cache_key)
        if pages is None:
            pages = Page.objects.filter(active=True, exclude_from_navigation=False)
            cache.set(cache_key, pages)

        return render_to_string("lfs/portlets/pages.html", RequestContext(request, {
            "title": self.title,
            "pages": pages,
        }))

    def form(self, **kwargs):
        return PagesForm(instance=self, **kwargs)


class PagesForm(forms.ModelForm):
    """Form for the PagesPortlet.
    """
    class Meta:
        model = PagesPortlet
