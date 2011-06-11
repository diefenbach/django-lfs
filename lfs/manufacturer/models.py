# django imports
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Manufacturer(models.Model):
    """The manufacturer is the unique creator of a product.
    """
    name = models.CharField(_(u"Name"), max_length=50)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the absolute url of the manufacturer
        """
        return reverse("lfs_manufacturer", kwargs={"manufacturer_id": self.id})
