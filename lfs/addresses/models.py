"""W
# django imports
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lfs.core.models import Country

class Address(models.Model):
    firstname = models.CharField(_("Firstname"), max_length=50)
    lastname = models.CharField(_("Lastname"), max_length=50)
    line1 = models.CharField(_("Line 1"), max_length=100, blank=True, null=True)
    line2 = models.CharField(_("Line 2"), max_length=100, blank=True, null=True)
    line3 = models.CharField(_("Line 3"), max_length=100, blank=True, null=True)
    line4 = models.CharField(_("Line 4"), max_length=100, blank=True, null=True)
    line5 = models.CharField(_("Line 5"), max_length=100, blank=True, null=True)
    country = models.ForeignKey(Country, verbose_name=_("Country"), blank=True, null=True, related_name="Country Address")
    mobile = models.CharField(_("Mobile"), null=True, blank=True, max_length=20)
    phone = models.CharField(_("Phone"), null=True, blank=True, max_length=20)
    email = models.EmailField(_("E-Mail"), blank=True, null=True, max_length=50)

    def __unicode__(self):
        return "%s / %s" % (self.line1, self.line2, self.country)
    
"""