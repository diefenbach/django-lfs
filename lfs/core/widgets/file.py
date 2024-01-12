# django imports
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _


class LFSFileInput(forms.FileInput):
    """A custom file widget which displays the current file."""

    def render(self, name, value, attrs=None, renderer=None):
        output = super(LFSFileInput, self).render(name, value, attrs=None, renderer=None)
        if value:
            if hasattr(value, "url"):
                output = ("""<div><a href="%s" />%s</a></div>""" % (value.url, value.name)) + output
            elif hasattr(value, "name"):
                output = ("""<div>%s</div>""" % value.name) + output

        if value:
            trans = _("Delete file")
            output += """<div><input type="checkbox" name="delete_%s" id="id_delete_%s" />
                              <label for="delete_%s">%s</label></div>""" % (
                name,
                name,
                name,
                trans,
            )

        return mark_safe(output)
