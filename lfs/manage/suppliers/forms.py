# django imports
from django.forms import ModelForm

# lfs imports
from lfs.supplier.models import Supplier


class SupplierAddForm(ModelForm):
    """Process form to add a supplier.
    """
    class Meta:
        model = Supplier
        fields = ("name", "slug")


class SupplierDataForm(ModelForm):
    """Form to manage selection data.
    """
    class Meta:
        model = Supplier
        fields = ("name", "slug", "user", "active")
