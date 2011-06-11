# django imports
from django import forms
from django.template import RequestContext
from django.template.loader import render_to_string

# portlets imports
from portlets.models import Portlet

# reviews imports
import reviews.utils


class AverageRatingPortlet(Portlet):
    """Portlet to display the average rating for a product.
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

        if product is None:
            d = {
                "average": False,
            }
        else:
            average, amount = reviews.utils.get_average_for_instance(product)

        return render_to_string("lfs/portlets/average_rating.html", RequestContext(request, {
            "title": self.title,
            "average": average,
            "amount": amount,
        }))

    def form(self, **kwargs):
        return AverageRatingForm(instance=self, **kwargs)


class AverageRatingForm(forms.ModelForm):
    """Form for the AverageRatingPortlet.
    """
    class Meta:
        model = AverageRatingPortlet
