# django imports
from django import forms
from django.template.loader import render_to_string

# portlets imports
from portlets.models import Portlet
from portlets.utils import register_portlet

class CartPortlet(Portlet):
    """A portlet to display news.
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
            amount_of_items = cart.amount_of_items
            price = lfs.cart.utils.get_cart_price(request, cart, total=True)
        
        return render_to_string("lfs/portlets/cart.html", {
            "title" : self.title,
            "amount_of_items" : amount_of_items,
            "price" : price,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        })
        
    def form(self, **kwargs):
        """
        """
        return CartPortletForm(instance=self, **kwargs)
        
class CartPortletForm(forms.ModelForm):
    """
    """
    class Meta:
        model = CartPortlet
