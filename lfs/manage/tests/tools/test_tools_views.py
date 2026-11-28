"""The tools of the management, tested through real requests as a shop manager: each tool does its job on real data
and returns to the tools page with a message."""

import pytest
from django.contrib.messages import get_messages
from django.core.cache import cache
from django.urls import reverse

from lfs.catalog.models import Category, Product
from lfs.marketing.models import ProductSales
from lfs.order.models import Order, OrderItem
from lfs.addresses.models import Address

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def run_tool(manager, url_name: str) -> list[str]:
    """Run a tool and return the messages; the tool must return to the tools page."""
    response = manager.get(reverse(url_name))
    assert response["Location"] == reverse("lfs_manage_tools")
    return [str(m) for m in get_messages(response.wsgi_request)]


def test_tools_page_links_every_tool(manager):
    urls = [u["url"] for u in manager.get(reverse("lfs_manage_tools")).context["utilities"]]

    assert urls == [
        reverse("lfs_manage_clear_cache"),
        reverse("lfs_manage_set_category_levels"),
        reverse("lfs_manage_reindex_topseller"),
        reverse("lfs_manage_update_effective_price"),
    ]


def test_clear_cache_empties_the_cache(manager):
    cache.set("some-key", "some value")

    assert run_tool(manager, "lfs_manage_clear_cache") == ["Cache has been cleared."]
    assert cache.get("some-key") is None


def test_set_category_levels_sets_the_depth_of_each_category(manager):
    top = Category.objects.create(name="Top", slug="top", level=7)
    middle = Category.objects.create(name="Middle", slug="middle", parent=top, level=7)
    bottom = Category.objects.create(name="Bottom", slug="bottom", parent=middle, level=7)

    assert run_tool(manager, "lfs_manage_set_category_levels") == ["Category levels have been created."]
    assert [Category.objects.get(pk=c.pk).level for c in (top, middle, bottom)] == [1, 2, 3]


def test_reindex_topseller_counts_the_sold_amount_per_product_and_variants_for_their_parent(manager):
    lamp = Product.objects.create(name="Lamp", slug="lamp", sub_type="1")
    red_lamp = Product.objects.create(name="Red lamp", slug="red-lamp", sub_type="2", parent=lamp)
    chair = Product.objects.create(name="Chair", slug="chair")
    address = Address.objects.create()
    order = Order.objects.create(invoice_address=address, shipping_address=address)
    OrderItem.objects.create(order=order, product=lamp, product_amount=2)
    OrderItem.objects.create(order=order, product=red_lamp, product_amount=3)
    OrderItem.objects.create(order=order, product=chair, product_amount=1)
    ProductSales.objects.create(product=chair, sales=99)

    assert run_tool(manager, "lfs_manage_reindex_topseller") == ["Topseller have been reindexed."]
    assert dict(ProductSales.objects.values_list("product__slug", "sales")) == {"lamp": 5, "chair": 1}


def test_update_effective_price_takes_the_sale_price_when_the_product_is_for_sale(manager):
    on_sale = Product.objects.create(name="Lamp", slug="lamp", price=100, for_sale=True, for_sale_price=80)
    regular = Product.objects.create(name="Chair", slug="chair", price=50)
    Product.objects.update(effective_price=0)

    assert run_tool(manager, "lfs_manage_update_effective_price") == ["Effective prices have been set."]
    assert Product.objects.get(pk=on_sale.pk).effective_price == 80
    assert Product.objects.get(pk=regular.pk).effective_price == 50
