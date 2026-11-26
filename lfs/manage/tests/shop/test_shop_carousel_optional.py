"""The shop management works without the optional lfs_carousel add-on and shows its tab only when installed."""

import pytest
from django.conf import settings
from django.test import override_settings
from django.urls import reverse

WITHOUT_CAROUSEL = [app for app in settings.INSTALLED_APPS if app != "lfs_carousel"]

requires_carousel = pytest.mark.skipif(
    "lfs_carousel" not in settings.INSTALLED_APPS, reason="needs the lfs_carousel add-on"
)


@pytest.fixture
def manage_client(client, manage_user):
    client.force_login(manage_user)
    return client


@pytest.mark.django_db
@override_settings(INSTALLED_APPS=WITHOUT_CAROUSEL)
def test_shop_data_tab_renders_without_carousel(manage_client, shop):
    response = manage_client.get(reverse("lfs_manage_shop_data"))

    assert response.status_code == 200
    assert reverse("lfs_manage_shop_carousel") not in response.content.decode()


@pytest.mark.django_db
@override_settings(INSTALLED_APPS=WITHOUT_CAROUSEL)
def test_carousel_tab_is_not_found_without_carousel(manage_client, shop):
    response = manage_client.get(reverse("lfs_manage_shop_carousel"))

    assert response.status_code == 404


@requires_carousel
@pytest.mark.django_db
def test_shop_data_tab_links_carousel_when_installed(manage_client, shop):
    response = manage_client.get(reverse("lfs_manage_shop_data"))

    assert response.status_code == 200
    assert reverse("lfs_manage_shop_carousel") in response.content.decode()


@requires_carousel
@pytest.mark.django_db
def test_carousel_tab_renders_when_installed(manage_client, shop):
    response = manage_client.get(reverse("lfs_manage_shop_carousel"))

    assert response.status_code == 200
