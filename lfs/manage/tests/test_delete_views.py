"""Deleting in the management interface: only a POST (the confirmation modal's form) deletes, a GET never does, and
what has to be tidied up after a deletion is tidied up."""

from collections.abc import Callable

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.urls import reverse
from reviews.models import Review

from lfs.caching.utils import get_cache_group_id, lfs_get_object_or_404
from lfs.cart.models import Cart
from lfs.catalog.models import Category, DeliveryTime, Product, Property, PropertyGroup
from lfs.customer_tax.models import CustomerTax
from lfs.discounts.models import Discount
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


def _product(request: pytest.FixtureRequest) -> Product:
    """Create a product."""
    return Product.objects.create(name="Lamp", slug="lamp")


def _review(request: pytest.FixtureRequest) -> Review:
    """Create a review of a product."""
    product = _product(request)
    return Review.objects.create(
        content_type=ContentType.objects.get_for_model(Product), content_id=product.id, comment="Fine", score=5
    )


# A function per delete URL that creates an object the URL can delete; fixtures come from the conftest.
OBJECTS: dict[str, Callable[[pytest.FixtureRequest], Model]] = {
    "lfs_manage_delete_action": lambda request: request.getfixturevalue("action"),
    "lfs_manage_delete_cart": lambda request: Cart.objects.create(session="session"),
    "lfs_manage_delete_category": lambda request: request.getfixturevalue("category"),
    "lfs_manage_delete_customer_tax": lambda request: CustomerTax.objects.create(rate=19),
    "lfs_manage_delete_delivery_time": lambda request: request.getfixturevalue("delivery_time"),
    "lfs_manage_delete_discount": lambda request: Discount.objects.create(name="Discount", value=1),
    "lfs_delete_manufacturer": lambda request: request.getfixturevalue("manufacturer"),
    "lfs_manage_delete_order": lambda request: request.getfixturevalue("order"),
    "lfs_delete_page": lambda request: request.getfixturevalue("page"),
    "lfs_manage_delete_payment_method": lambda request: request.getfixturevalue("payment_method"),
    "lfs_delete_tax": lambda request: request.getfixturevalue("tax"),
    "lfs_manage_delete_product": _product,
    "lfs_delete_property": lambda request: Property.objects.create(name="Colour", title="Colour"),
    "lfs_delete_property_group": lambda request: PropertyGroup.objects.create(name="Group"),
    "lfs_delete_review": _review,
    "lfs_manage_delete_shipping_method": lambda request: request.getfixturevalue("shipping_method"),
    "lfs_delete_static_block": lambda request: request.getfixturevalue("static_block"),
    "lfs_delete_voucher_group": lambda request: request.getfixturevalue("voucher_group"),
}


@pytest.fixture
def manager(client, admin_user):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.mark.django_db
@pytest.mark.parametrize("name,kwarg", DELETE_URLS)
def test_get_is_refused_and_deletes_nothing(manager, shop, request, name: str, kwarg: str):
    obj = OBJECTS[name](request)

    response = manager.get(reverse(name, kwargs={kwarg: obj.pk}))

    assert response.status_code == 405
    assert type(obj).objects.filter(pk=obj.pk).exists()


@pytest.mark.django_db
def test_post_deletes_a_product(manager, shop):
    product = Product.objects.create(name="Lamp", slug="lamp")

    response = manager.post(reverse("lfs_manage_delete_product", kwargs={"id": product.id}))

    assert not Product.objects.filter(pk=product.pk).exists()
    assert response["Location"] == reverse("lfs_manage_products_list")


@pytest.mark.django_db
def test_deleting_a_category_renumbers_its_siblings(manager, shop):
    parent = Category.objects.create(name="Parent", slug="parent")
    first, *_ = (
        Category.objects.create(name=name, slug=name.lower(), parent=parent, position=position)
        for name, position in [("A", 10), ("B", 20), ("C", 30)]
    )

    manager.post(reverse("lfs_manage_delete_category", kwargs={"id": first.id}))

    assert list(Category.objects.filter(parent=parent).order_by("position").values_list("name", "position")) == [
        ("B", 10),
        ("C", 20),
    ]


@pytest.mark.django_db
def test_deleting_a_subcategory_moves_its_children_to_the_top_level_in_order(manager, shop):
    """Category.parent is SET_NULL: the children of a deleted category become top-level categories."""
    top = Category.objects.create(name="Top", slug="top", position=10, level=1)
    deleted = Category.objects.create(name="Sub", slug="sub", parent=top, position=10, level=2)
    child = Category.objects.create(name="Child", slug="child", parent=deleted, position=10, level=3)

    manager.post(reverse("lfs_manage_delete_category", kwargs={"id": deleted.id}))

    assert list(Category.objects.filter(parent=None).order_by("position").values_list("name", "position")) == [
        ("Top", 10),
        ("Child", 20),
    ]
    child.refresh_from_db()
    assert child.level == 1, "the category tree shows only level 1 at the top"


@pytest.mark.django_db
def test_deleting_a_property_renumbers_the_others_and_invalidates_the_property_caches(manager, shop):
    first, *_ = (
        Property.objects.create(name=name, title=name, position=position)
        for name, position in [("A", 10), ("B", 20), ("C", 30)]
    )

    version = get_cache_group_id("global-properties-version")

    manager.post(reverse("lfs_delete_property", kwargs={"id": first.id}))

    assert list(Property.objects.order_by("position").values_list("name", "position")) == [("B", 10), ("C", 20)]
    assert get_cache_group_id("global-properties-version") == version + 1, "cached product properties stay stale"


@pytest.mark.django_db
def test_deleting_a_delivery_time_keeps_the_products_and_the_shop_and_clears_their_caches(manager, shop):
    delivery_time = DeliveryTime.objects.create(min=1, max=3)
    product = Product.objects.create(name="Lamp", slug="lamp", delivery_time=delivery_time, order_time=delivery_time)
    shop.delivery_time = delivery_time
    shop.save()

    lfs_get_object_or_404(Product, pk=product.pk)  # the shop caches products like this

    manager.post(reverse("lfs_manage_delete_delivery_time", kwargs={"pk": delivery_time.pk}))

    assert lfs_get_object_or_404(Product, pk=product.pk).delivery_time_id is None, "the cached product is stale"
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
