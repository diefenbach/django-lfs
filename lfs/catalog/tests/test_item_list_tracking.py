from unittest.mock import MagicMock
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.file import SessionStore
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyGroup
from lfs.catalog.models import PropertyOption
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_FILTER
from lfs.catalog.settings import VARIANT
from lfs.catalog.utils import item_list_to_tracking_snapshot
from lfs.catalog.utils import resolve_product_for_category_list
from lfs.catalog.utils import resolve_product_for_search_list
from lfs.tests.utils import RequestFactory


class ItemListTrackingUtilsTestCase(TestCase):
    fixtures = ["lfs_shop.xml"]

    def setUp(self):
        self.request = RequestFactory().get("/")
        self.request.session = SessionStore()
        self.request.user = AnonymousUser()

        self.p1 = Product.objects.create(
            name="List Product 1",
            slug="list-p1",
            active=True,
            price=10,
            sku="SKU-L1",
        )
        self.p2 = Product.objects.create(
            name="List Product 2",
            slug="list-p2",
            active=True,
            price=20,
            sku="SKU-L2",
        )

        self.parent = Product.objects.create(
            name="Parent List",
            slug="parent-list",
            sub_type=PRODUCT_WITH_VARIANTS,
            active=True,
            price=5,
        )
        color = Property.objects.create(name="Color", add_price=False)
        red = PropertyOption.objects.create(name="Red", property=color)
        self.pg = PropertyGroup.objects.create(name="PG")
        self.pg.products.set([self.parent])
        self.pg.save()
        self.variant = Product.objects.create(
            name="Variant List",
            slug="variant-list",
            sub_type=VARIANT,
            parent=self.parent,
            active=True,
            sku="SKU-VLIST",
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

    def test_item_list_to_tracking_snapshot_maps_products(self):
        snapshot = item_list_to_tracking_snapshot(
            self.request,
            [self.p1, self.p2],
            list_id="category-slug",
            list_name="Category Name",
        )
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot["list_id"], "category-slug")
        self.assertEqual(snapshot["list_name"], "Category Name")
        self.assertEqual(snapshot["currency"], "EUR")
        self.assertEqual(len(snapshot["line_items"]), 2)
        self.assertEqual(snapshot["line_items"][0]["sku"], "SKU-L1")
        self.assertEqual(snapshot["line_items"][1]["sku"], "SKU-L2")
        self.assertEqual(snapshot["value"], snapshot["line_items"][0]["price"] + snapshot["line_items"][1]["price"])

    def test_item_list_to_tracking_snapshot_returns_none_for_empty_list(self):
        self.assertIsNone(
            item_list_to_tracking_snapshot(
                self.request,
                [],
                list_id="empty",
                list_name="Empty",
            )
        )

    def test_resolve_product_for_search_list_uses_default_variant(self):
        resolved = resolve_product_for_search_list(self.request, self.parent)
        self.assertEqual(resolved.pk, self.variant.pk)

    def test_resolve_product_for_category_list_uses_default_variant(self):
        resolved = resolve_product_for_category_list(self.request, self.parent)
        self.assertEqual(resolved.pk, self.variant.pk)


@override_settings(GTM_ID="GTM-TEST")
class ItemListViewTrackingTestCase(TestCase):
    fixtures = ["lfs_shop.xml"]

    def setUp(self):
        self.client = Client()
        self.c1 = Category.objects.create(name="Category 1", slug="category-1")
        self.p1 = Product.objects.create(slug="product-1", name="Product 1", price=5, active=True, sku="SKU-P1")
        self.p2 = Product.objects.create(slug="product-2", name="Product 2", price=3, active=True, sku="SKU-P2")
        self.c1.products.set([self.p1, self.p2])
        self.c1.save()

    def test_category_view_renders_view_item_list(self):
        response = self.client.get(reverse("lfs_category", kwargs={"slug": "category-1"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "view_item_list")
        self.assertContains(response, "view-item-list-event")
        self.assertContains(response, '"item_list_id": "category-1"')

    @patch("lfs.search.views.render")
    @patch("lfs.search.views.Paginator")
    def test_search_view_passes_item_list_tracking_to_template(self, mock_paginator_cls, mock_render):
        from lfs.search.views import search

        product = Product.objects.create(
            name="Searchable Product",
            slug="search-p1",
            price=7,
            active=True,
            sku="SKU-SRCH",
        )
        current_page = MagicMock()
        current_page.object_list = [product]
        paginator = MagicMock()
        paginator.page.return_value = current_page
        paginator.num_pages = 1
        mock_paginator_cls.return_value = paginator
        mock_render.return_value = MagicMock(status_code=200)

        request = RequestFactory().get("/search/", {"q": "Searchable"})
        request.session = SessionStore()
        request.user = AnonymousUser()

        queryset = MagicMock()
        queryset.count.return_value = 1
        queryset.order_by.return_value = queryset

        with patch.object(Product.objects, "filter", return_value=queryset):
            with patch("lfs.search.views.lfs_pagination", return_value={"total_text": "1 product"}):
                search(request)

        if mock_render.call_args.kwargs:
            context = mock_render.call_args.kwargs["context"]
        else:
            context = mock_render.call_args.args[2]
        tracking = context["item_list_tracking"]
        self.assertEqual(tracking["list_id"], "search")
        self.assertEqual(tracking["list_name"], "Searchable")
        self.assertEqual(tracking["line_items"][0]["sku"], "SKU-SRCH")
