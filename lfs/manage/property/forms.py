# django imports
from django.forms import ModelForm

# lfs imports
from lfs.catalog.models import Property


class PropertyAddForm(ModelForm):
    """Form to add a property.
    """
    class Meta:
        model = Property
        fields = ["name"]


class PropertyDataForm(ModelForm):
    """Form to manage core data of a property.
    """
    class Meta:
        model = Property
        fields = ["position", "name", "title", "unit", "variants", "filterable", "configurable", "required", "display_on_product"]


class PropertyTypeForm(ModelForm):
    """Form to manage property type.
    """
    class Meta:
        model = Property
        fields = ["type"]


class StepTypeForm(ModelForm):
    """Form to manage the step type of a property.
    """
    class Meta:
        model = Property
        fields = ["step_type"]


class SelectFieldForm(ModelForm):
    """Form to manage attributes for select field.
    """
    class Meta:
        model = Property
        fields = ["display_price", "add_price"]


class NumberFieldForm(ModelForm):
    """Form to manage the number field.
    """
    class Meta:
        model = Property
        fields = ["decimal_places", "unit_min", "unit_max", "unit_step"]


class StepRangeForm(ModelForm):
    """Form to manage step range.
    """
    class Meta:
        model = Property
        fields = ["step"]
