# django imports
from django.db import models


class ActiveManager(models.Manager):
    """An extended manager to return active objects.
    """
    def active(self):
        return super(ActiveManager, self).get_queryset().filter(active=True)
