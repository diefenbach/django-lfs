# django imports
from django.conf.urls import include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps import views as sitemap_views

from . import views
from lfs.core.sitemap import CategorySitemap
from lfs.core.sitemap import PageSitemap
from lfs.core.sitemap import ProductSitemap
from lfs.core.sitemap import ShopSitemap


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

    # Sitemaps
    url(r'^sitemap.xml$', sitemap_views.sitemap, {'sitemaps': {"products": ProductSitemap, "categories": CategorySitemap, "pages": PageSitemap, "shop": ShopSitemap}}),
]
