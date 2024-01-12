# django imports
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tax(models.Model):
    """Represent a tax rate.

    **Attributes**:

    rate
        The tax rate in percent.

    description
        The description of the tax rate.
    """

    rate = models.FloatField(_("Rate"), default=0)
    description = models.TextField(_("Description"), blank=True)

    def __str__(self):
        return "%s%%" % self.rate

    class Meta:
        app_label = "tax"
