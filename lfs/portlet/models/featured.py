# django imports
from django import forms
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# portlets imports
from portlets.models import Portlet

from lfs.marketing.models import FeaturedProduct

from lfs.caching.utils import lfs_get_object


class FeaturedPortlet(Portlet):
    """A portlet for displaying for sale products.
    """

    class Meta:
        app_label = 'portlet'

    name = _("Featured products")

    limit = models.IntegerField(_(u"Limit"), default=5)
    current_category = models.BooleanField(_(u"Use current category"), default=False)
    slideshow = models.BooleanField(_(u"Slideshow"), default=False)

    @property
    def rendered_title(self):
        return self.title or self.name

    def render(self, context):
        """Renders the portlet as html.
        """
        filters = dict(for_sale=True,)
        # filter by current category
        if self.current_category and context.get('category'):
            cat = context.get('category')
            filters['categories__in'] = [cat.id,]

        products = [x.product
                    for x in FeaturedProduct.objects.all()[:self.limit]]

        return render_to_string("lfs/portlets/featured.html", {
            "title" : self.rendered_title,
            "slideshow" : self.slideshow,
            "products" : products,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        })



    def form(self, **kwargs):
        """
        """
        return FeaturedForm(instance=self, **kwargs)

    def __unicode__(self):
        return "%s" % self.id


class FeaturedForm(forms.ModelForm):
    """
    """
    class Meta:
        model = FeaturedPortlet

