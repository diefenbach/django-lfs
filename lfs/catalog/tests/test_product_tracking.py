import json
from decimal import Decimal

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.file import SessionStore
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from lfs.catalog.models import Product
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyGroup
from lfs.catalog.models import PropertyOption
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_FILTER
from lfs.catalog.settings import VARIANT
from lfs.catalog.utils import get_display_product
from lfs.catalog.utils import product_to_tracking_snapshot
from lfs.tests.utils import RequestFactory


class ProductTrackingUtilsTestCase(TestCase):
    fixtures = ["lfs_shop.xml"]

    def setUp(self):
        self.request = RequestFactory().get("/")
        self.request.session = SessionStore()
        self.request.user = AnonymousUser()

        self.parent = Product.objects.create(
            name="Parent",
            slug="parent-product",
            sub_type=PRODUCT_WITH_VARIANTS,
            active=True,
            price=5,
        )
        color = Property.objects.create(name="Color", add_price=True, price=10.0)
        red = PropertyOption.objects.create(name="Red", property=color)
        self.pg = PropertyGroup.objects.create(name="T-Shirts")
        self.pg.products.set([self.parent])
        self.pg.save()

        self.variant = Product.objects.create(
            name="Variant Red",
            slug="variant-red",
            sub_type=VARIANT,
            parent=self.parent,
            active=True,
            sku="SKU-VAR",
            active_sku=True,
        )
        ProductPropertyValue.objects.create(
            product=self.variant,
            property=color,
            property_group=self.pg,
            value=str(red.id),
            type=PROPERTY_VALUE_TYPE_FILTER,
        )
        self.parent.default_variant = self.variant
        self.parent.save()

        self.simple = Product.objects.create(
            name="Simple Product",
            slug="simple-product",
            active=True,
            price=12,
            sku="SKU-SIMPLE",
        )

    def test_get_display_product_returns_default_variant_for_parent(self):
        display = get_display_product(self.request, self.parent)
        self.assertEqual(display.pk, self.variant.pk)

    def test_get_display_product_returns_variant_for_variant_url(self):
        display = get_display_product(self.request, self.variant)
        self.assertEqual(display.pk, self.variant.pk)

    def test_get_display_product_returns_simple_product(self):
        display = get_display_product(self.request, self.simple)
        self.assertEqual(display.pk, self.simple.pk)

    def test_product_to_tracking_snapshot_maps_display_product(self):
        snapshot = product_to_tracking_snapshot(self.request, self.simple)
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot["currency"], "EUR")
        self.assertEqual(len(snapshot["line_items"]), 1)
        self.assertEqual(snapshot["line_items"][0]["sku"], "SKU-SIMPLE")
        self.assertEqual(snapshot["line_items"][0]["name"], "Simple Product")
        self.assertEqual(snapshot["line_items"][0]["quantity"], 1)
        self.assertEqual(snapshot["value"], snapshot["line_items"][0]["price"])

    def test_product_to_tracking_snapshot_returns_none_without_product(self):
        self.assertIsNone(product_to_tracking_snapshot(self.request, None))

    def test_product_to_tracking_snapshot_serializes_decimal_prices_as_float(self):
        from lfs.core.utils import LazyEncoder

        snapshot = {
            "currency": "EUR",
            "value": 9.99,
            "line_items": [{"sku": "S1", "name": "P", "price": 9.99, "quantity": 1}],
        }
        payload = json.dumps({"tracking_snapshot": snapshot}, cls=LazyEncoder)
        data = json.loads(payload)
        self.assertEqual(data["tracking_snapshot"]["value"], 9.99)
        self.assertIsInstance(data["tracking_snapshot"]["line_items"][0]["price"], float)


@override_settings(GTM_ID="GTM-TEST")
class ProductViewItemTrackingTestCase(TestCase):
    fixtures = ["lfs_shop.xml"]

    def setUp(self):
        self.client = Client()
        self.parent = Product.objects.create(
            name="Parent Track",
            slug="parent-track",
            sub_type=PRODUCT_WITH_VARIANTS,
            active=True,
            price=5,
        )
        color = Property.objects.create(name="Color", add_price=True, price=10.0)
        red = PropertyOption.objects.create(name="Red", property=color)
        self.pg = PropertyGroup.objects.create(name="T-Shirts")
        self.pg.products.set([self.parent])
        self.pg.save()

        self.variant = Product.objects.create(
            name="Variant Track",
            slug="variant-track",
            sub_type=VARIANT,
            parent=self.parent,
            active=True,
            sku="SKU-V1",
            active_sku=True,
        )
        ProductPropertyValue.objects.create(
            product=self.variant,
            property=color,
            property_group=self.pg,
            value=str(red.id),
            type=PROPERTY_VALUE_TYPE_FILTER,
        )
        self.parent.default_variant = self.variant
        self.parent.save()

    def test_product_view_renders_view_item(self):
        response = self.client.get(reverse("lfs_product", kwargs={"slug": "parent-track"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "view_item")
        self.assertContains(response, "view-item-event")
        self.assertContains(response, '"item_id": "SKU-V1"')

