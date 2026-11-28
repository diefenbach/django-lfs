import sys

from django.test import TestCase, override_settings

import lfs.core.utils
from lfs.core.models import Shop
from lfs.core.templatetags.lfs_tags import currency


class ShopTestCase(TestCase):
    """Tests the views of the lfs.catalog."""

    fixtures = ["lfs_shop.xml"]

    def test_shop_defaults(self):
        """Tests the shop values right after creation of an instance"""
        shop = Shop.objects.get(pk=1)

        self.assertEqual(shop.name, "LFS")
        self.assertEqual(shop.shop_owner, "John Doe")
        self.assertEqual(shop.product_cols, 1)
        self.assertEqual(shop.product_rows, 10)
        self.assertEqual(shop.category_cols, 1)
        self.assertEqual(shop.google_analytics_id, "")
        self.assertEqual(shop.ga_site_tracking, False)
        self.assertEqual(shop.ga_ecommerce_tracking, False)
        self.assertEqual(shop.default_country.name, "Deutschland")
        self.assertEqual(shop.get_default_country().name, "Deutschland")
        self.assertEqual(shop.meta_title, "<name>")
        self.assertEqual(shop.meta_keywords, "")
        self.assertEqual(shop.meta_description, "")

    def test_from_email(self):
        """ """
        shop = lfs.core.utils.get_default_shop()

        shop.from_email = "john@doe.com"
        self.assertEqual(shop.from_email, "john@doe.com")

    def test_get_notification_emails(self):
        """ """
        shop = lfs.core.utils.get_default_shop()

        shop.notification_emails = "john@doe.com, jane@doe.com, baby@doe.com"

        self.assertEqual(shop.get_notification_emails(), ["john@doe.com", "jane@doe.com", "baby@doe.com"])

        shop.notification_emails = "john@doe.com\njane@doe.com\nbaby@doe.com"
        self.assertEqual(shop.get_notification_emails(), ["john@doe.com", "jane@doe.com", "baby@doe.com"])

        shop.notification_emails = "john@doe.com\r\njane@doe.com\r\nbaby@doe.com"
        self.assertEqual(shop.get_notification_emails(), ["john@doe.com", "jane@doe.com", "baby@doe.com"])

        shop.notification_emails = "john@doe.com\n\rjane@doe.com\n\rbaby@doe.com"
        self.assertEqual(shop.get_notification_emails(), ["john@doe.com", "jane@doe.com", "baby@doe.com"])

        shop.notification_emails = "john@doe.com,,,,\n\n\n\njane@doe.com"
        self.assertEqual(shop.get_notification_emails(), ["john@doe.com", "jane@doe.com"])

    def test_get_meta_title(self):
        shop = lfs.core.utils.get_default_shop()
        self.assertEqual("LFS", shop.get_meta_title())

        shop.meta_title = "John Doe"
        shop.save()

        self.assertEqual("John Doe", shop.get_meta_title())

        shop.meta_title = "<name> - John Doe"
        shop.save()

        self.assertEqual("LFS - John Doe", shop.get_meta_title())

        shop.meta_title = "John Doe - <name>"
        shop.save()

        self.assertEqual("John Doe - LFS", shop.get_meta_title())

    def test_get_meta_keywords(self):
        shop = lfs.core.utils.get_default_shop()
        self.assertEqual("", shop.get_meta_keywords())

        shop.meta_keywords = "John Doe"
        shop.save()

        self.assertEqual("John Doe", shop.get_meta_keywords())

        shop.meta_keywords = "<name> - John Doe"
        shop.save()

        self.assertEqual("LFS - John Doe", shop.get_meta_keywords())

        shop.meta_keywords = "<name> - John Doe"
        shop.save()

        self.assertEqual("LFS - John Doe", shop.get_meta_keywords())

        shop.meta_keywords = "<name> - John Doe - <name>"
        shop.save()

        self.assertEqual("LFS - John Doe - LFS", shop.get_meta_keywords())

    def test_get_meta_description(self):
        shop = lfs.core.utils.get_default_shop()
        self.assertEqual("", shop.get_meta_description())

        shop.meta_description = "John Doe"
        shop.save()

        self.assertEqual("John Doe", shop.get_meta_description())

        shop.meta_description = "<name> - John Doe"
        shop.save()

        self.assertEqual("LFS - John Doe", shop.get_meta_description())

        shop.meta_description = "<name> - John Doe"
        shop.save()

        self.assertEqual("LFS - John Doe", shop.get_meta_description())

        shop.meta_description = "<name> - John Doe - <name>"
        shop.save()

        self.assertEqual("LFS - John Doe - LFS", shop.get_meta_description())


