from django.contrib.sitemaps import Sitemap
from django.utils import timezone

from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.core.models import Shop
from lfs.page.models import Page


class ProductSitemap(Sitemap):
    """Google's XML sitemap for products.
    """
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Product.objects.filter(active=True).exclude(sub_type=2)

    def lastmod(self, obj):
        return obj.creation_date


class CategorySitemap(Sitemap):
    """Google's XML sitemap for products.
    """
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        return timezone.now()


class PageSitemap(Sitemap):
    """Google's XML sitemap for pages.
    """
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Page.objects.filter(active=True)

    def lastmod(self, obj):
        return timezone.now()


class ShopSitemap(Sitemap):
    """Google's XML sitemap for the shop.
    """
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Shop.objects.all()

    def lastmod(self, obj):
        return timezone.now()

    def location(self, obj):
        return "/"
