"""Selecting a property option with a price on the product page adds that price to the shown product price."""

import json

from django.test import TestCase
from django.urls import reverse

from lfs.catalog.models import Product, Property, PropertyGroup, PropertyOption
from lfs.catalog.settings import PROPERTY_SELECT_FIELD


class PropertyPriceTestCase(TestCase):
    fixtures = ["lfs_shop.xml"]

    def setUp(self):
        self.product = Product.objects.create(name="Bench", slug="bench", active=True, price=100)
        self.group = PropertyGroup.objects.create(name="Options")
        self.prop = Property.objects.create(name="Wood", type=PROPERTY_SELECT_FIELD, add_price=True)
        self.oak = PropertyOption.objects.create(property=self.prop, name="Oak", price=25)
        self.url = reverse("lfs_calculate_price", kwargs={"id": self.product.id})

    def price(self, data: dict[str, str]) -> str:
        """Post ``data`` to the price calculation and return the shown price."""
        response = self.client.post(self.url, data)
        return json.loads(response.content)["price"]

    def test_selected_option_adds_its_price(self):
        without = self.price({})

        with_oak = self.price({f"property-{self.group.id}-{self.prop.id}": str(self.oak.id)})

        self.assertIn("100.00", without)
        self.assertIn("125.00", with_oak)

    def test_option_of_a_property_without_add_price_keeps_the_price(self):
        self.prop.add_price = False
        self.prop.save()

        self.assertIn("100.00", self.price({f"property-{self.group.id}-{self.prop.id}": str(self.oak.id)}))

    def test_unknown_property_or_option_keeps_the_price(self):
        self.assertIn("100.00", self.price({f"property-{self.group.id}-999": str(self.oak.id)}))
        self.assertIn("100.00", self.price({f"property-{self.group.id}-{self.prop.id}": "999"}))
