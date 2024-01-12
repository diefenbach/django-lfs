from django.conf import settings
from django.urls import include, re_path
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps import views as sitemap_views

from . import views
from .utils import import_symbol

urlpatterns = [
    # Auth
    re_path(r"^password-reset/$", auth_views.PasswordResetView.as_view(), name="lfs_password_reset"),
    re_path(r"^password-reset-done/$", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    re_path(
        r"^password-reset-confirm/(?P<uidb64>[-\w]*)/(?P<token>[-\w]*)/$",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    re_path(
        r"^password-reset-complete/$", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"
    ),
    # LFS modules
    re_path(r"", include("lfs.cart.urls")),
    re_path(r"", include("lfs.catalog.urls")),
    re_path(r"", include("lfs.checkout.urls")),
    re_path(r"", include("lfs.customer.urls")),
    re_path(r"", include("lfs.manufacturer.urls")),
    re_path(r"", include("lfs.page.urls")),
    re_path(r"", include("lfs.search.urls")),
    # Contact
    re_path(r"", include("lfs_contact.urls")),
    # Shop
    re_path(r"^$", views.shop_view, name="lfs_shop_view"),
    # Robots
    re_path(r"^robots.txt$", views.TextTemplateView.as_view(template_name="lfs/shop/robots.txt")),
]

# Sitemap urls
try:
    product_sitemap = import_symbol(settings.LFS_SITEMAPS["product"]["sitemap"])
except (AttributeError, KeyError, ImportError):
    from .sitemaps import ProductSitemap

    product_sitemap = ProductSitemap

try:
    category_sitemap = import_symbol(settings.LFS_SITEMAPS["category"]["sitemap"])
except (AttributeError, KeyError, ImportError):
    from .sitemaps import CategorySitemap

    category_sitemap = CategorySitemap

try:
    page_sitemap = import_symbol(settings.LFS_SITEMAPS["page"]["sitemap"])
except (AttributeError, KeyError, ImportError):
    from .sitemaps import PageSitemap

    page_sitemap = PageSitemap

try:
    shop_sitemap = import_symbol(settings.LFS_SITEMAPS["shop"]["sitemap"])
except (AttributeError, KeyError, ImportError):
    from .sitemaps import ShopSitemap

    shop_sitemap = ShopSitemap

urlpatterns += [
    re_path(
        r"^sitemap.xml$",
        sitemap_views.sitemap,
        {
            "sitemaps": {
                "products": product_sitemap,
                "categories": category_sitemap,
                "pages": page_sitemap,
                "shop": shop_sitemap,
            }
        },
    ),
]
