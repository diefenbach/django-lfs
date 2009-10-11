# django imports
from django import forms
from django.template.loader import render_to_string

# portlets imports
from portlets.models import Portlet
from portlets.utils import register_portlet

class RelatedProductsPortlet(Portlet):
    """A portlet to display related products.
    """
    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        product = context.get("product")

        return render_to_string("lfs/portlets/related_products.html", {
            "title" : self.title,
            "product" : product,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        })

    def form(self, **kwargs):
        """
        """
        return RelatedProductsForm(instance=self, **kwargs)

class RelatedProductsForm(forms.ModelForm):
    """
    """
    class Meta:
        model = RelatedProductsPortlet
