"""The payment method management, tested through real requests as a shop manager: the start page, adding a method,
the data tab, the criteria of a method and of its prices, and the prices tab."""

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from lfs.criteria.models import CartPriceCriterion
from lfs.payment.models import PaymentMethod, PaymentMethodPrice

CART_PRICE = "lfs.criteria.models.CartPriceCriterion"


@pytest.fixture(autouse=True)
def no_payment_methods(db):
    """Start without the payment methods the shop fixture brings."""
    PaymentMethod.objects.all().delete()


@pytest.fixture
def manager(client, admin_user):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def cod(db) -> PaymentMethod:
    """A payment method "Cash on delivery"."""
    return PaymentMethod.objects.create(name="Cash on delivery", price=5.0, active=True)


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def url(name: str, pm: PaymentMethod) -> str:
    """Return the URL of the payment method tab ``name``."""
    return reverse(name, kwargs={"id": pm.id})


def a_cart_price_criterion(operator: int, value: float) -> dict[str, str]:
    """Return the POST data the criteria form sends for one cart price criterion."""
    return {"type-1": CART_PRICE, "operator-1": str(operator), "position-1": "10", "value-1": str(value)}


class TestStartPage:
    def test_opens_the_first_payment_method_by_name(self, manager):
        PaymentMethod.objects.create(name="Prepayment")
        invoice = PaymentMethod.objects.create(name="Invoice")

        response = manager.get(reverse("lfs_manage_payment_methods"))

        assert response["Location"] == url("lfs_manage_payment_method", invoice)

    def test_without_payment_methods_shows_the_empty_page(self, manager):
        response = manager.get(reverse("lfs_manage_payment_methods"))

        assert response["Location"] == reverse("lfs_manage_no_payment_methods")

    def test_search_filters_the_list(self, manager, cod):
        PaymentMethod.objects.create(name="Invoice")

        response = manager.get(url("lfs_manage_payment_method", cod) + "?q=cash")

        assert list(response.context["payment_methods"]) == [cod]


class TestAddPaymentMethod:
    def test_adds_the_method_and_opens_it(self, manager):
        response = manager.post(reverse("lfs_manage_add_payment_method"), {"name": "Invoice"})

        invoice = PaymentMethod.objects.get(name="Invoice")
        assert response["Location"] == url("lfs_manage_payment_method", invoice)
        assert messages_of(response) == ["Payment method has been created."]

    def test_requires_a_name(self, manager):
        response = manager.post(reverse("lfs_manage_add_payment_method"), {"name": ""})

        assert not PaymentMethod.objects.exists()
        assert "name" in response.context["form"].errors


class TestDataTab:
    def test_saves_the_data(self, manager, cod):
        form = manager.get(url("lfs_manage_payment_method", cod)).context["form"]
        data = {n: v for n in form.fields if n != "image" and (v := form[n].value()) is not None and v is not False}
        data.update({"name": "Cash on delivery (DHL)", "price": "6.5"})

        response = manager.post(url("lfs_manage_payment_method", cod), data)

        cod.refresh_from_db()
        assert (cod.name, cod.price) == ("Cash on delivery (DHL)", 6.5)
        assert response["Location"] == url("lfs_manage_payment_method", cod)
        assert messages_of(response) == ["Payment method has been saved."]


