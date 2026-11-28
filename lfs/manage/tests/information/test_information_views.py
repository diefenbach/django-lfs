"""The environment page of the management lists LFS's version and the other installed apps with theirs."""

import pytest
from django.urls import reverse

from lfs import __version__

pytestmark = pytest.mark.django_db


def test_lists_the_version_and_the_other_apps_by_name(client, admin_user, shop, settings):
    settings.INSTALLED_APPS = [*settings.INSTALLED_APPS]  # the page reads them as they are
    client.force_login(admin_user)

    context = client.get(reverse("lfs_manage_environment")).context
    names = [app["name"] for app in context["apps"]]

    assert context["lfs_version"] == __version__
    assert names == sorted(names)
    assert "lfs_theme" in names
    assert not [n for n in names if n == "lfs" or n.startswith(("lfs.", "django."))]
    assert {app["version"] for app in context["apps"] if app["name"] == "lfs_theme"} != {"N/A"}
