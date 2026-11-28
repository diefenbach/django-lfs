"""Add-ons add their own tabs to the product management page through lfs.manage.products.tabs; the core itself knows
no add-on tabs (it used to ship the bulk prices tab, which failed without lfs_bulk_prices)."""

import importlib.util

import pytest
from django.contrib.sessions.backends.db import SessionStore
from django.urls import NoReverseMatch, reverse
from django.views.generic import TemplateView

from lfs.manage.products.tabs import ProductTab, register_product_tab, unregister_product_tab
from lfs.manage.products.views import ProductTabMixin


@pytest.fixture
def tab_template(tmp_path, settings):
    """A template for the add-on tab, found by Django's template loaders."""
    (tmp_path / "addon_tab.html").write_text("<p>Content of the add-on tab</p>")
    settings.TEMPLATES = [{**settings.TEMPLATES[0], "DIRS": [tmp_path, *settings.TEMPLATES[0].get("DIRS", [])]}]
    return "addon_tab.html"


@pytest.fixture
def addon_tab(tab_template):
    """Register an add-on tab, shown only for products whose SKU starts with "ADDON"."""
    tab = ProductTab(
        key="addon",
        label="Add-on tab",
        url_name="lfs_manage_product_seo",
        template=tab_template,
        show=lambda request, product: product.sku.startswith("ADDON"),
    )
    register_product_tab(tab)
    yield tab
    unregister_product_tab(tab.key)


class AddonTabView(ProductTabMixin, TemplateView):
    """What an add-on's tab view looks like."""

    tab_name = "addon"


def test_registered_tab_is_listed_for_matching_products(admin_client, product, addon_tab):
    product.sku = "ADDON-1"
    product.save()

    content = admin_client.get(reverse("lfs_manage_product_data", args=[product.pk])).content.decode()

    assert "Add-on tab" in content
    assert reverse("lfs_manage_product_seo", args=[product.pk]) in content


def test_registered_tab_is_hidden_for_other_products(admin_client, product, addon_tab):
    content = admin_client.get(reverse("lfs_manage_product_data", args=[product.pk])).content.decode()

    assert "Add-on tab" not in content


def test_addon_view_renders_the_registered_template(rf, admin_user, product, addon_tab):
    request = rf.get("/")
    request.user = admin_user
    request.session = SessionStore()

    response = AddonTabView.as_view()(request, id=product.pk)
    response.render()

    assert "Content of the add-on tab" in response.content.decode()


@pytest.mark.skipif(
    importlib.util.find_spec("lfs_bulk_prices") is not None, reason="lfs_bulk_prices is installed and adds the tab"
)
def test_core_has_no_bulk_prices_tab_without_the_addon(admin_client, product):
    with pytest.raises(NoReverseMatch):
        reverse("lfs_manage_product_bulk_prices", args=[product.pk])
    assert admin_client.get(f"/manage/product/{product.pk}/bulk-prices/").status_code == 404
