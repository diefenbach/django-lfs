"""The product tax management, tested through real requests as a shop manager: the start page, the list and its
search, adding, saving and deleting a tax."""

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from lfs.catalog.models import Product
from lfs.tax.models import Tax

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.fixture(autouse=True)
def no_taxes(db):
    """Start without the taxes other fixtures bring."""
    Tax.objects.all().delete()


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def test_shows_the_first_tax(manager):
    tax = Tax.objects.create(rate=19)

    assert manager.get(reverse("lfs_manage_taxes"))["Location"] == reverse("lfs_manage_tax", kwargs={"pk": tax.id})


def test_without_taxes_shows_the_empty_page(manager):
    assert manager.get(reverse("lfs_manage_taxes"))["Location"] == reverse("lfs_no_taxes")


def test_lists_taxes_by_rate_and_the_search_finds_rate_or_description(manager):
    full = Tax.objects.create(rate=19, description="Standard")
    reduced = Tax.objects.create(rate=7, description="Books and food")
    url = reverse("lfs_manage_tax", kwargs={"pk": full.id})

    assert list(manager.get(url).context["taxes"]) == [reduced, full]
    assert list(manager.get(url, {"q": "19"}).context["taxes"]) == [full]
    assert list(manager.get(url, {"q": "books"}).context["taxes"]) == [reduced]


def test_adds_a_tax(manager):
    response = manager.post(reverse("lfs_manage_add_tax"), {"create-rate": "7", "create-description": "Books"})

    tax = Tax.objects.get()
    assert (tax.rate, tax.description) == (7.0, "Books")
    assert response["Location"] == reverse("lfs_manage_tax", kwargs={"pk": tax.id})
    assert messages_of(response) == ["Tax has been added."]


def test_a_rate_must_be_a_number(manager):
    response = manager.post(reverse("lfs_manage_add_tax"), {"create-rate": "seven"})

    assert response.context["form"].errors["rate"]
    assert not Tax.objects.exists()


def test_saves_a_tax(manager):
    tax = Tax.objects.create(rate=16)
    url = reverse("lfs_manage_tax", kwargs={"pk": tax.id})

    response = manager.post(url, {"rate": "19", "description": "Standard"})

    tax.refresh_from_db()
    assert (tax.rate, tax.description) == (19.0, "Standard")
    assert response["Location"] == url
    assert messages_of(response) == ["Tax has been saved."]


def test_deleting_shows_the_next_tax_and_keeps_its_products(manager):
    full, reduced = Tax.objects.create(rate=19), Tax.objects.create(rate=7)
    lamp = Product.objects.create(name="Lamp", slug="lamp", tax=full)

    assert manager.get(reverse("lfs_manage_delete_tax_confirm", kwargs={"pk": full.id})).context["tax"] == full
    response = manager.post(reverse("lfs_delete_tax", kwargs={"pk": full.id}))

    assert list(Tax.objects.all()) == [reduced]
    assert Product.objects.get(pk=lamp.pk).tax is None
    assert response["Location"] == reverse("lfs_manage_tax", kwargs={"pk": reduced.id})
    assert messages_of(response) == ["Tax has been deleted."]


def test_deleting_the_last_tax_shows_the_empty_page(manager):
    tax = Tax.objects.create(rate=19)

    assert manager.post(reverse("lfs_delete_tax", kwargs={"pk": tax.id}))["Location"] == reverse("lfs_no_taxes")
