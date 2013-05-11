# django imports
from django.forms import ModelForm

# lfs imports
from lfs.core.models import Action


class ActionForm(ModelForm):
    """Form to edit an action.
    """
    class Meta:
        model = Action
        exclude = ("parent", "position")


class ActionAddForm(ModelForm):
    """Form to add a action
    """
    class Meta:
        model = Action
        fields = ("title", "link", "group")
