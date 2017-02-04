# django imports
from django import forms
from django.db import models
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
    show_manufacturer_filters = models.BooleanField(_(u"Show manufacturer filters"), default=False)

    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return u"%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        request = context.get("request")
        sorting = request.session.get("sorting", "price")

        category = context.get("category")
        if category is None:
            return render_to_string("lfs/portlets/filter.html", request=request, context={
                "show": False,
            })

        # get saved filters
        set_product_filters = request.session.get("product-filter", {})
        set_price_filters = request.session.get("price-filter", {})
        set_manufacturer_filters = request.session.get("manufacturer-filter")

        product_filters = None
        price_filters = None
        manufacturer_filters = None

        # calculate product filters
        if self.show_product_filters:
            product_filters = lfs.catalog.utils.get_product_filters(category, set_product_filters, set_price_filters,
                                                                    set_manufacturer_filters,
                                                                    sorting)

        # calculate price filters
        if self.show_price_filters:
            price_filters = lfs.catalog.utils.get_price_filters(category, set_product_filters, set_price_filters,
                                                                set_manufacturer_filters)

        # calculate manufacturer filters
        if self.show_manufacturer_filters:
            manufacturer_filters = lfs.catalog.utils.get_manufacturer_filters(category, set_product_filters,
                                                                              set_price_filters,
                                                                              set_manufacturer_filters)

        return render_to_string("lfs/portlets/filter.html", request=request, context={
            "show": True,
            "title": self.title,
            "category": category,
            "show_product_filters": self.show_product_filters,
            "show_manufacturer_filters": self.show_manufacturer_filters,
            "product_filters": product_filters,
            "manufacturer_filters": manufacturer_filters,
            "set_price_filters": set_price_filters,
            "show_price_filters": self.show_price_filters,
            "price_filters": price_filters,
        })

    def form(self, **kwargs):
        return FilterPortletForm(instance=self, **kwargs)


class FilterPortletForm(forms.ModelForm):
    """Form for the FilterPortlet.
    """
    class Meta:
        model = FilterPortlet
        exclude = ()
