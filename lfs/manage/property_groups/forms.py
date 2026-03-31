from django.forms import ModelForm, CharField
from lfs.catalog.models import PropertyGroup


class PropertyGroupForm(ModelForm):
    """
    Form to add/edit a property group.
    """

    name = CharField(max_length=50, required=True, strip=True, help_text="Name of the property group")

    class Meta:
        model = PropertyGroup
        fields = ["name"]
