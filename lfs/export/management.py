from django.db.models.signals import post_migrate
from django.dispatch import receiver

import lfs
from lfs.export.utils import register
from lfs.export.generic import export as export_script


@receiver(post_migrate)
def register_lfs_scripts(sender, **kwargs):
    # don't register our scripts until the table has been created by syncdb
    if sender == lfs.export.models:
        register(export_script, "Generic")
