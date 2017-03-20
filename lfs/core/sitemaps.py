from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.utils import timezone

from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.core.models import Shop
from lfs.page.models import Page


class ProductSitemap(Sitemap):
    """Google's XML sitemap for products.
    """
    changefreq = getattr(settings, "LFS_SITEMAPS", {}).get("product", {}).get("changefreq", "weekly")
    priority = getattr(settings, "LFS_SITEMAPS", {}).get("product", {}).get("priority", 0.5)
    protocol = getattr(settings, "LFS_SITEMAPS", {}).get("product", {}).get("protocol", "http")

    def items(self):
        return Product.objects.all()[:1]
        return Product.objects.filter(active=True).exclude(sub_type=2)[:10]

    def lastmod(self, obj):
        return obj.creation_date


class CategorySitemap(Sitemap):
    """Google's XML sitemap for products.
    """
    changefreq = getattr(settings, "LFS_SITEMAPS", {}).get("category", {}).get("changefreq", "weekly")
    priority = getattr(settings, "LFS_SITEMAPS", {}).get("category", {}).get("priority", 0.5)
    protocol = getattr(settings, "LFS_SITEMAPS", {}).get("category", {}).get("protocol", "http")

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        return timezone.now()


class PageSitemap(Sitemap):
    """Google's XML sitemap for pages.
    """
    changefreq = getattr(settings, "LFS_SITEMAPS", {}).get("page", {}).get("changefreq", "weekly")
    priority = getattr(settings, "LFS_SITEMAPS", {}).get("page", {}).get("priority", 0.5)
    protocol = getattr(settings, "LFS_SITEMAPS", {}).get("page", {}).get("protocol", "http")

    def items(self):
        return Page.objects.filter(active=True)

    def lastmod(self, obj):
        return timezone.now()


class ShopSitemap(Sitemap):
    """Google's XML sitemap for the shop.
    """
    changefreq = getattr(settings, "LFS_SITEMAPS", {}).get("shop", {}).get("changefreq", "weekly")
    priority = getattr(settings, "LFS_SITEMAPS", {}).get("shop", {}).get("priority", 0.5)
    protocol = getattr(settings, "LFS_SITEMAPS", {}).get("shop", {}).get("protocol", "http")

    def items(self):
        return Shop.objects.all()

    def lastmod(self, obj):
        return timezone.now()

    def location(self, obj):
        return "/"
