from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class LFSImageInput(forms.FileInput):
    """A custom image widget which displays the current image."""

    def render(self, name, value, attrs=None, renderer=None):
        output = super(LFSImageInput, self).render(name, value, attrs=None, renderer=None)

        if value and hasattr(value, "url_60x60"):
            output += """<div><img src="%s" /></div>""" % value.url_60x60
        elif value and hasattr(value, "url"):
            output += """<div><img src="%s" /></div>""" % value.url

        if value:
            trans = _("Delete image")
            output += (
                """<div><input type="checkbox" name="delete_image" id="id_delete_image" /> <label for="delete_image">%s</label></div>"""
                % trans
            )

        return mark_safe(output)
