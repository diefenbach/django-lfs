# django imports
from django.forms import ModelForm

# lfs imports
from lfs.manufacturer.models import Manufacturer


class ManufacturerDataForm(ModelForm):
    """Form to manage selection data.
    """
    class Meta:
        model = Manufacturer
