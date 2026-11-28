"""The products tab of a manufacturer: a manager assigns products to the manufacturer and removes them again; the tab
lists the assigned products and offers only the others."""

import pytest
from django.urls import reverse

from lfs.catalog.models import Product


@pytest.fixture
def products(db, shop) -> list[Product]:
    """Three products without manufacturer."""
    return [Product.objects.create(name=f"Product {i}", slug=f"product-{i}") for i in (1, 2, 3)]


@pytest.fixture
def manager(client, admin_user):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def tab_url(manufacturer) -> str:
    """Return the URL of the manufacturer's products tab."""
    return reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.id})


def test_assigning_products(manager, manufacturer, products):
    p1, p2, p3 = products

    response = manager.post(
        tab_url(manufacturer), {"assign_products": "1", f"product-{p1.id}": "on", f"product-{p2.id}": "on"}
    )

    assert set(Product.objects.filter(manufacturer=manufacturer)) == {p1, p2}
    assert response["Location"] == tab_url(manufacturer)


def test_removing_products_keeps_the_others(manager, manufacturer, products):
    p1, p2, _ = products
    Product.objects.filter(pk__in=[p1.pk, p2.pk]).update(manufacturer=manufacturer)

    manager.post(tab_url(manufacturer), {"remove_products": "1", f"product-{p2.id}": "on"})

    assert list(Product.objects.filter(manufacturer=manufacturer)) == [p1]


def test_lists_assigned_products_and_offers_only_the_others(manager, manufacturer, products):
    p1, p2, p3 = products
    Product.objects.filter(pk=p1.pk).update(manufacturer=manufacturer)

    context = manager.get(tab_url(manufacturer)).context

    assert list(context["manufacturer_products"]) == [p1]
    assert list(context["page"].object_list) == [p2, p3]


def test_removing_does_not_touch_products_of_another_manufacturer(manager, manufacturer, products):
    """The tab lists only this manufacturer's products; a posted id of another one's product must not change it."""
    from lfs.manufacturer.models import Manufacturer

    other = Manufacturer.objects.create(name="Other", slug="other")
    p1 = products[0]
    Product.objects.filter(pk=p1.pk).update(manufacturer=other)

    manager.post(tab_url(manufacturer), {"remove_products": "1", f"product-{p1.id}": "on"})

    assert Product.objects.get(pk=p1.pk).manufacturer == other


def test_unknown_ids_are_ignored(manager, manufacturer, products):
    response = manager.post(tab_url(manufacturer), {"assign_products": "1", "product-999999": "on", "product-x": "on"})

    assert response["Location"] == tab_url(manufacturer)


def test_offers_products_filtered_by_name_and_category_with_its_subcategories(manager, manufacturer, products):
    from lfs.catalog.models import Category

    lights = Category.objects.create(name="Lights", slug="lights")
    lamps = Category.objects.create(name="Lamps", slug="lamps", parent=lights)
    desk_lamp = Product.objects.create(name="Desk lamp", slug="desk-lamp")
    desk_lamp.categories.add(lamps)
    Product.objects.create(name="Lamp shade", slug="lamp-shade")

    by_category = manager.get(tab_url(manufacturer), {"filter": "lamp", "products_category_filter": lights.id})
    without_category = manager.get(tab_url(manufacturer), {"filter": "lamp", "products_category_filter": "None"})

    assert list(by_category.context["page"].object_list) == [desk_lamp]
    assert [p.name for p in without_category.context["page"].object_list] == ["Lamp shade"]


def test_paging_keeps_the_filter_in_the_session(manager, manufacturer, products):
    for i in range(26):
        Product.objects.create(name=f"Lamp {i:02d}", slug=f"lamp-{i}")
    manager.get(tab_url(manufacturer), {"filter": "lamp"})

    page = manager.get(tab_url(manufacturer), {"page": 2}).context["page"]

    assert [p.name for p in page.object_list] == ["Lamp 25"]
    assert manager.get(tab_url(manufacturer), {"page": 9}).context["page"] == 0
