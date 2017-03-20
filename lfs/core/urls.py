
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps import views as sitemap_views

from . import views
from . utils import import_symbol

urlpatterns = [
    # Auth
    url(r'^password-reset/$', auth_views.password_reset, name="lfs_password_reset"),
    url(r'^password-reset-done/$', auth_views.password_reset_done, name="password_reset_done"),
    url(r'^password-reset-confirm/(?P<uidb64>[-\w]*)/(?P<token>[-\w]*)/$', auth_views.password_reset_confirm, name="password_reset_confirm"),
    url(r'^password-reset-complete/$', auth_views.password_reset_complete, name="password_reset_complete"),

    # LFS modules
    url(r'', include('lfs.cart.urls')),
    url(r'', include('lfs.catalog.urls')),
    url(r'', include('lfs.checkout.urls')),
    url(r'', include('lfs.customer.urls')),
    url(r'', include('lfs.manufacturer.urls')),
    url(r'', include('lfs.page.urls')),
    url(r'', include('lfs.search.urls')),

    # Contact
    url(r'', include('lfs_contact.urls')),

    # Shop
    url(r'^$', views.shop_view, name="lfs_shop_view"),

    # Robots
    url(r'^robots.txt$', views.TextTemplateView.as_view(template_name='lfs/shop/robots.txt')),
]

# Sitemap urls
try:
    product_sitemap = import_symbol(settings.LFS_SITEMAPS["product"]["sitemap"])
except (AttributeError, KeyError, ImportError):
    from . sitemaps import ProductSitemap
    product_sitemap = ProductSitemap

try:
    category_sitemap = import_symbol(settings.LFS_SITEMAPS["category"]["sitemap"])
except (AttributeError, KeyError, ImportError):
    from . sitemaps import CategorySitemap
    category_sitemap = CategorySitemap

try:
    page_sitemap = import_symbol(settings.LFS_SITEMAPS["page"]["sitemap"])
except (AttributeError, KeyError, ImportError):
    from . sitemaps import PageSitemap
    page_sitemap = PageSitemap

try:
    shop_sitemap = import_symbol(settings.LFS_SITEMAPS["shop"]["sitemap"])
except (AttributeError, KeyError, ImportError):
    from . sitemaps import ShopSitemap
    shop_sitemap = ShopSitemap

urlpatterns += [
    url(r'^sitemap.xml$', sitemap_views.sitemap, {'sitemaps': {
        "products": product_sitemap,
        "categories": category_sitemap,
        "pages": page_sitemap,
        "shop": shop_sitemap,
    }}),
]
