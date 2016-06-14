# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.criteria.base import Criteria


class CustomerTax(models.Model, Criteria):
    """
    Represent a customer tax rate.

    **Attributes**:

    rate
        The tax rate in percent.

    description
        The description of the tax rate.
    """
    rate = models.FloatField(_(u"Rate"), default=0)
    description = models.TextField(_(u"Description"), blank=True)

    class Meta:
        app_label = 'customer_tax'
