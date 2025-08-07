from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^category-(?P<slug>[-\w]*)/$", views.category_view, name="lfs_category"),
    re_path(r"^product/(?P<slug>[-\w]*)/$", views.product_view, name="lfs_product"),
    re_path(r"^product-form-dispatcher/$", views.product_form_dispatcher, name="lfs_product_dispatcher"),
    re_path(r"^set-sorting/$", views.set_sorting, name="lfs_catalog_set_sorting"),
    re_path(r"^set-product-number-filter/$", views.set_number_filter, name="lfs_set_product_number_filter"),
    re_path(
        r"^set-product-filter/(?P<category_slug>[-\w]+)/(?P<property_group_id>\d+)/(?P<property_id>\d+)/(?P<value>.+)/$",
        views.set_filter,
        name="lfs_set_product_filter",
    ),
    re_path(r"^set-price-filter/(?P<category_slug>[-\w]+)/$", views.set_price_filter, name="lfs_set_price_filter"),
    re_path(
        r"^set-manufacturer-filter/(?P<category_slug>[-\w]+)/(?P<manufacturer_id>\d+)/$",
        views.set_manufacturer_filter,
        name="lfs_set_manufacturer_filter",
    ),
    re_path(
        r"^reset-price-filter/(?P<category_slug>[-\w]+)/$", views.reset_price_filter, name="lfs_reset_price_filter"
    ),
    re_path(
        r"^reset-number-filter/(?P<category_slug>[-\w]+)/(?P<property_group_id>\d+)/(?P<property_id>\d+)/$",
        views.reset_number_filter,
        name="lfs_reset_number_filter",
    ),
    re_path(
        r"^reset-product-filter/(?P<category_slug>[-\w]+)/(?P<property_group_id>\d+)/(?P<property_id>\d+)/$",
        views.reset_filter,
        name="lfs_reset_product_filter",
    ),
    re_path(
        r"^reset-manufacturer-filter/(?P<category_slug>[-\w]+)/(?P<manufacturer_id>\d+)/$",
        views.reset_manufacturer_filter,
        name="lfs_reset_manufacturer_filter",
    ),
    re_path(
        r"^reset-all-manufacturer-filter/(?P<category_slug>[-\w]+)/$",
        views.reset_all_manufacturer_filter,
        name="lfs_reset_all_manufacturer_filter",
    ),
    re_path(
        r"^reset-all-product-filter/(?P<category_slug>[-\w]+)/$",
        views.reset_all_filter,
        name="lfs_reset_all_product_filter",
    ),
    re_path(r"^select-variant/$", views.select_variant, name="lfs_select_variant"),
    re_path(
        r"^select-variant-from-properties/$",
        views.select_variant_from_properties,
        name="lfs_select_variant_from_properties",
    ),
    re_path(r"^file/(?P<file_id>[-\w]*)/$", views.file_download, name="lfs_file"),
    re_path(r"^calculate-price/(?P<id>[-\w]*)/$", views.calculate_price, name="lfs_calculate_price"),
    re_path(r"^calculate-packing/(?P<id>[-\w]*)/$", views.calculate_packing, name="lfs_calculate_packing"),
]
