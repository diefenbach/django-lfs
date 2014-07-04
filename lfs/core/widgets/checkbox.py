from django.forms.widgets import CheckboxInput


class LFSCheckboxInput(CheckboxInput):
    def value_from_datadict(self, data, files, name):
        res = super(LFSCheckboxInput, self).value_from_datadict(data, files, name)
        return int(res)