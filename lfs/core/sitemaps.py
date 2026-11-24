from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.settings import VARIANT
from lfs.core.models import Shop
from lfs.manufacturer.models import Manufacturer
from lfs.page.models import Page


class ProductSitemap(Sitemap):
    """Google's XML sitemap for products."""

    changefreq = getattr(settings, "LFS_SITEMAPS", {}).get("product", {}).get("changefreq", "weekly")
    priority = getattr(settings, "LFS_SITEMAPS", {}).get("product", {}).get("priority", 0.5)
    protocol = getattr(settings, "LFS_SITEMAPS", {}).get("product", {}).get("protocol", None)

    def items(self):
        return Product.objects.filter(active=True).exclude(sub_type=2)

    def lastmod(self, obj):
        return obj.creation_date


class CategorySitemap(Sitemap):
    """Google's XML sitemap for products."""

    changefreq = getattr(settings, "LFS_SITEMAPS", {}).get("category", {}).get("changefreq", "weekly")
    priority = getattr(settings, "LFS_SITEMAPS", {}).get("category", {}).get("priority", 0.5)
    protocol = getattr(settings, "LFS_SITEMAPS", {}).get("category", {}).get("protocol", None)

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        return timezone.now()


class PageSitemap(Sitemap):
    """Google's XML sitemap for pages."""

    changefreq = getattr(settings, "LFS_SITEMAPS", {}).get("page", {}).get("changefreq", "weekly")
    priority = getattr(settings, "LFS_SITEMAPS", {}).get("page", {}).get("priority", 0.5)
    protocol = getattr(settings, "LFS_SITEMAPS", {}).get("page", {}).get("protocol", None)

    def items(self):
        return Page.objects.filter(active=True).exclude(slug="")

    def lastmod(self, obj):
        return timezone.now()


class ShopSitemap(Sitemap):
    """Google's XML sitemap for the shop."""

    changefreq = getattr(settings, "LFS_SITEMAPS", {}).get("shop", {}).get("changefreq", "weekly")
    priority = getattr(settings, "LFS_SITEMAPS", {}).get("shop", {}).get("priority", 0.5)
    protocol = getattr(settings, "LFS_SITEMAPS", {}).get("shop", {}).get("protocol", None)

    def items(self):
        return Shop.objects.all()

    def lastmod(self, obj):
        return timezone.now()

    def location(self, obj):
        return "/"


class ManufacturerSitemap(Sitemap):
    """Google's XML sitemap for manufacturers that have active products.

    A manufacturer without them has an empty page, which should not be offered for search results.
    No lastmod: manufacturers have no modification date, and Google uses lastmod only if it is accurate.
    """

    changefreq = getattr(settings, "LFS_SITEMAPS", {}).get("manufacturer", {}).get("changefreq", "weekly")
    priority = getattr(settings, "LFS_SITEMAPS", {}).get("manufacturer", {}).get("priority", 0.5)
    protocol = getattr(settings, "LFS_SITEMAPS", {}).get("manufacturer", {}).get("protocol", None)

    def items(self):
        # The products a manufacturer page shows (Manufacturer.get_all_products).
        shown = Product.objects.filter(active=True).exclude(sub_type=VARIANT)
        return Manufacturer.objects.filter(products__in=shown).distinct()


class ViewSitemap(Sitemap):
    """Google's XML sitemap for shop views without a model: the manufacturer list and the contact form."""

    changefreq = getattr(settings, "LFS_SITEMAPS", {}).get("view", {}).get("changefreq", "monthly")
    priority = getattr(settings, "LFS_SITEMAPS", {}).get("view", {}).get("priority", 0.5)
    protocol = getattr(settings, "LFS_SITEMAPS", {}).get("view", {}).get("protocol", None)

    def items(self):
        return ["lfs_manufacturers", "lfs_contact_form"]

    def location(self, obj):
        return reverse(obj)
