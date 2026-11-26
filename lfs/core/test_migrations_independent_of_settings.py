"""LFS's migrations must not depend on a shop's settings (price calculators, units, payment modules, order states).

Otherwise every shop with other settings sees a pending migration, and makemigrations would write one into the
installed django-lfs package.
"""

import pytest
from django.core.management import call_command

LFS_APPS_WITH_SETTINGS_CHOICES = ["catalog", "core", "order", "payment", "shipping"]


@pytest.mark.django_db
def test_lfs_has_no_pending_migrations_with_this_projects_settings(settings):
    settings.MIGRATION_MODULES = {}  # use the real migrations, also when the tests run with --nomigrations
    call_command("makemigrations", *LFS_APPS_WITH_SETTINGS_CHOICES, check=True, dry_run=True, verbosity=0)
