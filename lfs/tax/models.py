# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Tax(models.Model):
    """Represent a tax rate.

    **Attributes**:

    rate
        The tax rate in percent.

    description
        The description of the tax rate.
    """
    rate = models.FloatField(_(u"Rate"), default=0)
    description = models.TextField(_(u"Description"), blank=True)

    def __unicode__(self):
        return "%s%%" % self.rate
