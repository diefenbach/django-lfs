from django import forms
from django.utils.translation import gettext_lazy as _

from lfs.core.widgets.image import LFSImageInput
from lfs.manufacturer.models import Manufacturer


class ManufacturerAddForm(forms.ModelForm):
    """Form to add a new manufacturer."""

    class Meta:
        model = Manufacturer
        fields = ("name", "slug")


class ManufacturerForm(forms.ModelForm):
    """Form to edit manufacturer data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].widget = LFSImageInput()

    class Meta:
        model = Manufacturer
        fields = (
            "name",
            "slug",
            "short_description",
            "description",
            "image",
        )
