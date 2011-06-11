# django imports
from django import forms
from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# portlets imports
from portlets.models import Portlet

# lfs imports
import lfs.catalog.utils


class FilterPortlet(Portlet):
    """A portlet to display filters.
    """
    show_product_filters = models.BooleanField(_(u"Show product filters"), default=True)
    show_price_filters = models.BooleanField(_(u"Show price filters"), default=True)

    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        request = context.get("request")
        sorting = request.session.get("sorting")

        category = context.get("category")
        if category is None:
            return render_to_string("lfs/portlets/filter.html", {
                "show": False,
            })

        # get saved filters
        set_product_filters = request.session.get("product-filter", {})
        set_product_filters = set_product_filters.items()
        set_price_filters = request.session.get("price-filter")

        # calculate product filters
        if self.show_product_filters:
            product_filters = lfs.catalog.utils.get_product_filters(category,
                set_product_filters, set_price_filters, sorting)
        else:
            product_filters = None

        # calculate price filters
        if self.show_price_filters:
            price_filters = lfs.catalog.utils.get_price_filters(category,
                set_product_filters, set_price_filters)
        else:
            price_filters = None

        return render_to_string("lfs/portlets/filter.html", RequestContext(request, {
            "show": True,
            "title": self.title,
            "category": category,
            "show_product_filters": self.show_product_filters,
            "product_filters": product_filters,
            "set_price_filters": set_price_filters,
            "show_price_filters": self.show_price_filters,
            "price_filters": price_filters,
        }))

    def form(self, **kwargs):
        return FilterPortletForm(instance=self, **kwargs)


class FilterPortletForm(forms.ModelForm):
    """Form for the FilterPortlet.
    """
    class Meta:
        model = FilterPortlet
