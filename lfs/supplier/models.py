# django imports
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Supplier(models.Model):
    """
    * A supplier holds all shop supplier related information
    * A Supplier is only created by the system administrator
    """

    user = models.ForeignKey(User, models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(_("Slug"), unique=True, max_length=80)
    active = models.BooleanField(default=True)

    class Meta:
        app_label = "supplier"

    def __str__(self):
        return "%s" % (self.name)
