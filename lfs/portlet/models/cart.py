# django imports
from django import forms
from django.template import RequestContext
from django.template.loader import render_to_string

# portlets imports
from portlets.models import Portlet
from portlets.utils import register_portlet


class CartPortlet(Portlet):
    """Portlet to display the cart.
    """
    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        import lfs.cart.utils

        request = context.get("request")
        cart = lfs.cart.utils.get_cart(request)
        if cart is None:
            amount_of_items = None
            price = None
        else:
            amount_of_items = cart.get_amount_of_items()
            price = cart.get_price_gross(request, total=True)

        return render_to_string("lfs/portlets/cart.html", RequestContext(request, {
            "title": self.title,
            "amount_of_items": amount_of_items,
            "price": price,
        }))

    def form(self, **kwargs):
        return CartPortletForm(instance=self, **kwargs)


class CartPortletForm(forms.ModelForm):
    """Form for CartPortlet.
    """
    class Meta:
        model = CartPortlet
