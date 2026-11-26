"""Search and live search work on every database; accents are ignored only on PostgreSQL (unaccent)."""

import json

import pytest
from django.core.management import call_command
from django.urls import reverse

from lfs.catalog.models import Product


@pytest.fixture
def products(db):
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    Product.objects.create(name="Garden spade", slug="garden-spade", price=10, active=True)
    Product.objects.create(name="Kitchen knife", slug="kitchen-knife", price=10, active=True)
    Product.objects.create(name="Garden hose", slug="garden-hose", price=10, active=False)


def test_search_finds_active_products_by_name(client, products):
    response = client.get(reverse("lfs_search"), {"q": "garden"})

    assert response.status_code == 200
    html = response.content.decode()
    assert "Garden spade" in html
    assert "Kitchen knife" not in html
    assert "Garden hose" not in html


def test_livesearch_finds_active_products_by_name(client, products):
    response = client.get(reverse("lfs_livesearch"), {"q": "knife"})

    data = json.loads(response.content)
    assert data["state"] == "success"
    assert "Kitchen knife" in data["products"]
    assert "Garden spade" not in data["products"]
