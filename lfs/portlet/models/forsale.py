from django import forms
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from portlets.models import Portlet

from lfs.catalog.models import Category
from lfs.catalog.models import Product


class ForsalePortlet(Portlet):
    """A portlet for displaying for sale products.
    """

    class Meta:
        app_label = 'portlet'

    name = _("Product Forsale")

    limit = models.IntegerField(_(u"Limit"), default=5)
    current_category = models.BooleanField(_(u"Use current category"), default=False)
    slideshow = models.BooleanField(_(u"Slideshow"), default=False)

    @property
    def rendered_title(self):
        return self.title or self.name

    def render(self, context):
        """Renders the portlet as html.
        """
        request = context.get("request")

        products = Product.objects.filter(for_sale=True)
        if self.current_category:
            obj = context.get("category") or context.get("product")
            if obj:
                category = obj if isinstance(obj, Category) else obj.get_current_category(request)
                categories = [category]
                categories.extend(category.get_all_children())
                products = products.filter(categories__in=categories)[:self.limit]
            else:
                products = None
        else:
            products = products[:self.limit]

        return render_to_string("lfs/portlets/forsale.html", request=request, context={
            "title": self.rendered_title,
            "slideshow": self.slideshow,
            "products": products,
            "MEDIA_URL": context.get("MEDIA_URL"),
        })

    def form(self, **kwargs):
        """
        """
        return ForsaleForm(instance=self, **kwargs)

    def __unicode__(self):
        return u"%s" % self.id


class ForsaleForm(forms.ModelForm):
    """
    """
    class Meta:
        model = ForsalePortlet
        exclude = ()
