# django imports
from django.conf.urls import patterns, url, include

# lfs imports
from lfs.core.sitemap import CategorySitemap
from lfs.core.sitemap import PageSitemap
from lfs.core.sitemap import ProductSitemap
from lfs.core.sitemap import ShopSitemap
from lfs.core.views import one_time_setup, TextTemplateView

# Robots
urlpatterns = patterns('django.views.generic.simple',
    (r'^robots.txt$', TextTemplateView.as_view(template_name='lfs/shop/robots.txt'))
)

# Sitemaps
urlpatterns += patterns("django.contrib.sitemaps.views",
    url(r'^sitemap.xml$', 'sitemap', {'sitemaps': {"products": ProductSitemap, "categories": CategorySitemap, "pages": PageSitemap, "shop": ShopSitemap}})
)

# Shop
urlpatterns += patterns('lfs.core.views',
    url(r'^$', "shop_view", name="lfs_shop_view"),
)

# Cart
urlpatterns += patterns('lfs.cart.views',
    url(r'^add-to-cart$', "add_to_cart", name="lfs_add_to_cart"),
    url(r'^add-accessory-to-cart/(?P<product_id>\d*)/(?P<quantity>.*)$', "add_accessory_to_cart", name="lfs_add_accessory_to_cart"),
    url(r'^added-to-cart$', "added_to_cart", name="lfs_added_to_cart"),
    url(r'^delete-cart-item/(?P<cart_item_id>\d*)$', "delete_cart_item", name="lfs_delete_cart_item"),
    url(r'^refresh-cart$', "refresh_cart", name="lfs_refresh_cart"),
    url(r'^cart$', "cart", name="lfs_cart"),
    url(r'^check-voucher-cart/$', "check_voucher", name="lfs_check_voucher_cart"),
)

# Catalog
urlpatterns += patterns('lfs.catalog.views',
    url(r'^category-(?P<slug>[-\w]*)$', "category_view", name="lfs_category"),
    url(r'^product/(?P<slug>[-\w]*)$', "product_view", name="lfs_product"),
    url(r'^product-form-dispatcher', "product_form_dispatcher", name="lfs_product_dispatcher"),
    url(r'^set-sorting', "set_sorting", name="lfs_catalog_set_sorting"),
    url(r'^set-product-number-filter', "set_number_filter", name="lfs_set_product_number_filter"),
    url(r'^set-product-filter/(?P<category_slug>[-\w]+)/(?P<property_group_id>\d+)/(?P<property_id>\d+)/(?P<value>.+)', "set_filter", name="lfs_set_product_filter"),
    url(r'^set-price-filter/(?P<category_slug>[-\w]+)/$', "set_price_filter", name="lfs_set_price_filter"),
    url(r'^set-manufacturer-filter/(?P<category_slug>[-\w]+)/(?P<manufacturer_id>\d+)/$', "set_manufacturer_filter", name="lfs_set_manufacturer_filter"),
    url(r'^reset-price-filter/(?P<category_slug>[-\w]+)/$', "reset_price_filter", name="lfs_reset_price_filter"),
    url(r'^reset-number-filter/(?P<category_slug>[-\w]+)/(?P<property_group_id>\d+)/(?P<property_id>\d+)', "reset_number_filter", name="lfs_reset_number_filter"),
    url(r'^reset-product-filter/(?P<category_slug>[-\w]+)/(?P<property_group_id>\d+)/(?P<property_id>\d+)', "reset_filter", name="lfs_reset_product_filter"),
    url(r'^reset-manufacturer-filter/(?P<category_slug>[-\w]+)/(?P<manufacturer_id>\d+)', "reset_manufacturer_filter", name="lfs_reset_manufacturer_filter"),
    url(r'^reset-all-manufacturer-filter/(?P<category_slug>[-\w]+)', "reset_all_manufacturer_filter", name="lfs_reset_all_manufacturer_filter"),
    url(r'^reset-all-product-filter/(?P<category_slug>[-\w]+)', "reset_all_filter", name="lfs_reset_all_product_filter"),
    url(r'^select-variant$', "select_variant", name="lfs_select_variant"),
    url(r'^select-variant-from-properties$', "select_variant_from_properties", name="lfs_select_variant_from_properties"),
    url(r'^file/(?P<file_id>[-\w]*)', "file_download", name="lfs_file"),
    url(r'^calculate-price/(?P<id>[-\w]*)', "calculate_price", name="lfs_calculate_price"),
    url(r'^calculate-packing/(?P<id>[-\w]*)', "calculate_packing", name="lfs_calculate_packing"),
)

# Checkout
urlpatterns += patterns('lfs.checkout.views',
    url(r'^checkout-dispatcher', "checkout_dispatcher", name="lfs_checkout_dispatcher"),
    url(r'^checkout-login', "login", name="lfs_checkout_login"),
    url(r'^checkout', "one_page_checkout", name="lfs_checkout"),
    url(r'^thank-you', "thank_you", name="lfs_thank_you"),
    url(r'^changed-checkout/$', "changed_checkout", name="lfs_changed_checkout"),
    url(r'^changed-invoice-country/$', "changed_invoice_country", name="lfs_changed_invoice_country"),
    url(r'^changed-shipping-country/$', "changed_shipping_country", name="lfs_changed_shipping_country"),
    url(r'^check-voucher/$', "check_voucher", name="lfs_check_voucher"),
)

# Customer
urlpatterns += patterns('lfs.customer.views',
    url(r'^login', "login", name="lfs_login"),
    url(r'^logout', "logout", name="lfs_logout"),
    url(r'^my-account', "account", name="lfs_my_account"),
    url(r'^my-addresses', "addresses", name="lfs_my_addresses"),
    url(r'^my-email', "email", name="lfs_my_email"),
    url(r'^my-orders', "orders", name="lfs_my_orders"),
    url(r'^my-order/(?P<id>\d+)', "order", name="lfs_my_order"),
    url(r'^my-password', "password", name="lfs_my_password"),
)

# Manufacturers
urlpatterns += patterns('lfs.manufacturer.views',
    url(r'^manufacturers/$', "manufacturers", name="lfs_manufacturers"),
    url(r'^manufacturer-(?P<slug>[-\w]*)$', "manufacturer_view", name="lfs_manufacturer"),
)

# Page
urlpatterns += patterns('lfs.page.views',
    url(r'^page/(?P<slug>[-\w]*)$', "page_view", name="lfs_page_view"),
    url(r'^pages/$', "pages_view", name="lfs_pages"),
    url(r'^popup/(?P<slug>[-\w]*)$', "popup_view", name="lfs_popup_view"),
)

# Password reset
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^password-reset/$', "password_reset", name="lfs_password_reset"),
    url(r'^password-reset-done/$', "password_reset_done", name="password_reset_done"),
    url(r'^password-reset-confirm/(?P<uidb64>[-\w]*)/(?P<token>[-\w]*)$', "password_reset_confirm",
        name="password_reset_confirm"),
    url(r'^password-reset-complete/$', "password_reset_complete", name="password_reset_complete"),
)

# Search
urlpatterns += patterns('lfs.search.views',
    url(r'^search', "search", name="lfs_search"),
    url(r'^livesearch', "livesearch", name="lfs_livesearch"),
)

# Contact
urlpatterns += patterns('',
    (r'', include('lfs_contact.urls')),
)

one_time_setup()
