"""Validation rules of the product forms that the management views do not cover on their own: what a new product
needs, and the property fields the simple variant form adds."""

import pytest

from lfs.catalog.models import Product
from lfs.manage.products.forms import ProductAddForm, ProductVariantSimpleForm


@pytest.mark.django_db
class TestProductAddForm:
    def test_creates_the_product(self, shop):
        form = ProductAddForm(data={"name": "New Product", "slug": "new-product", "sub_type": "0"})

        product = form.save()

        assert Product.objects.get(pk=product.pk).slug == "new-product"

    @pytest.mark.parametrize("missing", ["slug", "sub_type"])
    def test_requires_slug_and_type(self, missing: str):
        data = {"name": "New Product", "slug": "new-product", "sub_type": "0"}
        del data[missing]

        form = ProductAddForm(data=data)

        assert not form.is_valid()
        assert missing in form.errors

    def test_refuses_a_slug_that_is_taken(self, product):
        form = ProductAddForm(data={"name": "Duplicate", "slug": product.slug, "sub_type": "0"})

        assert not form.is_valid()
        assert "slug" in form.errors


class TestProductVariantSimpleForm:
    def test_adds_a_field_for_each_property(self, product_property):
        form = ProductVariantSimpleForm(all_properties=[{"property": product_property, "property_group": None}])

        assert f"property_0_{product_property.id}" in form.fields

    @pytest.mark.django_db
    def test_accepts_slug_name_and_price(self):
        form = ProductVariantSimpleForm(all_properties=[], data={"slug": "v", "name": "Variant", "price": "29.99"})

        assert form.is_valid()
