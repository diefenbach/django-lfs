# django imports
from django import forms
from django.template.loader import render_to_string

# portlets imports
from portlets.models import Portlet

# reviews imports
import reviews.utils

class AverageRatingPortlet(Portlet):
    """A portlet to display recent visited products.
    """
    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        product = context.get("product")

        if product is None:
            d = {
                "average" : False,
            }
        else:
            average, amount = reviews.utils.get_average_for_instance(product)
            d = {
                "title" : self.title,
                "average" : average,
                "amount" : amount,
                "MEDIA_URL" : context.get("MEDIA_URL"),
            }

        return render_to_string("lfs/portlets/average_rating.html", d)

    def form(self, **kwargs):
        """
        """
        return AverageRatingForm(instance=self, **kwargs)

class AverageRatingForm(forms.ModelForm):
    """
    """
    class Meta:
        model = AverageRatingPortlet