# django imports
from django import forms
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.customer_tax.models import CustomerTax

class CustomerTaxForm(forms.ModelForm):
    """Form to add and edit a customer tax.
    """
    class Meta:
        model = CustomerTax
        exclude = ("description", )

    def clean_countries(self):
        countries = self.cleaned_data.get("countries")

        for country in countries:
            try:
                ct = CustomerTax.objects.filter(countries=country).exclude(pk=self.instance.id)[0]
            except IndexError:
                continue
            else:
                raise forms.ValidationError(
                    _(u"There is already a customer tax with country %(country)s, see %(customer_tax)s %% ") %
                    {"country": country.name, "customer_tax": ct.rate})

        return countries
