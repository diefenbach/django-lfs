"""The management interface speaks the shop's language: tab labels, breadcrumbs and form labels are translated."""

import re

from django.urls import reverse

from lfs.catalog.models import Product


def nav_texts(html: str) -> list[str]:
    """Return the texts of the tab links and breadcrumb items of a page, whitespace collapsed."""
    found = re.findall(r'class="(?:nav-link|breadcrumb-item)[^"]*"[^>]*>(.*?)</(?:a|li)>', html, re.S)
    return [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip() for text in found]


def test_category_tabs_and_breadcrumb_are_german(authenticated_client, category, settings):
    settings.LANGUAGE_CODE = "de"

    response = authenticated_client.get(reverse("lfs_manage_category", args=[category.pk]))

    texts = nav_texts(response.content.decode())
    for german in ("Daten", "Ansicht", "Produkte", "SEO", "Verwaltung", "Kategorien"):
        assert german in texts
    for english in ("Data", "View", "Seo", "Manage", "Categories"):
        assert english not in texts


def test_category_tabs_stay_english_in_an_english_shop(authenticated_client, category, settings):
    settings.LANGUAGE_CODE = "en"

    response = authenticated_client.get(reverse("lfs_manage_category", args=[category.pk]))

    texts = nav_texts(response.content.decode())
    for english in ("Data", "View", "Products", "SEO", "Manage", "Categories"):
        assert english in texts


def test_product_form_labels_are_german(authenticated_client, settings):
    settings.LANGUAGE_CODE = "de"
    product = Product.objects.create(name="Apron", slug="apron", price=10)

    response = authenticated_client.get(reverse("lfs_manage_product_data", args=[product.pk]))

    content = response.content.decode()
    assert "Active base price" not in content
    assert "Grundpreis aktivieren" in content


def test_catalog_menu_links_the_product_overview_in_german(authenticated_client, category, settings):
    settings.LANGUAGE_CODE = "de"

    content = authenticated_client.get(reverse("lfs_manage_category", args=[category.pk])).content.decode()

    assert f'href="{reverse("lfs_manage_products_list")}">Produktübersicht</a>' in content
