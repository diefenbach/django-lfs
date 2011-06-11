# django imports
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CriteriaObjects(models.Model):
    """Assigns arbitrary criteria to arbitrary content objects.
    """
    class Meta:
        ordering = ["position"]
        verbose_name_plural = "Criteria objects"
        app_label = "criteria"

    criterion_type = models.ForeignKey(ContentType, verbose_name=_(u"Criterion type"), related_name="criterion")
    criterion_id = models.PositiveIntegerField(_(u"Content id"))
    criterion = generic.GenericForeignKey(ct_field="criterion_type", fk_field="criterion_id")

    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"), related_name="content_type")
    content_id = models.PositiveIntegerField(_(u"Content id"))
    content = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")

    position = models.PositiveIntegerField(_(u"Position"), default=999)
