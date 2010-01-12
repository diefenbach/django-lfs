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
        if value is None: value = ''
        self.image_id ="image_%s" % attrs["id"]
        final_attrs = self.build_attrs(attrs, name=name)
        #onchange ="onChange='document.getElementById(\"%s\").src=this.options[this.selectedIndex].title;'" % (self.image_id) 
        #alert(this.selectedIndex);
        onchange ="onchange='alert(this.options[this.selectedIndex].title);'"         
        output = [u'<table><tr> <td> <select%s%s>' % (flatatt(final_attrs),onchange) ]
        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append('</select></td> <td> <img src="" id="%s"></td> </tr></table>' % self.image_id)               
        #return mark_safe(u'\n'.join(output))
        return render_to_string("manage/widgets/selectimage.html",
               {"selectimageid":self.image_id,"choices":self.choices,"currentvalue":value,"finalattrs":flatatt(final_attrs)})
    def render_options(self, choices, selected_choices):
        def render_option(option_value, option_label):
            image= option_label['image']
            file_url= option_label['file']                
            option_value = force_unicode(option_value)
            selected_html = (option_value in selected_choices) and u' selected="selected"' or ''            
            return u'<option value="%s" title="%s"%s>%s</option>' % (
                escape(option_value), escape(image),selected_html,
                conditional_escape(force_unicode(file_url)))
        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):                
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(render_option(*option))
                output.append(u'</optgroup>')
            else:
                output.append(render_option(option_value, option_label))
        return u'\n'.join(output)