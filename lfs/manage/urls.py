from django.urls import path, include
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
    path("", include("lfs.manage.actions.urls")),
    path("", include("lfs.manage.carts.urls")),
    path("", include("lfs.manage.categories.urls")),
    path("", include("lfs.manage.criteria.urls")),
    path("", include("lfs.manage.customer_taxes.urls")),
    path("", include("lfs.manage.customers.urls")),
    path("", include("lfs.manage.dashboard.urls")),
    path("", include("lfs.manage.delivery_times.urls")),
    path("", include("lfs.manage.discounts.urls")),
    path("", include("lfs.manage.featured.urls")),
    path("", include("lfs.manage.images.urls")),
    path("", include("lfs.manage.manufacturers.urls")),
    path("", include("lfs.manage.orders.urls")),
    path("", include("lfs.manage.pages.urls")),
    path("", include("lfs.manage.payment_methods.urls")),
    path("", include("lfs.manage.portlets.urls")),
    path("", include("lfs.manage.product_taxes.urls")),
    path("", include("lfs.manage.products.urls")),
    path("", include("lfs.manage.properties.urls")),
    path("", include("lfs.manage.property_groups.urls")),
    path("", include("lfs.manage.review_mails.urls")),
    path("", include("lfs.manage.reviews.urls")),
    path("", include("lfs.manage.shipping_methods.urls")),
    path("", include("lfs.manage.shop.urls")),
    path("", include("lfs.manage.static_blocks.urls")),
    path("", include("lfs.manage.topseller.urls")),
    path("", include("lfs.manage.voucher.urls")),
    # Export
    path(
        "export-dispatcher",
        lfs.manage.views.export.export_dispatcher,
        name="lfs_export_dispatcher",
    ),
    path(
        "export/<int:export_id>",
        lfs.manage.views.export.manage_export,
        name="lfs_export",
    ),
    path(
        "export-inline/<int:export_id>/<int:category_id>",
        lfs.manage.views.export.export_inline,
        name="lfs_export_inline",
    ),
    path(
        "edit-category/<int:export_id>/<int:category_id>",
        lfs.manage.views.export.edit_category,
        name="lfs_export_edit_category",
    ),
    path(
        "edit-product/<int:export_id>/<int:product_id>",
        lfs.manage.views.export.edit_product,
        name="lfs_export_edit_product",
    ),
    path(
        "category-state/<int:export_id>/<int:category_id>",
        lfs.manage.views.export.category_state,
        name="lfs_export_category_state",
    ),
    path(
        "update-export-data/<int:export_id>",
        lfs.manage.views.export.update_data,
        name="lfs_export_update_export_data",
    ),
    path(
        "add-export",
        lfs.manage.views.export.add_export,
        name="lfs_export_add_export",
    ),
    path(
        "delete-export/<int:export_id>",
        lfs.manage.views.export.delete_export,
        name="lfs_export_delete_export",
    ),
    path(
        "export-export/<slug>",
        lfs.manage.views.export.export,
        name="lfs_export_export",
    ),
    path(
        "update-category-variants-option/<int:export_id>/<int:category_id>",
        lfs.manage.views.export.update_category_variants_option,
        name="lfs_export_update_category_variants_option",
    ),
    # Utils
    path(
        "utilities",
        lfs.manage.views.utils.utilities,
        name="lfs_manage_utils",
    ),
    path(
        "clear-cache",
        lfs.manage.views.utils.clear_cache,
        name="lfs_clear_cache",
    ),
    path(
        "set-category-levels",
        lfs.manage.views.utils.set_category_levels,
        name="lfs_set_category_levels",
    ),
    path(
        "update-effective-price",
        lfs.manage.views.utils.update_effective_price,
        name="lfs_update_effective_price",
    ),
    path(
        "reindex-topseller",
        lfs.manage.views.utils.reindex_topseller,
        name="lfs_reindex_topseller",
    ),
    # Information
    path(
        "environment",
        lfs.manage.information.views.environment,
        name="lfs_manage_environment",
    ),
]

# Manufacturer / SEO
urlpatterns += SEOView.get_seo_urlpattern(Manufacturer)
urlpatterns += ShopSEOView.get_seo_urlpattern(Shop)
urlpatterns += SEOView.get_seo_urlpattern(Product, form_klass=ProductSEOForm, template_name="manage/products/seo.html")
urlpatterns += SEOView.get_seo_urlpattern(Category)