class TestCriteriaTab:
    def test_saves_a_criterion_of_the_method(self, manager, cod):
        response = manager.post(
            url("lfs_manage_payment_method_criteria", cod), a_cart_price_criterion(CartPriceCriterion.LESS_THAN, 500)
        )

        [criterion] = cod.get_criteria()
        assert (type(criterion), criterion.operator, criterion.value) == (
            CartPriceCriterion,
            CartPriceCriterion.LESS_THAN,
            500.0,
        )
        assert response["Location"] == url("lfs_manage_payment_method_criteria", cod)

    def test_shows_the_saved_criteria(self, manager, cod):
        CartPriceCriterion.objects.create(content=cod, operator=CartPriceCriterion.LESS_THAN, value=512)

        content = manager.get(url("lfs_manage_payment_method_criteria", cod)).content.decode()

        assert 'value="512.0"' in content

    def test_shows_the_criteria_of_a_price_in_the_modal(self, manager, cod):
        price = PaymentMethodPrice.objects.create(payment_method=cod, price=2.0)
        CartPriceCriterion.objects.create(content=price, operator=CartPriceCriterion.GREATER_THAN, value=123)

        content = manager.get(
            reverse("lfs_manage_payment_price_criteria", kwargs={"price_id": price.id}), HTTP_HX_REQUEST="true"
        ).content.decode()

        assert 'value="123.0"' in content

    def test_saving_without_criteria_removes_them(self, manager, cod):
        CartPriceCriterion.objects.create(content=cod, operator=CartPriceCriterion.LESS_THAN, value=500)

        manager.post(url("lfs_manage_payment_method_criteria", cod), {})

        assert cod.get_criteria() == []

    def test_saves_a_criterion_of_a_price(self, manager, cod):
        price = PaymentMethodPrice.objects.create(payment_method=cod, price=2.0)

        response = manager.post(
            reverse("lfs_manage_save_payment_price_criteria", kwargs={"price_id": price.id}),
            a_cart_price_criterion(CartPriceCriterion.GREATER_THAN, 100),
            HTTP_HX_REQUEST="true",
        )

        [criterion] = price.get_criteria()
        assert (criterion.operator, criterion.value) == (CartPriceCriterion.GREATER_THAN, 100.0)
        assert response["HX-Redirect"] == url("lfs_manage_payment_method_prices", cod)


class TestPricesTab:
    def test_lists_the_prices(self, manager, cod):
        price = PaymentMethodPrice.objects.create(payment_method=cod, price=2.0)

        assert list(manager.get(url("lfs_manage_payment_method_prices", cod)).context["prices"]) == [price]

    def test_adds_a_price(self, manager, cod):
        response = manager.post(url("lfs_manage_payment_method_prices", cod), {"add_price": "1", "price": "2.5"})

        assert [p.price for p in cod.prices.all()] == [2.5]
        assert messages_of(response) == ["Price has been added"]

    @pytest.mark.parametrize("price", ["-1", "inf"])
    def test_refuses_a_negative_or_infinite_price(self, manager, cod, price: str):
        response = manager.post(url("lfs_manage_payment_method_prices", cod), {"add_price": "1", "price": price})

        assert not cod.prices.exists()
        assert messages_of(response) in (["Price cannot be negative"], ["Invalid price value"])

    def test_updates_prices_and_renumbers_their_priorities(self, manager, cod):
        first = PaymentMethodPrice.objects.create(payment_method=cod, price=1.0, priority=10)
        second = PaymentMethodPrice.objects.create(payment_method=cod, price=2.0, priority=20)

        manager.post(
            url("lfs_manage_payment_method_prices", cod),
            {"action": "update", f"price-{first.id}": "3", f"priority-{first.id}": "30", f"price-{second.id}": "4"},
        )

        assert [(p.id, p.price, p.priority) for p in cod.prices.all()] == [(second.id, 4.0, 10), (first.id, 3.0, 20)]

    def test_deletes_selected_prices(self, manager, cod):
        keep = PaymentMethodPrice.objects.create(payment_method=cod, price=1.0)
        delete = PaymentMethodPrice.objects.create(payment_method=cod, price=2.0)

        response = manager.post(
            url("lfs_manage_payment_method_prices", cod), {"action": "delete", f"delete-{delete.id}": "on"}
        )

        assert list(cod.prices.all()) == [keep]
        assert messages_of(response) == ["Prices have been deleted"]


def test_delete_confirmation_names_the_method(manager, cod):
    content = manager.get(url("lfs_manage_delete_payment_method_confirm", cod)).content.decode()

    assert "Cash on delivery" in content
