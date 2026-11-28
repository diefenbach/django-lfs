"""The customer tax management, tested through real requests as a shop manager: the list and its search, adding,
saving, the criteria that decide when a tax applies, and deleting. Which rate a customer gets is tested in
lfs/customer_tax/tests.py."""

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from lfs.criteria.models import CartPriceCriterion, Criterion
from lfs.customer_tax.models import CustomerTax

pytestmark = pytest.mark.django_db

CART_PRICE = "lfs.criteria.models.CartPriceCriterion"


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


class TestStartAndList:
    def test_shows_the_tax_with_the_lowest_rate(self, manager):
        CustomerTax.objects.create(rate=19)
        low = CustomerTax.objects.create(rate=7)

        assert manager.get(reverse("lfs_manage_customer_taxes"))["Location"] == reverse(
            "lfs_manage_customer_tax", kwargs={"id": low.id}
        )

    def test_without_taxes_shows_the_empty_page(self, manager):
        assert manager.get(reverse("lfs_manage_customer_taxes"))["Location"] == reverse("lfs_manage_no_customer_taxes")

    def test_search_finds_by_rate_or_description_and_the_tabs_keep_it(self, manager):
        eu = CustomerTax.objects.create(rate=19, description="EU customers")
        CustomerTax.objects.create(rate=0, description="Export")
        url = reverse("lfs_manage_customer_tax", kwargs={"id": eu.id})

        by_rate = manager.get(url, {"q": "19"}).context
        by_description = manager.get(url, {"q": "eu cus"}).context

        assert list(by_rate["customer_taxes"]) == [eu]
        assert list(by_description["customer_taxes"]) == [eu]
        assert all(u.endswith("?q=eu+cus") for _, u in by_description["tabs"])


class TestTax:
    def test_adds_a_tax(self, manager):
        response = manager.post(reverse("lfs_manage_add_customer_tax"), {"rate": "7", "description": "Books"})

        tax = CustomerTax.objects.get()
        assert (tax.rate, tax.description) == (7.0, "Books")
        assert response["Location"] == reverse("lfs_manage_customer_tax", kwargs={"id": tax.id})
        assert messages_of(response) == ["Customer tax has been created."]

    def test_a_rate_must_be_a_number(self, manager):
        response = manager.post(reverse("lfs_manage_add_customer_tax"), {"rate": "seven"})

        assert response.context["form"].errors["rate"]
        assert not CustomerTax.objects.exists()

    def test_saves_the_rate_and_description(self, manager):
        tax = CustomerTax.objects.create(rate=7)
        url = reverse("lfs_manage_customer_tax", kwargs={"id": tax.id})

        response = manager.post(url, {"rate": "19", "description": "EU"})

        tax.refresh_from_db()
        assert (tax.rate, tax.description) == (19.0, "EU")
        assert response["Location"] == url
        assert messages_of(response) == ["Customer tax has been saved."]

    def test_saves_the_criteria_and_shows_them(self, manager):
        tax = CustomerTax.objects.create(rate=19)
        url = reverse("lfs_manage_customer_tax_criteria", kwargs={"id": tax.id})

        response = manager.post(
            url, {"type-1": CART_PRICE, "operator-1": str(Criterion.GREATER_THAN), "position-1": "10", "value-1": "100"}
        )

        criterion = CartPriceCriterion.objects.get()
        assert (criterion.content, criterion.operator, criterion.value) == (tax, Criterion.GREATER_THAN, 100.0)
        assert response["Location"] == url
        assert messages_of(response) == ["Criteria have been saved."]
        assert len(manager.get(url).context_data["criteria"]) == 1

    def test_saving_the_criteria_with_htmx_returns_the_tab(self, manager):
        tax = CustomerTax.objects.create(rate=19)

        response = manager.post(
            reverse("lfs_manage_customer_tax_criteria", kwargs={"id": tax.id}), HTTP_HX_REQUEST="true"
        )

        assert response.status_code == 200
        assert response.templates[0].name == "manage/customer_taxes/tabs/_criteria.html"

    def test_deletes_the_tax(self, manager):
        tax = CustomerTax.objects.create(rate=19)

        assert (
            manager.get(reverse("lfs_manage_delete_customer_tax_confirm", kwargs={"id": tax.id})).context[
                "customer_tax"
            ]
            == tax
        )
        response = manager.post(reverse("lfs_manage_delete_customer_tax", kwargs={"id": tax.id}))

        assert not CustomerTax.objects.exists()
        assert response["Location"] == reverse("lfs_manage_customer_taxes")
