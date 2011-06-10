# python imports
from datetime import datetime

# improt django
from django.contrib.sitemaps import Sitemap
from lfs.catalog.models import Category
from lfs.catalog.models import Product


class ProductSitemap(Sitemap):
    """Google's XML sitemap for products.
    """
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Product.objects.filter(active=True)

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
        return datetime.now()
