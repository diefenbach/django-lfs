# django imports
from django.db.models.signals import post_migrate

# lfs imports
from lfs.export.utils import register
from lfs.export.generic import export as export_script
from lfs.export.models import Script
import lfs


def register_lfs_scripts(sender, **kwargs):
    # don't register our scripts until the table has been created by syncdb
    if sender == lfs.export.models:
        register(export_script, "Generic")
post_migrate.connect(register_lfs_scripts)
