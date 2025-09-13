from django.urls import path, include
import lfs.manage
import lfs.manage.images.views
import lfs.manage.information.views
import lfs.manage.products

# Removed imports for non-existent product modules
import lfs.manage.views.utils


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
    path("", include("lfs.manage.exports.urls")),
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
