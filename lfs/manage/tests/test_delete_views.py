"""Deleting in the management interface: only a POST (the confirmation modal's form) deletes, a GET never does, and
what has to be tidied up after a deletion is tidied up."""

import pytest
from django.urls import reverse

from lfs.caching.utils import get_cache_group_id
from lfs.catalog.models import Category, DeliveryTime, Product, Property
from lfs.customer.models import Customer

# Every delete URL of the management interface with the keyword of its id.
DELETE_URLS = [
    ("lfs_manage_delete_action", "pk"),
    ("lfs_manage_delete_cart", "id"),
    ("lfs_manage_delete_category", "id"),
    ("lfs_manage_delete_customer_tax", "id"),
    ("lfs_manage_delete_delivery_time", "pk"),
    ("lfs_manage_delete_discount", "id"),
    ("lfs_delete_manufacturer", "id"),
    ("lfs_manage_delete_order", "order_id"),
    ("lfs_delete_page", "id"),
    ("lfs_manage_delete_payment_method", "id"),
    ("lfs_delete_tax", "pk"),
    ("lfs_manage_delete_product", "id"),
    ("lfs_delete_property", "id"),
    ("lfs_delete_property_group", "id"),
    ("lfs_delete_review", "id"),
    ("lfs_manage_delete_shipping_method", "id"),
    ("lfs_delete_static_block", "id"),
    ("lfs_delete_voucher_group", "id"),
]


@pytest.fixture
def manager(client, admin_user):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.mark.django_db
@pytest.mark.parametrize("name,kwarg", DELETE_URLS)
def test_get_is_refused(manager, name: str, kwarg: str):
    response = manager.get(reverse(name, kwargs={kwarg: 1}))

    assert response.status_code == 405


@pytest.mark.django_db
def test_get_does_not_delete_a_product(manager, shop):
    product = Product.objects.create(name="Lamp", slug="lamp")

    manager.get(reverse("lfs_manage_delete_product", kwargs={"id": product.id}))

    assert Product.objects.filter(pk=product.pk).exists()


@pytest.mark.django_db
def test_post_deletes_a_product(manager, shop):
    product = Product.objects.create(name="Lamp", slug="lamp")

    response = manager.post(reverse("lfs_manage_delete_product", kwargs={"id": product.id}))

    assert not Product.objects.filter(pk=product.pk).exists()
    assert response["Location"] == reverse("lfs_manage_products_list")


@pytest.mark.django_db
def test_deleting_a_category_renumbers_its_siblings(manager, shop):
    parent = Category.objects.create(name="Parent", slug="parent")
    first, second, third = (
        Category.objects.create(name=name, slug=name.lower(), parent=parent, position=position)
        for name, position in [("A", 10), ("B", 20), ("C", 30)]
    )

    manager.post(reverse("lfs_manage_delete_category", kwargs={"id": first.id}))

    assert list(Category.objects.filter(parent=parent).order_by("position").values_list("name", "position")) == [
        ("B", 10),
        ("C", 20),
    ]


@pytest.mark.django_db
def test_deleting_a_property_renumbers_the_others_and_invalidates_the_property_caches(manager, shop):
    first, second, third = (
        Property.objects.create(name=name, title=name, position=position)
        for name, position in [("A", 10), ("B", 20), ("C", 30)]
    )

    version = get_cache_group_id("global-properties-version")

    manager.post(reverse("lfs_delete_property", kwargs={"id": first.id}))

    assert list(Property.objects.order_by("position").values_list("name", "position")) == [("B", 10), ("C", 20)]
    assert get_cache_group_id("global-properties-version") == version + 1, "cached product properties stay stale"


@pytest.mark.django_db
def test_deleting_a_delivery_time_keeps_the_products_and_the_shop(manager, shop):
    delivery_time = DeliveryTime.objects.create(min=1, max=3)
    product = Product.objects.create(name="Lamp", slug="lamp", delivery_time=delivery_time, order_time=delivery_time)
    shop.delivery_time = delivery_time
    shop.save()

    manager.post(reverse("lfs_manage_delete_delivery_time", kwargs={"pk": delivery_time.pk}))

    product.refresh_from_db()
    shop.refresh_from_db()
    assert (product.delivery_time, product.order_time, shop.delivery_time) == (None, None, None)


@pytest.mark.django_db
def test_deleting_a_payment_method_keeps_the_customers_who_chose_it(manager, shop, customer, payment_method):
    customer.selected_payment_method = payment_method
    customer.save()

    manager.post(reverse("lfs_manage_delete_payment_method", kwargs={"id": payment_method.id}))

    assert Customer.objects.get(pk=customer.pk).selected_payment_method is None


@pytest.mark.django_db
def test_deleting_a_shipping_method_keeps_the_customers_who_chose_it(manager, shop, customer, shipping_method):
    customer.selected_shipping_method = shipping_method
    customer.save()

    manager.post(reverse("lfs_manage_delete_shipping_method", kwargs={"id": shipping_method.id}))

    assert Customer.objects.get(pk=customer.pk).selected_shipping_method is None
