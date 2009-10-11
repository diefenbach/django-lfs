# django imports
from django import forms
from django.db import models
from django.template.loader import render_to_string

# portlets
from portlets.models import Portlet

# lfs imports
import lfs.core.utils

class CategoriesPortlet(Portlet):
    """A portlet to display categories.
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

        object = context.get("category") or context.get("product")
        current_categories = lfs.core.utils.get_current_categories(request, object)

        ct = lfs.core.utils.CategoryTree(
            current_categories, self.start_level, self.expand_level)
        category_tree = ct.get_category_tree()

        return render_to_string("lfs/portlets/categories.html", {
            "title" : self.title,
            "categories" : category_tree,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        })

    def form(self, **kwargs):
        """
        """
        return CategoriesPortletForm(instance=self, **kwargs)

class CategoriesPortletForm(forms.ModelForm):
    """
    """
    class Meta:
        model = CategoriesPortlet
