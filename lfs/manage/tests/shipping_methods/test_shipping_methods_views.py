"""The shipping method management, tested through real requests as a shop manager: the start page, adding a method,
the data tab, the criteria of a method and of its prices, and the prices tab."""

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from lfs.criteria.models import CartPriceCriterion
from lfs.shipping.models import ShippingMethod, ShippingMethodPrice

CART_PRICE = "lfs.criteria.models.CartPriceCriterion"


@pytest.fixture(autouse=True)
def no_shipping_methods(db):
    """Start without the shipping methods the shop fixture brings."""
    ShippingMethod.objects.all().delete()


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def express(db) -> ShippingMethod:
    """A shipping method "Express"."""
    return ShippingMethod.objects.create(name="Express", price=5.0, active=True)


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def url(name: str, pm: ShippingMethod) -> str:
    """Return the URL of the shipping method tab ``name``."""
    return reverse(name, kwargs={"id": pm.id})


def a_cart_price_criterion(operator: int, value: float) -> dict[str, str]:
    """Return the POST data the criteria form sends for one cart price criterion."""
    return {"type-1": CART_PRICE, "operator-1": str(operator), "position-1": "10", "value-1": str(value)}


class TestStartPage:
    def test_opens_the_first_shipping_method_by_name(self, manager):
        ShippingMethod.objects.create(name="Standard")
        courier = ShippingMethod.objects.create(name="Courier")

        response = manager.get(reverse("lfs_manage_shipping_methods"))

        assert response["Location"] == url("lfs_manage_shipping_method", courier)

    def test_without_shipping_methods_shows_the_empty_page(self, manager):
        response = manager.get(reverse("lfs_manage_shipping_methods"))

        assert response["Location"] == reverse("lfs_manage_no_shipping_methods")

    def test_search_filters_the_list(self, manager, express):
        ShippingMethod.objects.create(name="Courier")

        response = manager.get(url("lfs_manage_shipping_method", express) + "?q=expr")

        assert list(response.context["shipping_methods"]) == [express]


class TestAddShippingMethod:
    def test_adds_the_method_and_opens_it(self, manager):
        response = manager.post(reverse("lfs_manage_add_shipping_method"), {"name": "Courier"})

        courier = ShippingMethod.objects.get(name="Courier")
        assert response["Location"] == url("lfs_manage_shipping_method", courier)
        assert messages_of(response) == ["Shipping method has been created."]

    def test_requires_a_name(self, manager):
        response = manager.post(reverse("lfs_manage_add_shipping_method"), {"name": ""})

        assert not ShippingMethod.objects.exists()
        assert "name" in response.context["form"].errors


class TestDataTab:
    def test_saves_the_data(self, manager, express):
        form = manager.get(url("lfs_manage_shipping_method", express)).context["form"]
        data = {n: v for n in form.fields if n != "image" and (v := form[n].value()) is not None and v is not False}
        data.update({"name": "Express (DHL)", "price": "6.5"})

        response = manager.post(url("lfs_manage_shipping_method", express), data)

        express.refresh_from_db()
        assert (express.name, express.price) == ("Express (DHL)", 6.5)
        assert response["Location"] == url("lfs_manage_shipping_method", express)
        assert messages_of(response) == ["Shipping method has been saved."]


