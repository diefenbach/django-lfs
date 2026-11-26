"""A project can leave out LFS's settings: LFS then uses its defaults (lfs.settings.DEFAULTS)."""

import pytest
from django.core.management import call_command
from django.urls import reverse

from lfs.catalog.models import Product
from lfs.settings import DEFAULTS, lfs_setting


@pytest.fixture
def without_lfs_settings(settings):
    """Remove every LFS setting that has a default from the project's settings."""
    for name in DEFAULTS:
        if hasattr(settings, name):
            delattr(settings, name)


@pytest.fixture
def shop(db):
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    return Product.objects.create(name="Spade", slug="spade", price=10, active=True)


def test_lfs_setting_prefers_the_project_setting(settings):
    settings.LFS_RECENT_PRODUCTS_LIMIT = 9
    assert lfs_setting("LFS_RECENT_PRODUCTS_LIMIT") == 9


def test_lfs_setting_falls_back_to_the_default(without_lfs_settings):
    assert lfs_setting("LFS_RECENT_PRODUCTS_LIMIT") == 5
    assert lfs_setting("LFS_ORDER_NUMBER_GENERATOR") == "lfs_order_numbers.models.OrderNumberGenerator"


def test_shop_works_without_lfs_settings(client, shop, without_lfs_settings):
    assert client.get(reverse("lfs_product", kwargs={"slug": "spade"})).status_code == 200

    response = client.post(reverse("lfs_add_to_cart"), {"product_id": shop.id, "quantity": "1", "action": "add-to-cart"})
    assert response.status_code == 302
    assert response["Location"] == reverse("lfs_added_to_cart")


def test_management_works_without_lfs_settings(admin_client, shop, without_lfs_settings):
    assert admin_client.get(reverse("lfs_manage_shop_order_numbers")).status_code == 200
    assert "CartPriceCriterion" in admin_client.get(reverse("lfs_manage_add_criterion")).content.decode()