class TagsTestCase(TestCase):
    """ """

    fixtures = ["lfs_shop.xml"]

    # TODO: Fix this test (there needs to be a saved Order, see line 261)
    @override_settings(LFS_CURRENCY="EUR", LANGUAGE_CODE="en")
    def test_currency_rounds_half_up_and_appends_the_currency(self):
        self.assertEqual(currency(0.0), "0.00 EUR")
        self.assertEqual(currency(-1.0), "-1.00 EUR")
        self.assertEqual(currency(0.125), "0.13 EUR")


class SiteMapsTestCase(TestCase):
    fixtures = ["lfs_shop.xml"]

    def test_sitemaps_default_1(self):
        result = self.client.get("/sitemap.xml")
        self.assertContains(result, "<priority>0.5</priority>")
        self.assertContains(result, "<changefreq>weekly</changefreq>")
        self.assertContains(result, "http://")

    def test_sitemap_lists_manufacturers_with_products_their_list_and_the_contact_form(self):
        from lfs.manufacturer.models import Manufacturer

        from lfs.catalog.models import Product

        auma = Manufacturer.objects.create(name="auma", slug="auma")
        Product.objects.create(name="Zaun", slug="zaun", active=True, manufacturer=auma)
        remmers = Manufacturer.objects.create(name="Remmers", slug="remmers")
        Product.objects.create(name="Lasur", slug="lasur", active=False, manufacturer=remmers)
        Manufacturer.objects.create(name="menz", slug="menz")
        result = self.client.get("/sitemap.xml")
        self.assertContains(result, "/manufacturer-auma/</loc>", count=1)
        self.assertNotContains(result, "/manufacturer-remmers/")
        self.assertNotContains(result, "/manufacturer-menz/")
        self.assertContains(result, "/manufacturers/</loc>")
        self.assertContains(result, "/contact</loc>")

    def test_sitemaps_settings(self):
        my_sitemaps = {
            "category": {
                "priority": 0.1,
                "changefreq": "category-daily",
                "protocol": "category-https",
            },
            "page": {
                "priority": 0.2,
                "changefreq": "page-daily",
                "protocol": "page-https",
            },
            "product": {
                "priority": 0.3,
                "changefreq": "product-daily",
                "protocol": "product-https",
            },
            "shop": {
                "priority": 0.4,
                "changefreq": "shop-daily",
                "protocol": "shop-https",
            },
        }

        with self.settings(LFS_SITEMAPS=my_sitemaps):
            if "lfs.core.sitemaps" in sys.modules:
                del sys.modules["lfs.core.sitemaps"]

            from lfs.core.sitemaps import CategorySitemap
            from lfs.core.sitemaps import ShopSitemap
            from lfs.core.sitemaps import PageSitemap
            from lfs.core.sitemaps import ProductSitemap

            self.assertEqual(CategorySitemap.priority, 0.1)
            self.assertEqual(CategorySitemap.changefreq, "category-daily")
            self.assertEqual(CategorySitemap.protocol, "category-https")

            self.assertEqual(PageSitemap.priority, 0.2)
            self.assertEqual(PageSitemap.changefreq, "page-daily")
            self.assertEqual(PageSitemap.protocol, "page-https")

            self.assertEqual(ProductSitemap.priority, 0.3)
            self.assertEqual(ProductSitemap.changefreq, "product-daily")
            self.assertEqual(ProductSitemap.protocol, "product-https")

            self.assertEqual(ShopSitemap.priority, 0.4)
            self.assertEqual(ShopSitemap.changefreq, "shop-daily")
            self.assertEqual(ShopSitemap.protocol, "shop-https")