class TestCriteriaTab:
    def test_saves_a_criterion_of_the_method(self, manager, express):
        response = manager.post(
            url("lfs_manage_shipping_method_criteria", express),
            a_cart_price_criterion(CartPriceCriterion.LESS_THAN, 500),
        )

        [criterion] = express.get_criteria()
        assert (type(criterion), criterion.operator, criterion.value) == (
            CartPriceCriterion,
            CartPriceCriterion.LESS_THAN,
            500.0,
        )
        assert response["Location"] == url("lfs_manage_shipping_method_criteria", express)

    def test_shows_the_saved_criteria(self, manager, express):
        CartPriceCriterion.objects.create(content=express, operator=CartPriceCriterion.LESS_THAN, value=512)

        content = manager.get(url("lfs_manage_shipping_method_criteria", express)).content.decode()

        assert 'value="512.0"' in content

    def test_shows_the_criteria_of_a_price_in_the_modal(self, manager, express):
        price = ShippingMethodPrice.objects.create(shipping_method=express, price=2.0)
        CartPriceCriterion.objects.create(content=price, operator=CartPriceCriterion.GREATER_THAN, value=123)

        content = manager.get(
            reverse("lfs_manage_shipping_price_criteria", kwargs={"price_id": price.id}), HTTP_HX_REQUEST="true"
        ).content.decode()

        assert 'value="123.0"' in content

    def test_saving_without_criteria_removes_them(self, manager, express):
        CartPriceCriterion.objects.create(content=express, operator=CartPriceCriterion.LESS_THAN, value=500)

        manager.post(url("lfs_manage_shipping_method_criteria", express), {})

        assert express.get_criteria() == []

    def test_saves_a_criterion_of_a_price(self, manager, express):
        price = ShippingMethodPrice.objects.create(shipping_method=express, price=2.0)

        response = manager.post(
            reverse("lfs_manage_save_shipping_price_criteria", kwargs={"price_id": price.id}),
            a_cart_price_criterion(CartPriceCriterion.GREATER_THAN, 100),
            HTTP_HX_REQUEST="true",
        )

        [criterion] = price.get_criteria()
        assert (criterion.operator, criterion.value) == (CartPriceCriterion.GREATER_THAN, 100.0)
        assert response["HX-Redirect"] == url("lfs_manage_shipping_method_prices", express)


class TestPricesTab:
    def test_lists_the_prices(self, manager, express):
        price = ShippingMethodPrice.objects.create(shipping_method=express, price=2.0)

        assert list(manager.get(url("lfs_manage_shipping_method_prices", express)).context["prices"]) == [price]

    def test_adds_a_price(self, manager, express):
        response = manager.post(url("lfs_manage_shipping_method_prices", express), {"add_price": "1", "price": "2.5"})

        assert [p.price for p in express.prices.all()] == [2.5]
        assert messages_of(response) == ["Price has been added"]

    @pytest.mark.parametrize("price", ["-1", "inf"])
    def test_refuses_a_negative_or_infinite_price(self, manager, express, price: str):
        response = manager.post(url("lfs_manage_shipping_method_prices", express), {"add_price": "1", "price": price})

        assert not express.prices.exists()
        assert messages_of(response) in (["Price cannot be negative"], ["Invalid price value"])

    def test_updates_prices_and_renumbers_their_priorities(self, manager, express):
        first = ShippingMethodPrice.objects.create(shipping_method=express, price=1.0, priority=10)
        second = ShippingMethodPrice.objects.create(shipping_method=express, price=2.0, priority=20)

        manager.post(
            url("lfs_manage_shipping_method_prices", express),
            {"action": "update", f"price-{first.id}": "3", f"priority-{first.id}": "30", f"price-{second.id}": "4"},
        )

        assert [(p.id, p.price, p.priority) for p in express.prices.all()] == [
            (second.id, 4.0, 10),
            (first.id, 3.0, 20),
        ]

    def test_deletes_selected_prices(self, manager, express):
        keep = ShippingMethodPrice.objects.create(shipping_method=express, price=1.0)
        delete = ShippingMethodPrice.objects.create(shipping_method=express, price=2.0)

        response = manager.post(
            url("lfs_manage_shipping_method_prices", express), {"action": "delete", f"delete-{delete.id}": "on"}
        )

        assert list(express.prices.all()) == [keep]
        assert messages_of(response) == ["Prices have been deleted"]


def test_delete_confirmation_names_the_method(manager, express):
    content = manager.get(url("lfs_manage_delete_shipping_method_confirm", express)).content.decode()

    assert "Express" in content


def test_the_shipping_menu_entry_opens_the_first_method(manager, express):
    assert manager.get(reverse("lfs_manage_shipping"))["Location"] == url("lfs_manage_shipping_method", express)


def test_deletes_the_method_with_its_prices(manager, express):
    ShippingMethodPrice.objects.create(shipping_method=express, price=2.0)

    response = manager.post(url("lfs_manage_delete_shipping_method", express))

    assert not ShippingMethod.objects.exists() and not ShippingMethodPrice.objects.exists()
    assert response["Location"] == reverse("lfs_manage_shipping_methods")
