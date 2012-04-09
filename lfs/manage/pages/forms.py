# django imports
from django.forms import ModelForm

# lfs imports
from lfs.core.widgets.file import LFSFileInput
from lfs.page.models import Page


class PageForm(ModelForm):
    """Form to edit a page.
    """
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields["file"].widget = LFSFileInput()

    class Meta:
        model = Page
        exclude = ("position", "meta_title", "meta_description", "meta_keywords")


class PageAddForm(ModelForm):
    """Form to add a page.
    """
    class Meta:
        model = Page
        fields = ("title", "slug")
