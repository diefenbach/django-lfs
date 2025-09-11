# django imports
from django.forms import ModelForm

# lfs imports
from lfs.catalog.models import Property


class PropertyAddForm(ModelForm):
    """Form to add a property."""

    class Meta:
        model = Property
        fields = ["name"]


class PropertyDataForm(ModelForm):
    """Form to manage all data of a property including type and select field options."""

    class Meta:
        model = Property
        fields = [
            "name",
            "title",
            "unit",
            "type",
            "variants",
            "filterable",
            "configurable",
            "required",
            "display_on_product",
            "display_price",
            "add_price",
            "decimal_places",
            "unit_min",
            "unit_max",
            "unit_step",
            "step_type",
            "step",
        ]
