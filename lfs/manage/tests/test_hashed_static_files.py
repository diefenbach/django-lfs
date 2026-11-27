"""The management interface works with content-hashed static file names (ManifestStaticFilesStorage), which shops
use in production: every {% static %} name must be a real file, since the manifest has no entry for anything else."""

import pytest
from django.core.management import call_command
from django.urls import reverse

MANIFEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
}


@pytest.fixture
def hashed_static_files(settings, tmp_path):
    """Collect the static files with hashed names into a temporary STATIC_ROOT and serve them from there."""
    settings.STATIC_ROOT = tmp_path
    settings.STORAGES = MANIFEST_STORAGES
    call_command("collectstatic", interactive=False, verbosity=0)


def test_dashboard_renders_with_hashed_static_files(authenticated_client, hashed_static_files):
    response = authenticated_client.get(reverse("lfs_manage_dashboard"))

    assert response.status_code == 200
    assert "var STATIC_URL = '/static/';" in response.content.decode()
