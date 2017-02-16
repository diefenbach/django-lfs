from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^category-(?P<slug>[-\w]*)/$', views.category_view, name="lfs_category"),
    url(r'^product/(?P<slug>[-\w]*)/$', views.product_view, name="lfs_product"),
    url(r'^product-form-dispatcher/$', views.product_form_dispatcher, name="lfs_product_dispatcher"),
    url(r'^set-sorting/$', views.set_sorting, name="lfs_catalog_set_sorting"),
    url(r'^set-product-number-filter/$', views.set_number_filter, name="lfs_set_product_number_filter"),
    url(r'^set-product-filter/(?P<category_slug>[-\w]+)/(?P<property_group_id>\d+)/(?P<property_id>\d+)/(?P<value>.+)/$', views.set_filter, name="lfs_set_product_filter"),
    url(r'^set-price-filter/(?P<category_slug>[-\w]+)/$', views.set_price_filter, name="lfs_set_price_filter"),
    url(r'^set-manufacturer-filter/(?P<category_slug>[-\w]+)/(?P<manufacturer_id>\d+)/$', views.set_manufacturer_filter, name="lfs_set_manufacturer_filter"),
    url(r'^reset-price-filter/(?P<category_slug>[-\w]+)/$', views.reset_price_filter, name="lfs_reset_price_filter"),
    url(r'^reset-number-filter/(?P<category_slug>[-\w]+)/(?P<property_group_id>\d+)/(?P<property_id>\d+)/$', views.reset_number_filter, name="lfs_reset_number_filter"),
    url(r'^reset-product-filter/(?P<category_slug>[-\w]+)/(?P<property_group_id>\d+)/(?P<property_id>\d+)/$', views.reset_filter, name="lfs_reset_product_filter"),
    url(r'^reset-manufacturer-filter/(?P<category_slug>[-\w]+)/(?P<manufacturer_id>\d+)/$', views.reset_manufacturer_filter, name="lfs_reset_manufacturer_filter"),
    url(r'^reset-all-manufacturer-filter/(?P<category_slug>[-\w]+)/$', views.reset_all_manufacturer_filter, name="lfs_reset_all_manufacturer_filter"),
    url(r'^reset-all-product-filter/(?P<category_slug>[-\w]+)/$', views.reset_all_filter, name="lfs_reset_all_product_filter"),
    url(r'^select-variant/$', views.select_variant, name="lfs_select_variant"),
    url(r'^select-variant-from-properties/$', views.select_variant_from_properties, name="lfs_select_variant_from_properties"),
    url(r'^file/(?P<file_id>[-\w]*)/$', views.file_download, name="lfs_file"),
    url(r'^calculate-price/(?P<id>[-\w]*)/$', views.calculate_price, name="lfs_calculate_price"),
    url(r'^calculate-packing/(?P<id>[-\w]*)/$', views.calculate_packing, name="lfs_calculate_packing"),
]
