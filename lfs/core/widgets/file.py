# django imports
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class LFSFileInput(forms.FileInput):
    """A custom file widget which displays the current file.
    """
    def render(self, name, value, attrs=None):
        output = super(LFSFileInput, self).render(name, None, attrs=attrs)
        if value:
            if hasattr(value, "url"):
                output = (u"""<div><a href="%s" />%s</a></div>""" % (value.url, value.name)) + output
            elif hasattr(value, "name"):
                output = (u"""<div>%s</div>""" % value.name) + output

        if value:
            trans = _(u"Delete file")
            output += """<div><input type="checkbox" name="delete_file" id="id_delete_file" /> <label for="delete_file">%s</label></div>""" % trans._proxy____unicode_cast()

        return mark_safe(output)
