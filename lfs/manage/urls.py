from django.urls import path, include

# Removed imports for non-existent product modules


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
    # path("", include("lfs.manage.exports.urls")),
    path("", include("lfs.manage.featured.urls")),
    path("", include("lfs.manage.images.urls")),
    path("", include("lfs.manage.information.urls")),
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
    path("", include("lfs.manage.utils.urls")),
    path("", include("lfs.manage.voucher.urls")),
]
