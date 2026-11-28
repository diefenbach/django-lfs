"""The selects for category variant and display type in a product's variants tab are styled like the other
form fields of the management interface (Bootstrap ``form-select``), not as plain browser selects."""

import re

import pytest
from django.urls import reverse


def select_classes(html: str, name: str) -> list[str]:
    """Return the CSS classes of the ``<select>`` of the field ``name`` in ``html``."""
    tag = re.search(r'<select[^>]*name="%s"[^>]*>' % name, html)
    assert tag, f"no select named {name}"
    classes = re.search(r'class="([^"]*)"', tag.group(0))
    return classes.group(1).split() if classes else []


@pytest.mark.django_db
@pytest.mark.parametrize("name", ["category_variant", "variants_display_type"])
def test_variants_tab_selects_are_styled(client, admin_user, product_with_variant, name: str):
    parent, _ = product_with_variant
    client.force_login(admin_user)

    html = client.get(reverse("lfs_manage_product_variants", kwargs={"id": parent.id})).content.decode()

    assert "form-select" in select_classes(html, name)


@pytest.mark.django_db
def test_category_variant_select_still_offers_the_variants(client, admin_user, product_with_variant):
    parent, variant = product_with_variant
    client.force_login(admin_user)

    html = client.get(reverse("lfs_manage_product_variants", kwargs={"id": parent.id})).content.decode()

    assert re.search(r'<option value="%s"[^>]*>[^<]*\(' % variant.id, html)
