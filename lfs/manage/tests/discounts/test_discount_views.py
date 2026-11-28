"""The discount management, tested through real requests as a shop manager: the start page and search, adding,
saving and deleting a discount, its criteria, and assigning products to it with the product filters."""

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from lfs.catalog.models import Category, Product
from lfs.criteria.models import CartPriceCriterion
from lfs.discounts.models import Discount
from lfs.discounts.settings import DISCOUNT_TYPE_ABSOLUTE, DISCOUNT_TYPE_PERCENTAGE
from lfs.manufacturer.models import Manufacturer

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def summer(db) -> Discount:
    """An absolute discount of 10."""
    return Discount.objects.create(name="Summer", value=10.0, type=DISCOUNT_TYPE_ABSOLUTE, active=True)


def tab(name: str, d: Discount) -> str:
    """Return the URL of the discount tab ``name``."""
    return reverse(name, kwargs={"id": d.id})


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


class TestStartPageAndSearch:
    def test_opens_a_discount(self, manager, summer):
        assert manager.get(reverse("lfs_manage_discounts"))["Location"] == tab("lfs_manage_discount", summer)

    def test_without_discounts_shows_the_empty_page(self, manager):
        assert manager.get(reverse("lfs_manage_discounts"))["Location"] == reverse("lfs_manage_no_discounts")

    def test_search_filters_the_list_case_insensitive(self, manager, summer):
        Discount.objects.create(name="Winter", value=5.0)

        response = manager.get(tab("lfs_manage_discount", summer), {"q": "SUM"})

        assert list(response.context["discounts"]) == [summer]


class TestAddSaveDelete:
    def test_adds_a_discount_and_opens_it(self, manager):
        response = manager.post(
            reverse("lfs_manage_add_discount"),
            {"name": "Spring", "value": "15", "type": str(DISCOUNT_TYPE_PERCENTAGE), "sums_up": "on"},
        )

        spring = Discount.objects.get(name="Spring")
        assert (spring.value, spring.type, spring.sums_up) == (15.0, DISCOUNT_TYPE_PERCENTAGE, True)
        assert response["Location"] == tab("lfs_manage_discount", spring)
        assert messages_of(response) == ["Discount has been created."]

    def test_adding_requires_name_value_and_type(self, manager):
        response = manager.post(reverse("lfs_manage_add_discount"), {})

        assert not Discount.objects.exists()
        assert {"name", "value", "type"} <= set(response.context["form"].errors)

    def test_saves_the_data(self, manager, summer):
        response = manager.post(
            tab("lfs_manage_discount", summer),
            {"name": "Summer sale", "value": "12.5", "type": str(DISCOUNT_TYPE_ABSOLUTE), "sku": "SUM-1"},
        )

        summer.refresh_from_db()
        assert (summer.name, summer.value, summer.sku, summer.active) == ("Summer sale", 12.5, "SUM-1", False)
        assert response["Location"] == tab("lfs_manage_discount", summer)
        assert messages_of(response) == ["Discount has been saved."]

    def test_delete_confirmation_names_the_discount(self, manager, summer):
        response = manager.get(tab("lfs_manage_delete_discount_confirm", summer))

        assert response.context["discount"] == summer

    def test_deletes_the_discount(self, manager, summer):
        response = manager.post(tab("lfs_manage_delete_discount", summer))

        assert not Discount.objects.exists()
        assert response["Location"] == reverse("lfs_manage_discounts")


class TestCriteria:
    def test_saves_a_criterion(self, manager, summer):
        response = manager.post(
            tab("lfs_manage_discount_criteria", summer),
            {
                "type-1": "lfs.criteria.models.CartPriceCriterion",
                "operator-1": str(CartPriceCriterion.GREATER_THAN),
                "position-1": "10",
                "value-1": "100",
            },
        )

        [criterion] = summer.get_criteria()
        assert (criterion.operator, criterion.value) == (CartPriceCriterion.GREATER_THAN, 100.0)
        assert response["Location"] == tab("lfs_manage_discount_criteria", summer)

    def test_htmx_save_returns_the_tab_with_the_criteria(self, manager, summer):
        response = manager.post(
            tab("lfs_manage_discount_criteria", summer),
            {
                "type-1": "lfs.criteria.models.CartPriceCriterion",
                "operator-1": str(CartPriceCriterion.GREATER_THAN),
                "position-1": "10",
                "value-1": "123",
            },
            HTTP_HX_REQUEST="true",
        )

        assert 'value="123.0"' in response.content.decode()

    def test_shows_the_saved_criteria(self, manager, summer):
        CartPriceCriterion.objects.create(content=summer, operator=CartPriceCriterion.LESS_THAN, value=512)

        assert 'value="512.0"' in manager.get(tab("lfs_manage_discount_criteria", summer)).content.decode()


class TestProducts:
    @pytest.fixture
    def products(self, shop) -> list[Product]:
        """Three products."""
        return [Product.objects.create(name=n, slug=n.lower()) for n in ("Lamp", "Chair", "Table")]

    def offered(self, manager, summer, **params) -> list[str]:
        """Return the names of the products the tab offers to assign."""
        page = manager.get(tab("lfs_manage_discount_products", summer), params).context["page"]
        return [p.name for p in page.object_list] if page else []

    def test_assigns_products(self, manager, summer, products):
        lamp, chair, _ = products

        response = manager.post(
            tab("lfs_manage_discount_products", summer),
            {"assign_products": "1", f"product-{lamp.id}": "on", f"product-{chair.id}": "on"},
        )

        assert set(summer.products.all()) == {lamp, chair}
        assert messages_of(response) == ["Products have been assigned."]

    def test_removes_products(self, manager, summer, products):
        lamp, chair, _ = products
        summer.products.add(lamp, chair)

        manager.post(tab("lfs_manage_discount_products", summer), {"remove_products": "1", f"product-{chair.id}": "on"})

        assert list(summer.products.all()) == [lamp]

    def test_offers_only_unassigned_products(self, manager, summer, products):
        summer.products.add(products[0])

        assert sorted(self.offered(manager, summer)) == ["Chair", "Table"]

    def test_filters_by_name_category_and_manufacturer(self, manager, summer, products):
        lamp, chair, table = products
        furniture = Category.objects.create(name="Furniture", slug="furniture")
        chairs = Category.objects.create(name="Chairs", slug="chairs", parent=furniture)
        chair.categories.add(chairs)
        acme = Manufacturer.objects.create(name="Acme", slug="acme")
        Product.objects.filter(pk=table.pk).update(manufacturer=acme)

        assert self.offered(manager, summer, filter="lam") == ["Lamp"]
        assert self.offered(manager, summer, products_category_filter=furniture.id) == ["Chair"]
        assert sorted(self.offered(manager, summer, products_category_filter="None")) == ["Lamp", "Table"]
        assert self.offered(manager, summer, products_manufacturer_filter=acme.id) == ["Table"]

    def test_offers_25_products_per_page(self, manager, summer, shop):
        for i in range(30):
            Product.objects.create(name=f"Product {i:02d}", slug=f"product-{i}")

        assert len(self.offered(manager, summer)) == 25
        assert len(self.offered(manager, summer, page=2)) == 5
