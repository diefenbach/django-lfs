# django imports
from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string

# portlets imports
from portlets.models import Portlet
from portlets.utils import register_portlet

# lfs imports
from lfs.catalog.models import Product

class RecentProductsPortlet(Portlet):
    """A portlet to display recent visited products.
    """
    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        object = context.get("product")        
        slug_not_to_display = ""
        limit = settings.LFS_RECENT_PRODUCTS_LIMIT
        if object:
            ctype = ContentType.objects.get_for_model(object)
            if ctype.name == u"product":
                slug_not_to_display = object.slug
                limit = settings.LFS_RECENT_PRODUCTS_LIMIT + 1

        request = context.get("request")

        products = []
        for slug in request.session.get("RECENT_PRODUCTS", [])[:limit]:
            if slug == slug_not_to_display:
                continue
            try:
                product = Product.objects.get(slug=slug)
            except Product.DoesNotExist:
                pass
            else:
                if product.is_product_with_variants() and product.has_variants():
                    product = product.get_default_variant()
                products.append(product)

        return render_to_string("lfs/portlets/recent_products.html", {
            "title" : self.title,
            "products" : products,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        })

    def form(self, **kwargs):
        """
        """
        return RecentProductsForm(instance=self, **kwargs)

class RecentProductsForm(forms.ModelForm):
    """
    """
    class Meta:
        model = RecentProductsPortlet
