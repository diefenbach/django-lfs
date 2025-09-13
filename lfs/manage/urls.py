from django.urls import path, re_path, include
import lfs.manage
import lfs.manage.images.views
import lfs.manage.information.views
import lfs.manage.products

# Removed imports for non-existent product modules
import lfs.manage.views.export
import lfs.manage.views.utils
from lfs.catalog.models import Product
from lfs.catalog.models import Category
from lfs.core.models import Shop
from lfs.manage.products.forms import SEOForm as ProductSEOForm
from lfs.manage.shop.views import ShopSEOView
from lfs.manage.seo.views import SEOView
from lfs.manufacturer.models import Manufacturer


urlpatterns = [
    path("", include("lfs.manage.dashboard.urls")),
    path("", include("lfs.manage.delivery_times.urls")),
    path("", include("lfs.manage.manufacturers.urls")),
    path("", include("lfs.manage.featured.urls")),
    path("", include("lfs.manage.review_mails.urls")),
    path("", include("lfs.manage.topseller.urls")),
    path("", include("lfs.manage.voucher.urls")),
    path("", include("lfs.manage.portlets.urls")),
    path("", include("lfs.manage.images.urls")),
    path("", include("lfs.manage.property_groups.urls")),
    path("", include("lfs.manage.properties.urls")),
    re_path(
        r"^update-product-properties/(?P<id>\d*)$",
        lfs.manage.products.views.ProductPropertiesView.as_view(),
        name="lfs_update_product_properties",
    ),
    re_path(
        r"^update-product-property-groups/(?P<id>\d*)$",
        lfs.manage.products.views.ProductPropertiesView.as_view(),
        name="lfs_update_product_property_groups",
    ),
    path("", include("lfs.manage.carts.urls")),
    path("", include("lfs.manage.categories.urls")),
    path("", include("lfs.manage.customers.urls")),
    path("", include("lfs.manage.products.urls")),
    path("", include("lfs.manage.shipping_methods.urls")),
    path("", include("lfs.manage.discounts.urls")),
    path("", include("lfs.manage.pages.urls")),
    path("", include("lfs.manage.payment_methods.urls")),
    path("", include("lfs.manage.orders.urls")),
    path("", include("lfs.manage.criteria.urls")),
    path("", include("lfs.manage.static_blocks.urls")),
    path("", include("lfs.manage.reviews.urls")),
    path("", include("lfs.manage.shop.urls")),
    path("", include("lfs.manage.actions.urls")),
    path("", include("lfs.manage.product_taxes.urls")),
    path("", include("lfs.manage.customer_taxes.urls")),
    # Export
    re_path(r"^export-dispatcher$", lfs.manage.views.export.export_dispatcher, name="lfs_export_dispatcher"),
    re_path(r"^export/(?P<export_id>\d*)$", lfs.manage.views.export.manage_export, name="lfs_export"),
    re_path(
        r"^export-inline/(?P<export_id>\d*)/(?P<category_id>\d*)$",
        lfs.manage.views.export.export_inline,
        name="lfs_export_inline",
    ),
    re_path(
        r"^edit-category/(?P<export_id>\d*)/(?P<category_id>\d*)$",
        lfs.manage.views.export.edit_category,
        name="lfs_export_edit_category",
    ),
    re_path(
        r"^edit-product/(?P<export_id>\d*)/(?P<product_id>\d*)$",
        lfs.manage.views.export.edit_product,
        name="lfs_export_edit_product",
    ),
    re_path(
        r"^category-state/(?P<export_id>\d*)/(?P<category_id>\d*)$",
        lfs.manage.views.export.category_state,
        name="lfs_export_category_state",
    ),
    re_path(
        r"^update-export-data/(?P<export_id>\d*)$",
        lfs.manage.views.export.update_data,
        name="lfs_export_update_export_data",
    ),
    re_path(r"^add-export$", lfs.manage.views.export.add_export, name="lfs_export_add_export"),
    re_path(
        r"^delete-export/(?P<export_id>\d*)$", lfs.manage.views.export.delete_export, name="lfs_export_delete_export"
    ),
    re_path(r"^export-export/(?P<slug>[-\w]*)$", lfs.manage.views.export.export, name="lfs_export_export"),
    re_path(
        r"^update-category-variants-option/(?P<export_id>\d*)/(?P<category_id>\d*)$",
        lfs.manage.views.export.update_category_variants_option,
        name="lfs_export_update_category_variants_option",
    ),
    # Utils
    re_path(r"^utilities$", lfs.manage.views.utils.utilities, name="lfs_manage_utils"),
    re_path(r"^clear-cache$", lfs.manage.views.utils.clear_cache, name="lfs_clear_cache"),
    re_path(r"^set-category-levels$", lfs.manage.views.utils.set_category_levels, name="lfs_set_category_levels"),
    re_path(
        r"^update-effective-price$", lfs.manage.views.utils.update_effective_price, name="lfs_update_effective_price"
    ),
    re_path(r"^reindex-topseller$", lfs.manage.views.utils.reindex_topseller, name="lfs_reindex_topseller"),
    # Information
    re_path(r"^environment$", lfs.manage.information.views.environment, name="lfs_manage_environment"),
]

# Manufacturer / SEO
urlpatterns += SEOView.get_seo_urlpattern(Manufacturer)
urlpatterns += ShopSEOView.get_seo_urlpattern(Shop)
urlpatterns += SEOView.get_seo_urlpattern(Product, form_klass=ProductSEOForm, template_name="manage/products/seo.html")
urlpatterns += SEOView.get_seo_urlpattern(Category)
