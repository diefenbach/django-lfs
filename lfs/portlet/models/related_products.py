# django imports
from django import forms
from django.template import RequestContext
from django.template.loader import render_to_string

# portlets imports
from portlets.models import Portlet


class RelatedProductsPortlet(Portlet):
    """Portlet to display related products.
    """
    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        product = context.get("product")
        request = context.get("request")
        price = ""
        sale_price = ""
        if product:
            price = product.get_price(request)
            sale_price = product.get_for_sale_price(request)

        return render_to_string("lfs/portlets/related_products.html", RequestContext(request, {
            "title": self.title,
            "product": product,
            "price": price,
            "sale_price": sale_price
        }))

    def form(self, **kwargs):
        return RelatedProductsForm(instance=self, **kwargs)


class RelatedProductsForm(forms.ModelForm):
    """Form for the RelatedProductsPortlet.
    """
    class Meta:
        model = RelatedProductsPortlet
