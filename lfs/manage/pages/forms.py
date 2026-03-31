# django imports
from django.forms import ModelForm
from django.forms.widgets import ClearableFileInput

# lfs imports
from lfs.page.models import Page


class PageForm(ModelForm):
    """Form to edit a page."""

    class Meta:
        model = Page
        exclude = ("position", "meta_title", "meta_description", "meta_keywords")
        widgets = {
            "file": ClearableFileInput,
        }


class PageAddForm(ModelForm):
    """Form to add a page."""

    class Meta:
        model = Page
        fields = ("title", "slug")
