# django imports
from django import forms
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

# portlets imports
from portlets.models import Portlet


class TextPortlet(Portlet):
    """Portlet to display some text."""

    text = models.TextField(_("Text"), blank=True)

    class Meta:
        app_label = "portlet"

    def __str__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html."""
        request = context.get("request")
        return render_to_string(
            "lfs/portlets/text_portlet.html", request=request, context={"title": self.title, "text": self.text}
        )

    def form(self, **kwargs):
        return TextPortletForm(instance=self, **kwargs)


class TextPortletForm(forms.ModelForm):
    """Form for the TextPortlet."""

    class Meta:
        model = TextPortlet
        exclude = ()
