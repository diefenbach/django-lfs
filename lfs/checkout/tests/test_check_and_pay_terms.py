"""Both checkouts (check and pay, one page) place an order only after the customer confirms the terms, if the shop
asks for it."""

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse

from lfs.addresses.models import Address
from lfs.cart.models import Cart, CartItem
from lfs.catalog.models import Product
from lfs.core.models import Country
from lfs.core.utils import get_default_shop
from lfs.customer.models import Customer
from lfs.order.models import Order
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import BY_INVOICE
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax


@pytest.fixture
def customer_client(client, db):
    """A logged-in customer with addresses, shipping and payment chosen, and one product in the cart."""
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    tax = Tax.objects.create(rate=19)
    address = Address.objects.create(
        firstname="John",
        lastname="Doe",
        line1="Street 42",
        city="Gotham",
        zip_code="2342",
        country=Country.objects.get(code="de"),
    )
    user = User.objects.create_user(username="joe", password="bloggs", email="joe@example.com")
    Customer.objects.create(
        user=user,
        selected_shipping_method=ShippingMethod.objects.create(name="Standard", active=True, price=1, tax=tax),
        selected_payment_method=PaymentMethod.objects.get(pk=BY_INVOICE),
        selected_invoice_address=address,
        selected_shipping_address=address,
    )
    product = Product.objects.create(name="Spade", slug="spade", price=10, tax=tax, active=True)
    CartItem.objects.create(cart=Cart.objects.create(user=user), product=product, amount=1)
    client.login(username="joe", password="bloggs")
    return client


@pytest.fixture
def shop_requires_terms(db):
    """Set whether the default shop asks customers to confirm its terms."""

    def require(confirm_toc: bool) -> None:
        shop = get_default_shop()
        shop.confirm_toc = confirm_toc
        shop.save()

    return require


def test_order_is_refused_without_confirmed_terms(customer_client, shop_requires_terms):
    shop_requires_terms(True)

    response = customer_client.post(reverse("lfs_checkout_check_and_pay"), {})

    assert Order.objects.count() == 0
    assert "confirm_toc" in response.context["checkout_form"].errors


def test_order_is_placed_with_confirmed_terms(customer_client, shop_requires_terms):
    shop_requires_terms(True)

    response = customer_client.post(reverse("lfs_checkout_check_and_pay"), {"confirm_toc": "on"})

    assert Order.objects.count() == 1
    assert response["Location"] == reverse("lfs_thank_you")


def test_order_is_placed_without_confirmation_when_the_shop_does_not_ask(customer_client, shop_requires_terms):
    shop_requires_terms(False)

    customer_client.post(reverse("lfs_checkout_check_and_pay"), {})

    assert Order.objects.count() == 1


def test_one_page_checkout_asks_for_the_terms_too(customer_client, shop_requires_terms):
    shop_requires_terms(True)

    response = customer_client.post(reverse("lfs_checkout"), {})

    assert Order.objects.count() == 0
    assert "confirm_toc" in response.context["checkout_form"].errors
