from django import forms
from django.utils.translation import gettext_lazy as _

from lfs.catalog.models import Category, StaticBlock
from lfs.catalog.settings import CATEGORY_TEMPLATES
from lfs.core.widgets.image import LFSImageInput
from lfs.utils.widgets import SelectImage


class CategoryAddForm(forms.ModelForm):
    """Form to add a new category."""

    class Meta:
        model = Category
        fields = ("name", "slug")


class CategoryForm(forms.ModelForm):
    """Form to edit category data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].widget = LFSImageInput()

        # Set up static_block choices
        static_block_choices = [("", _("No static block"))]
        static_block_choices.extend([(sb.id, sb.name) for sb in StaticBlock.objects.all().order_by("name")])
        self.fields["static_block_above"].choices = static_block_choices
        self.fields["static_block_below"].choices = static_block_choices

    class Meta:
        model = Category
        fields = (
            "name",
            "slug",
            "short_description",
            "description",
            "exclude_from_navigation",
            "image",
            "static_block_above",
            "static_block_below",
        )


class CategoryViewForm(forms.ModelForm):
    """Form to edit category view settings."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(ord, d["name"]) for (ord, d) in enumerate(CATEGORY_TEMPLATES)]
        self.fields["template"].widget = SelectImage(choices=choices)

    class Meta:
        model = Category
        fields = (
            "template",
            "show_all_products",
        )
