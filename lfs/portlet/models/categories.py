# django imports
from django.conf import settings
from django import forms
from django.core.cache import cache
from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string

# portlets
from portlets.models import Portlet

# lfs imports
import lfs.core.utils


class CategoriesPortlet(Portlet):
    """Portlet to display categories.
    """
    start_level = models.PositiveSmallIntegerField(default=1)
    expand_level = models.PositiveSmallIntegerField(default=1)

    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        # Calculate current categories
        request = context.get("request")

        product = context.get("product")
        category = context.get("category")
        object = category or product

        if object is None:
            object_id = None
        else:
            object_id = object.id

        cache_key = "%s-categories-portlet-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, object.__class__.__name__, object_id)
        result = cache.get(cache_key)
        if result is not None:
            return result

        current_categories = lfs.core.utils.get_current_categories(request, object)

        ct = lfs.core.utils.CategoryTree(
            current_categories, self.start_level, self.expand_level)
        category_tree = ct.get_category_tree()

        result = render_to_string("lfs/portlets/categories.html", RequestContext(request, {
            "title": self.title,
            "categories": category_tree,
            "product": product,
            "category": category,
        }))

        cache.set(cache_key, result)
        return result

    def form(self, **kwargs):
        return CategoriesPortletForm(instance=self, **kwargs)


class CategoriesPortletForm(forms.ModelForm):
    """Form for CategoriesPortlet.
    """
    class Meta:
        model = CategoriesPortlet
