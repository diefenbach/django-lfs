# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Tax(models.Model):
    """
    """
    rate = models.FloatField(_(u"Rate"), default=0)
    description = models.TextField(_(u"Description"), blank=True)
    
    def __unicode__(self):
        return "%s%%" % self.rate