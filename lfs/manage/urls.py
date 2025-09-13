from django.urls import path, re_path, include
import lfs.manage
import lfs.manage.images.views
import lfs.manage.information.views
import lfs.manage.products

# Removed imports for non-existent product modules
import lfs.manage.views.criteria
import lfs.manage.views.export
import lfs.manage.views.utils
from lfs.catalog.models import Product
from lfs.catalog.models import Category
from lfs.core.models import Shop
from lfs.manage.products.forms import SEOForm as ProductSEOForm
from lfs.manage.shop.views import ShopSEOView
from lfs.manage.seo.views import SEOView
from lfs.manage.manufacturers import views as manufacturers_views
from lfs.manufacturer.models import Manufacturer


urlpatterns = [
    path("", include("lfs.manage.dashboard.urls")),
    # Delivery Times
    path("", include("lfs.manage.delivery_times.urls")),
    # Manufacturers
    path("", include("lfs.manage.manufacturers.urls")),
    # Legacy Manufacturer URLs (for backward compatibility)
    re_path(
        r"^manufacturer-dispatcher$", manufacturers_views.manufacturer_dispatcher, name="lfs_manufacturer_dispatcher"
    ),
    # Featured Products
    path("", include("lfs.manage.featured.urls")),
    # Marketing
    path("", include("lfs.manage.review_mails.urls")),
    # Topseller Products
    path("", include("lfs.manage.topseller.urls")),
    # Voucher Groups
    path("", include("lfs.manage.voucher.urls")),
    # Portlets
    path("", include("lfs.manage.portlets.urls")),
    # Product
    # Product management URLs are now handled by modern class-based views in products/urls.py
    re_path(r"^imagebrowser$", lfs.manage.images.views.imagebrowser, name="lfs_manage_imagebrowser"),
    re_path(r"^global-images$", lfs.manage.images.views.images, name="lfs_manage_global_images"),
    re_path(r"^global-images-list$", lfs.manage.images.views.images_list, name="lfs_manage_global_images_list"),
    re_path(r"^delete-global-images$", lfs.manage.images.views.delete_images, name="lfs_manage_delete_images"),
    re_path(r"^add-global-images$", lfs.manage.images.views.add_images, name="lfs_manage_add_global_image"),
    # Property Groups
    path("", include("lfs.manage.property_groups.urls")),
    # Properties
    path("", include("lfs.manage.properties.urls")),
    # Product properties
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
    # Carts
    path("", include("lfs.manage.carts.urls")),
    # Categories
    path("", include("lfs.manage.categories.urls")),
    # Customers (refactored views)
    path("", include("lfs.manage.customers.urls")),
    # Products (refactored views)
    path("", include("lfs.manage.products.urls")),
    # export
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
    # Shipping Methods
    path("", include("lfs.manage.shipping_methods.urls")),
    path("", include("lfs.manage.discounts.urls")),
    path("", include("lfs.manage.pages.urls")),
    path("", include("lfs.manage.payment_methods.urls")),
    path("", include("lfs.manage.orders.urls")),
    # Order numbers - now handled by class-based views
    # Criteria
    re_path(r"^add-criterion", lfs.manage.views.criteria.add_criterion, name="lfs_add_criterion"),
    re_path(
        r"^change-criterion",
        lfs.manage.views.criteria.change_criterion_form,
        name="lfs_change_criterion_form",
    ),
    re_path(
        r"^delete-criterion",
        lfs.manage.views.criteria.delete_criterion,
        name="lfs_delete_criterion",
    ),
    path("", include("lfs.manage.static_blocks.urls")),
    path("", include("lfs.manage.reviews.urls")),
    # Shop
    path("", include("lfs.manage.shop.urls")),
    # Legacy shop URLs removed - now handled by class-based views
    # Actions
    path("", include("lfs.manage.actions.urls")),
    # Product Taxes
    path("", include("lfs.manage.product_taxes.urls")),
    # Customer Taxes
    path("", include("lfs.manage.customer_taxes.urls")),
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
