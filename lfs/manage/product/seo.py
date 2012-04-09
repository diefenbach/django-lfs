# django imports
from django.forms import ModelForm

# lfs.imports
from lfs.catalog.models import Product


class SEOForm(ModelForm):
    """Form to add/edit seo properties of a product.
    """
    class Meta:
        model = Product
        fields = (
            "active_meta_title", "meta_title",
            "active_meta_keywords", "meta_keywords",
            "active_meta_description", "meta_description",
        )
