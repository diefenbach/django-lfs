# django imports
from django.forms import ModelForm

# lfs imports
from lfs.catalog.models import PropertyGroup


class PropertyGroupForm(ModelForm):
    """
    Form to add/edit a property group.
    """
    class Meta:
        model = PropertyGroup
        fields = ["name"]
