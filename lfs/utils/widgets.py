from itertools import chain

from django.forms.widgets import Select
from django.forms.util import flatatt

from django.utils.html import escape, conditional_escape
#from django.utils.safestring import mark_safe
from django.utils.encoding import StrAndUnicode, force_unicode

from django.template.loader import render_to_string


class SelectImage(Select):
    def __init__(self, attrs=None, choices=()):
        super(Select, self).__init__(attrs)
        # choices can be any iterable, but we may need to render this widget
        # multiple times. Thus, collapse it into a list so it can be consumed
        # more than once.
        self.choices = list(choices)

    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = ""
        self.image_id = "image_%s" % attrs["id"]
        final_attrs = self.build_attrs(attrs, name=name)
        defaultimage = None
        for id, keys in self.choices:
            if str(id) == str(value):
                defaultimage = keys["image"]

        # Try to pick first image as default image
        if defaultimage == None:
            if len(self.choices) > 0:
                defaultimage = self.choices[0][1]["image"]
        return render_to_string("manage/widgets/selectimage.html",
               {"selectimageid": self.image_id,
                "choices": self.choices,
                "currentvalue": value,
                "finalattrs": flatatt(final_attrs),
                "imageurl": defaultimage,
               })
