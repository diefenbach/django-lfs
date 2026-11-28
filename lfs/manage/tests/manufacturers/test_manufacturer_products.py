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
