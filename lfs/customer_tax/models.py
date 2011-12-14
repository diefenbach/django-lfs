# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.core.models import Country


class CustomerTax(models.Model):
    """Represent a tax rate.

    **Attributes**:

    rate
        The tax rate in percent.

    description
        The description of the tax rate.

    countries
        The country for which the tax is valid.
    """
    rate = models.FloatField(_(u"Rate"), default=0)
    description = models.TextField(_(u"Description"), blank=True)
    countries = models.ManyToManyField(Country, verbose_name=_(u"Countries"))
