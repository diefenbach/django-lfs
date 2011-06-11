# django imports
from django import forms
from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# portlets imports
from portlets.models import Portlet


class TextPortlet(Portlet):
    """Portlet to display some text.
    """
    text = models.TextField(_(u"Text"), blank=True)

    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        request = context.get("request")
        return render_to_string("lfs/portlets/text_portlet.html", RequestContext(request, {
            "title": self.title,
            "text": self.text
        }))

    def form(self, **kwargs):
        return TextPortletForm(instance=self, **kwargs)


class TextPortletForm(forms.ModelForm):
    """Form for the TextPortlet.
    """
    class Meta:
        model = TextPortlet
