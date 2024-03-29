# django imports
from django import forms
from django.template.loader import render_to_string

# portlets imports
from portlets.models import Portlet


class RelatedProductsPortlet(Portlet):
    """Portlet to display related products."""

    class Meta:
        app_label = "portlet"

    def __str__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html."""
        product = context.get("product")
        request = context.get("request")

        return render_to_string(
            "lfs/portlets/related_products.html",
            request=request,
            context={
                "title": self.title,
                "product": product,
            },
        )

    def form(self, **kwargs):
        return RelatedProductsForm(instance=self, **kwargs)


class RelatedProductsForm(forms.ModelForm):
    """Form for the RelatedProductsPortlet."""

    class Meta:
        model = RelatedProductsPortlet
        exclude = ()
