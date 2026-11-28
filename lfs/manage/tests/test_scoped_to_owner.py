"""Tabs that change or delete the images, attachments or prices of one object only touch that object's own: an id of
another product's image or another method's price in the posted form is ignored, so a crafted form cannot reach them."""

import pytest
from django.urls import reverse

from lfs.catalog.models import Image, Product, ProductAttachment
from lfs.payment.models import PaymentMethod, PaymentMethodPrice
from lfs.shipping.models import ShippingMethod, ShippingMethodPrice

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def products(shop) -> tuple[Product, Product]:
    """The product being edited and another one."""
    return Product.objects.create(name="Lamp", slug="lamp"), Product.objects.create(name="Chair", slug="chair")


def tab(name: str, obj) -> str:
    """Return the URL of the management tab ``name`` of ``obj``."""
    return reverse(name, kwargs={"id": obj.id})


def test_images_tab_does_not_delete_another_products_image(manager, products):
    lamp, chair = products
    other = Image.objects.create(content=chair, title="chair.jpg")

    manager.post(tab("lfs_manage_product_images", lamp), {"action": "delete", f"delete-{other.id}": "1"})

    assert Image.objects.filter(pk=other.pk).exists()


def test_images_tab_does_not_change_another_products_image(manager, products):
    lamp, chair = products
    other = Image.objects.create(content=chair, title="chair.jpg")

    manager.post(tab("lfs_manage_product_images", lamp), {"action": "update", f"title-{other.id}": "hacked"})

    other.refresh_from_db()
    assert other.title == "chair.jpg"


def test_images_tab_still_deletes_the_products_own_image(manager, products):
    lamp, _ = products
    own = Image.objects.create(content=lamp, title="lamp.jpg")

    manager.post(tab("lfs_manage_product_images", lamp), {"action": "delete", f"delete-{own.id}": "1"})

    assert not Image.objects.filter(pk=own.pk).exists()


def test_attachments_tab_does_not_delete_another_products_attachment(manager, products):
    lamp, chair = products
    other = ProductAttachment.objects.create(product=chair, title="chair.pdf")

    manager.post(tab("lfs_manage_product_attachments", lamp), {"action": "delete", f"delete-{other.id}": "1"})

    assert ProductAttachment.objects.filter(pk=other.pk).exists()


@pytest.mark.parametrize(
    "method_model,price_model,url_name,fk",
    [
        (PaymentMethod, PaymentMethodPrice, "lfs_manage_payment_method_prices", "payment_method"),
        (ShippingMethod, ShippingMethodPrice, "lfs_manage_shipping_method_prices", "shipping_method"),
    ],
    ids=["payment", "shipping"],
)
class TestPricesOfAnotherMethod:
    def test_are_not_deleted(self, manager, method_model, price_model, url_name: str, fk: str):
        edited, other_method = method_model.objects.create(name="A"), method_model.objects.create(name="B")
        other = price_model.objects.create(**{fk: other_method}, price=3.0)

        manager.post(tab(url_name, edited), {"action": "delete", f"delete-{other.id}": "on"})

        assert price_model.objects.filter(pk=other.pk).exists()

    def test_are_not_changed(self, manager, method_model, price_model, url_name: str, fk: str):
        edited, other_method = method_model.objects.create(name="A"), method_model.objects.create(name="B")
        other = price_model.objects.create(**{fk: other_method}, price=3.0)

        manager.post(tab(url_name, edited), {"action": "update", f"price-{other.id}": "0"})

        other.refresh_from_db()
        assert other.price == 3.0
