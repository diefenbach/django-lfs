from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('django.views.generic.simple',
    (r'^products-new', 'direct_to_template', {'template': 'manage/new/product.html'}),
)

# General
urlpatterns += patterns('lfs.manage.views',
    url(r'^$', "dashboard", name="lfs_manage_dashboard"),
)

urlpatterns += patterns('lfs.manage.views.delivery_times',
    url(r'^delivery_times$', "manage_delivery_times", name="lfs_manage_delivery_times"),
    url(r'^delivery_time/(?P<id>\d*)$', "manage_delivery_time", name="lfs_manage_delivery_time"),
    url(r'^add-delivery-time$', "add_delivery_time", name="lfs_add_delivery_time"),
    url(r'^delete-delivery-time/(?P<id>\d*)$', "delete_delivery_time", name="lfs_delete_delivery_time"),
)

# Manufacturer
urlpatterns += patterns('lfs.manage.views.manufacturer',
    url(r'^manufacturer-dispatcher$', "manufacturer_dispatcher", name="lfs_manufacturer_dispatcher"),
    url(r'^manufacturer/(?P<manufacturer_id>\d*)$', "manage_manufacturer", name="lfs_manufacturer"),
    url(r'^update-manufacturer-data/(?P<manufacturer_id>\d*)$', "update_data", name="lfs_manufacturer_update_manufacturer_data"),
    url(r'^add-manufacturer$', "add_manufacturer", name="lfs_manufacturer_add_manufacturer"),
    url(r'^delete-manufacturer/(?P<manufacturer_id>\d*)$', "delete_manufacturer", name="lfs_manufacturer_delete_manufacturer"),
    url(r'^edit-category-manufacturer/(?P<manufacturer_id>\d*)/(?P<category_id>\d*)$', "edit_category", name="lfs_manufacturer_edit_category"),
    url(r'^edit-product-manufacturer/(?P<manufacturer_id>\d*)/(?P<product_id>\d*)$', "edit_product", name="lfs_manufacturer_edit_product"),
    url(r'^category-state-manufacturer/(?P<manufacturer_id>\d*)/(?P<category_id>\d*)$', "category_state", name="lfs_manufacturer_category_state"),
    url(r'^manufacturer-inline/(?P<manufacturer_id>\d*)/(?P<category_id>\d*)$', "manufacturer_inline", name="lfs_manufacturer_inline"),
)

# Marketing
urlpatterns += patterns('lfs.manage.views.marketing',
    url(r'^featured$', "marketing.manage_featured_page", name="lfs_manage_featured"),
    url(r'^add-featured$', "featured.add_featured", name="lfs_manage_add_featured"),
    url(r'^update-featured$', "featured.update_featured", name="lfs_manage_update_featured"),
    url(r'^featured-inline$', "featured.manage_featured_inline", name="lfs_manage_featured_inline"),
    url(r'^marketing$', "marketing.manage_marketing", name="lfs_manage_marketing"),
    url(r'^manage-rating-mails$', "rating_mails.manage_rating_mails", name="lfs_manage_rating_mails"),
    url(r'^add-topseller$', "topseller.add_topseller", name="lfs_manage_add_topseller"),
    url(r'^update-topseller$', "topseller.update_topseller", name="lfs_manage_update_topseller"),
    url(r'^topseller-inline$', "topseller.manage_topseller_inline", name="lfs_manage_topseller_inline"),
    url(r'^send-rating-mails$', "rating_mails.send_rating_mails", name="lfs_send_rating_mails"),
)

# Voucher
urlpatterns += patterns('lfs.manage.views.voucher',
    url(r'^manage-vouchers$', "manage_vouchers", name="lfs_manage_vouchers"),
    url(r'^add-voucher-group$', "add_voucher_group", name="lfs_manage_add_voucher_group"),
    url(r'^manage-voucher-group/(?P<id>\d+)$', "voucher_group", name="lfs_manage_voucher_group"),
    url(r'^delete-voucher-group/(?P<id>\d+)$', "delete_voucher_group", name="lfs_delete_voucher_group"),
    url(r'^save-voucher-group-data/(?P<id>\d+)$', "save_voucher_group_data", name="lfs_manage_save_voucher_group_data"),
    url(r'^save-voucher-options$', "save_voucher_options", name="lfs_manage_save_voucher_options"),
    url(r'^add-vouchers/(?P<group_id>\d+)$', "add_vouchers", name="lfs_manage_add_vouchers"),
    url(r'^delete-vouchers/(?P<group_id>\d+)$', "delete_vouchers", name="lfs_manage_delete_vouchers"),
    url(r'^set-vouchers-page$', "set_vouchers_page", name="lfs_set_vouchers_page"),
)

# Portlets
urlpatterns += patterns('lfs.manage.views.lfs_portlets',
    url(r'^add-portlet/(?P<object_type_id>\d+)/(?P<object_id>\d+)$', "add_portlet", name="lfs_add_portlet"),
    url(r'^update-portlets/(?P<object_type_id>\d+)/(?P<object_id>\d+)$', "update_portlets", name="lfs_update_portlets"),
    url(r'^delete-portlet/(?P<portletassignment_id>\d+)$', "delete_portlet", name="lfs_delete_portlet"),
    url(r'^edit-portlet/(?P<portletassignment_id>\d+)$', "edit_portlet", name="lfs_edit_portlet"),
)

# Product
urlpatterns += patterns('lfs.manage.views',
    url(r'^product-dispatcher$', "product_dispatcher", name="lfs_manage_product_dispatcher"),
    url(r'^product-by-id/(?P<product_id>\d*)$', "product_by_id", name="lfs_product_by_id"),
    url(r'^product/(?P<product_id>\d*)$', "manage_product", name="lfs_manage_product"),
    url(r'^product-data-form/(?P<product_id>\d*)$', "product_data_form"),
    url(r'^add-product$', "add_product", name="lfs_manage_add_product"),
    url(r'^edit-product-data/(?P<product_id>\d*)$', "edit_product_data"),
    url(r'^delete-product/(?P<product_id>\d*)$', "delete_product", name="lfs_manage_delete_product"),
    url(r'^selectable-products-inline$', "selectable_products_inline", name="lfs_manage_selectable_products_inline"),
    url(r'^save-product-stock/(?P<product_id>\d*)$', "stock", name="lfs_save_product_stock"),
    url(r'^change-product-subtype/(?P<product_id>\d*)$', "change_subtype", name="lfs_change_product_subtype"),
    url(r'^products$', "products", name="lfs_manage_products"),
    url(r'^products-inline$', "products_inline", name="lfs_products_inline"),
    url(r'^save-products$', "save_products", name="lfs_manage_save_products"),
    url(r'^set-product-filters$', "set_filters", name="lfs_set_product_filters"),
    url(r'^set-product-name-filter$', "set_name_filter", name="lfs_set_product_name_filter"),
    url(r'^reset-product-filters$', "reset_filters", name="lfs_reset_product_filters"),
    url(r'^set-products-page$', "set_products_page", name="lfs_set_products_page"),
)

urlpatterns += patterns('lfs.manage.views.product',
    url(r'^product-categories-tab/(?P<product_id>\d*)$', "categories.manage_categories", name="lfs_product_categories_tab"),
    url(r'^product-accessories-tab/(?P<product_id>\d*)$', "accessories.load_tab", name="lfs_manage_product_accessories_tab"),
    url(r'^product-relateds-tab/(?P<product_id>\d*)$', "related_products.load_tab", name="lfs_manage_product_related_products_tab"),
    url(r'^product-variants-tab/(?P<product_id>\d*)$', "variants.manage_variants", name="lfs_manage_product_variants_tab"),
)

urlpatterns += patterns('lfs.manage.views',
    url(r'^change-product-categories/(?P<product_id>\d*)$', "change_categories", name="lfs_manage_product_categories"),
)

# Product Images
urlpatterns += patterns('lfs.manage.views.product.images',
    url(r'^add-image/(?P<product_id>\d*)$', "add_image", name="lfs_manage_add_image"),
    url(r'^update-images/(?P<product_id>\d*)$', "update_images", name="lfs_manage_update_images"),
    url(r'^product-images/(?P<product_id>\d*)$', "manage_images", name="lfs_manage_images"),
    url(r'^update-active-images/(?P<product_id>\d*)$', "update_active_images", name="lfs_manage_update_active_images"),
    url(r'^move-image/(?P<id>\d+)$', "move_image", name="lfc_move_image"),
)

# Product SEO
urlpatterns += patterns('lfs.manage.views',
    url(r'^manage-seo/(?P<product_id>\d*)$', "manage_seo", name="lfs_manage_product_seo"),
)

# Variants
urlpatterns += patterns('lfs.manage.views.product.variants',
    url(r'^properties/(?P<product_id>\d*)$', "manage_variants"),
    url(r'^add-property/(?P<product_id>\d*)$', "add_property"),
    url(r'^add-property-option/(?P<product_id>\d*)$', "add_property_option"),
    url(r'^delete-property/(?P<product_id>\d*)/(?P<property_id>\d*)$', "delete_property"),
    url(r'^delete-property-option/(?P<product_id>\d*)/(?P<option_id>\d*)$', "delete_property_option"),
    url(r'^change-property-position$', "change_property_position"),
    url(r'^update-variants/(?P<product_id>\d*)$', "update_variants", name="lfs_manage_update_variants"),
    url(r'^add-variants/(?P<product_id>\d*)$', "add_variants", name="lfs_add_variants"),
    url(r'^edit-sub-type/(?P<product_id>\d*)$', "edit_sub_type", name="lfs_edit_sub_type"),
    url(r'^update-default-variant/(?P<product_id>\d*)$', "update_default_variant", name="lfs_update_default_variant"),
)

# Property Groups
urlpatterns += patterns('lfs.manage.views.property_groups.property_groups',
    url(r'^property-groups', "manage_property_groups", name="lfs_manage_property_groups"),
    url(r'^property-group/(?P<id>\d*)', "manage_property_group", name="lfs_manage_property_group"),
    url(r'^add-property-group', "add_property_group", name="lfs_add_property_group"),
    url(r'^delete-property-group/(?P<id>\d*)', "delete_property_group", name="lfs_delete_property_group"),
    url(r'^assign-properties/(?P<group_id>\d*)', "assign_properties", name="lfs_assign_properties"),
    url(r'^update-properties/(?P<group_id>\d*)', "update_properties", name="lfs_update_properties"),
)

# Property Groups / Products
urlpatterns += patterns('lfs.manage.views.property_groups.products',
    url(r'^assign-products-to-property-group/(?P<group_id>\d*)', "assign_products", name="lfs_assign_products_to_property_group"),
    url(r'^remove-products-from-property-group/(?P<group_id>\d*)', "remove_products", name="lfs_pg_remove_products"),
    url(r'^pg-products-inline/(?P<product_group_id>\d*)', "products_inline", name="lfs_pg_products_inline"),
)

# Shop Properties
urlpatterns += patterns('lfs.manage.views.properties',
    url(r'^shop-properties$', "manage_properties", name="lfs_manage_shop_properties"),
    url(r'^shop-property/(?P<id>\d*)', "manage_property", name="lfs_manage_shop_property"),
    url(r'^update-shop-property-type/(?P<id>\d*)', "update_property_type", name="lfs_update_shop_property_type"),
    url(r'^add-shop-property$', "add_property", name="lfs_add_shop_property"),
    url(r'^delete-shop-property/(?P<id>\d*)', "delete_property", name="lfs_delete_shop_property"),
    url(r'^add-shop-property-option/(?P<property_id>\d*)', "add_option", name="lfs_add_shop_property_option"),
    url(r'^add-shop-property-step/(?P<property_id>\d*)', "add_step", name="lfs_add_shop_property_step"),
    url(r'^save-shop-property-step/(?P<property_id>\d*)', "save_step_range", name="lfs_save_shop_property_step_range"),
    url(r'^save-shop-property-step-type/(?P<property_id>\d*)', "save_step_type", name="lfs_save_shop_property_step_type"),
    url(r'^delete-shop-property-option/(?P<id>\d*)', "delete_option", name="lfs_delete_shop_property_option"),
    url(r'^delete-shop-property-step/(?P<id>\d*)', "delete_step", name="lfs_delete_shop_property_step"),

    url(r'^save-number-field-validators/(?P<property_id>\d*)', "save_number_field_validators", name="lfs_save_number_field_validators"),
    url(r'^save-select-field/(?P<property_id>\d*)', "save_select_field", name="lfs_save_select_field"),
)

# Product properties
urlpatterns += patterns('lfs.manage.views.product.properties',
    url(r'^update-product-properties/(?P<product_id>\d*)$', "update_properties", name="lfs_update_product_properties"),
    url(r'^update-product-property-groups/(?P<product_id>\d*)$', "update_property_groups", name="lfs_update_product_property_groups"),

)

# Accesories
urlpatterns += patterns('lfs.manage.views',
    url(r'^accessories/(?P<product_id>\d*)$', "manage_accessories"),
    url(r'^accessories-inline/(?P<product_id>\d*)$', "manage_accessories_inline"),
    url(r'^add-accessories/(?P<product_id>\d*)$', "add_accessories"),
    url(r'^remove-accessories/(?P<product_id>\d*)$', "remove_accessories"),
    url(r'^update-accessories/(?P<product_id>\d*)$', "update_accessories", name="lfs_manage_update_accessories"),
)

# Related Products
urlpatterns += patterns('lfs.manage.views',
    url(r'^related-products/(?P<product_id>\d*)$', "manage_related_products"),
    url(r'^related-products-inline/(?P<product_id>\d*)$', "manage_related_products_inline"),
    url(r'^add-related-products/(?P<product_id>\d*)$', "add_related_products"),
    url(r'^remove-related-products/(?P<product_id>\d*)$', "remove_related_products"),
    url(r'^manage-related-products/(?P<product_id>\d*)$', "update_related_products", name="lfs_manage_update_related_products"),
)

# Carts
urlpatterns += patterns('lfs.manage.views.carts',
    url(r'^carts$', "carts_view", name="lfs_manage_carts"),
    url(r'^carts-inline$', "carts_inline", name="lfs_carts_inline"),
    url(r'^cart-inline/(?P<cart_id>\d*)$', "cart_inline", name="lfs_cart_inline"),
    url(r'^cart/(?P<cart_id>\d*)$', "cart_view", name="lfs_manage_cart"),
    url(r'^selectable-carts-inline$', "selectable_carts_inline", name="lfs_selectable_carts_inline"),
    url(r'^set-cart-filters$', "set_cart_filters", name="lfs_set_cart_filters"),
    url(r'^set-cart-filters-date$', "set_cart_filters_date", name="lfs_set_cart_filters_date"),
    url(r'^reset-cart-filters$', "reset_cart_filters", name="lfs_reset_cart_filters"),
)

# Categories
urlpatterns += patterns('lfs.manage.views.categories',
    url(r'^categories$', "manage_categories", name="lfs_manage_categories"),
    url(r'^category/(?P<category_id>\d*)$', "manage_category", name="lfs_manage_category"),
    url(r'^add-products/(?P<category_id>\d*)$', "add_products", name="lfs_manage_category_add_products"),
    url(r'^remove-products/(?P<category_id>\d*)$', "remove_products", name="lfs_manage_category_remove_products"),
    url(r'^add-top-category$', "add_category", name="lfs_manage_add_top_category"),
    url(r'^add-category/(?P<category_id>\d*)$', "add_category", name="lfs_manage_add_category"),
    url(r'^delete-category/(?P<id>[-\w]*)$', "delete_category", name="lfs_delete_category"),
    url(r'^products-inline/(?P<category_id>\d*)$', "products_inline", name="lfs_manage_category_products_inline"),
    url(r'^edit-category-data/(?P<category_id>\d*)$', "edit_category_data", name="lfs_manage_category_edit_data"),
    url(r'^edit-category-view/(?P<category_id>\d*)$', "category_view", name="lfs_manage_category_view"),
    url(r'^selected-products/(?P<category_id>\d*)$', "selected_products", name="lfs_selected_products"),
    url(r'^load-products-tab/(?P<category_id>\d*)$', "products_tab", name="lfs_load_products_tab"),
)

# Categories / SEO
urlpatterns += patterns('lfs.manage.views.categories.seo',
    url(r'^edit-category-seo/(?P<category_id>\d*)$', "edit_seo", name="lfs_manage_category_seo"),
)

# Customers
urlpatterns += patterns('lfs.manage.views.customer',
    url(r'^customers$', "customers", name="lfs_manage_customers"),
    url(r'^customers-inline$', "customers_inline", name="lfs_customers_inline"),
    url(r'^customer/(?P<customer_id>\d*)$', "customer", name="lfs_manage_customer"),
    url(r'^customer-inline/(?P<customer_id>\d*)$', "customer_inline", name="lfs_customer_inline"),
    url(r'^set-customer-filters$', "set_customer_filters", name="lfs_set_customer_filters"),
    url(r'^reset-customer-filters$', "reset_customer_filters", name="lfs_reset_customer_filters"),
    url(r'^set-customer-ordering/(?P<ordering>\w*)$', "set_ordering", name="lfs_set_customer_ordering"),
    url(r'^selectable-customers-inline$', "selectable_customers_inline", name="lfs_selectable_customers_inline"),
)

# Export
urlpatterns += patterns('lfs.manage.views.export',
    url(r'^export-dispatcher$', "export_dispatcher", name="lfs_export_dispatcher"),
    url(r'^export/(?P<export_id>\d*)$', "manage_export", name="lfs_export"),
    url(r'^export-inline/(?P<export_id>\d*)/(?P<category_id>\d*)$', "export_inline", name="lfs_export_inline"),
    url(r'^edit-category/(?P<export_id>\d*)/(?P<category_id>\d*)$', "edit_category", name="lfs_export_edit_category"),
    url(r'^edit-product/(?P<export_id>\d*)/(?P<product_id>\d*)$', "edit_product", name="lfs_export_edit_product"),
    url(r'^category-state/(?P<export_id>\d*)/(?P<category_id>\d*)$', "category_state", name="lfs_export_category_state"),
    url(r'^update-export-data/(?P<export_id>\d*)$', "update_data", name="lfs_export_update_export_data"),
    url(r'^add-export$', "add_export", name="lfs_export_add_export"),
    url(r'^delete-export/(?P<export_id>\d*)$', "delete_export", name="lfs_export_delete_export"),
    url(r'^export-export/(?P<slug>[-\w]*)$', "export", name="lfs_export_export"),
    url(r'^update-category-variants-option/(?P<export_id>\d*)/(?P<category_id>\d*)$', "update_category_variants_option", name="lfs_export_update_category_variants_option"),
)

# Shipping
urlpatterns += patterns('lfs.manage.views',
    url(r'^shipping$', "manage_shipping", name="lfs_manage_shipping"),
    url(r'^shipping-method/(?P<shipping_method_id>\d*)$', "manage_shipping_method", name="lfs_manage_shipping_method"),
    url(r'^add-shipping-method', "add_shipping_method"),
    url(r'^save-shipping-data/(?P<shipping_method_id>\d*)$', "save_shipping_method_data", name="lfs_manage_save_shipping_method_data"),
    url(r'^delete-shipping-method/(?P<shipping_method_id>\d*)$', "delete_shipping_method"),
    url(r'^add-shipping-price/(?P<shipping_method_id>\d*)$', "add_shipping_price", name="lfs_manage_add_shipping_price"),
    url(r'^update-shipping-prices/(?P<shipping_method_id>\d*)$', "update_shipping_prices", name="lfs_manage_update_shipping_prices"),
    url(r'^shipping-price-criteria/(?P<shipping_price_id>\d*)$', "shipping_price_criteria", name="lfs_manage_shipping_price_criteria"),
    url(r'^save-shipping-price-criteria/(?P<shipping_price_id>\d*)$', "save_shipping_price_criteria", name="lfs_manage_save_shipping_price_criteria"),
    url(r'^save-shipping-method-criteria/(?P<shipping_method_id>\d*)$', "save_shipping_method_criteria", name="lfs_manage_save_shipping_method_criteria"),
)

# Discounts
urlpatterns += patterns('lfs.manage.views.discounts',
    url(r'^discounts$', "manage_discounts", name="lfs_manage_discounts"),
    url(r'^discount/(?P<id>\d*)$', "manage_discount", name="lfs_manage_discount"),
    url(r'^add-discount', "add_discount", name="lfs_manage_add_discount"),
    url(r'^save-discount-data/(?P<id>\d*)$', "save_discount_data", name="lfs_manage_save_discount_data"),
    url(r'^delete-discount/(?P<id>\d*)$', "delete_discount", name="lfs_manage_delete_discount"),
    url(r'^save-discount-criteria/(?P<id>\d*)$', "save_discount_criteria", name="lfs_manage_save_discount_criteria"),
)

# Pages
urlpatterns += patterns('lfs.manage.views.page',
    url(r'^add-page$', "add_page", name="lfs_add_page"),
    url(r'^delete-page/(?P<id>\d*)$', "delete_page", name="lfs_delete_page"),
    url(r'^manage-pages$', "manage_pages", name="lfs_manage_pages"),
    url(r'^manage-page/(?P<id>\d*)$', "manage_page", name="lfs_manage_page"),
)

# Payment
urlpatterns += patterns('lfs.manage.views.payment',
    url(r'^payment$', "manage_payment", name="lfs_manage_payment"),
    url(r'^payment-method/(?P<payment_method_id>\d*)$', "manage_payment_method", name="lfs_manage_payment_method"),
    url(r'^add-payment-method', "add_payment_method", name="lfs_add_payment_method"),
    url(r'^save-payment-data/(?P<payment_method_id>\d*)$', "save_payment_method_data", name="lfs_manage_save_payment_method_data"),
    url(r'^delete-payment-method/(?P<payment_method_id>\d*)$', "delete_payment_method", name="lfs_delete_payment_method"),
    url(r'^add-payment-price/(?P<payment_method_id>\d*)$', "add_payment_price", name="lfs_manage_add_payment_price"),
    url(r'^update-payment-prices/(?P<payment_method_id>\d*)$', "update_payment_prices", name="lfs_manage_update_payment_prices"),
    url(r'^payment-price-criteria/(?P<payment_price_id>\d*)$', "payment_price_criteria", name="lfs_manage_payment_price_criteria"),
    url(r'^save-payment-price-criteria/(?P<payment_price_id>\d*)$', "save_payment_price_criteria", name="lfs_manage_save_payment_price_criteria"),
    url(r'^save-payment-method-criteria/(?P<payment_method_id>\d*)$', "save_payment_method_criteria", name="lfs_manage_save_payment_method_criteria"),
)

# Orders
urlpatterns += patterns('lfs.manage.views.orders',
    url(r'^manage-orders$', "manage_orders", name="lfs_manage_orders"),
    url(r'^orders$', "orders_view", name="lfs_orders"),
    url(r'^orders-inline$', "orders_inline", name="lfs_orders_inline"),
    url(r'^order/(?P<order_id>\d*)$', "order_view", name="lfs_manage_order"),
    url(r'^delete-order/(?P<order_id>\d*)$', "delete_order", name="lfs_delete_order"),
    url(r'^send-order/(?P<order_id>\d*)$', "send_order", name="lfs_send_order"),
    url(r'^set-orders-filter$', "set_order_filters", name="lfs_set_order_filter"),
    url(r'^set-orders-filter-date$', "set_order_filters_date", name="lfs_set_order_filters_date"),
    url(r'^reset-order-filter$', "reset_order_filters", name="lfs_reset_order_filters"),
    url(r'^selectable-orders-inline$', "selectable_orders_inline", name="lfs_selectable_orders_inline"),
    url(r'^change-order-state$', "change_order_state", name="lfs_change_order_state"),
)

# Criteria
urlpatterns += patterns('lfs.manage.views.criteria',
    url(r'^add-criterion', "add_criterion", name="lfs_add_criterion"),
    url(r'^change-criterion', "change_criterion_form", name="lfs_manage_criteria_change_criterion_form"),
)

# Static blocks
urlpatterns += patterns('lfs.manage.views.static_blocks',
    url(r'^add-static-block$', "add_static_block", name="lfs_add_static_block"),
    url(r'^delete-static-block/(?P<id>\d*)$', "delete_static_block", name="lfs_delete_static_block"),
    url(r'^preview-static-block/(?P<id>\d*)$', "preview_static_block", name="lfs_preview_static_block"),
    url(r'^manage-static-blocks$', "manage_static_blocks", name="lfs_manage_static_blocks"),
    url(r'^manage-static-block/(?P<id>\d*)$', "manage_static_block", name="lfs_manage_static_block"),
    url(r'^add_files/(?P<id>[-\w]*)', "add_files", name="lfs_add_files_to_static_block"),
    url(r'^update_files/(?P<id>[-\w]*)', "update_files", name="lfs_manage_update_files_sb"),
    url(r'^reload_files/(?P<id>[-\w]*)', "reload_files", name="lfs_reload_files"),
)

# Reviews
# urlpatterns += patterns('lfs.manage.views.review',
#     url(r'^manage-reviews$', "manage_reviews", name="lfs_manage_reviews"),
#     url(r'^manage-review/(?P<review_id>\d*)$', "manage_review", name="lfs_manage_review"),
#     url(r'^add-review$', "add_review", name="lfs_add_review"),
#     url(r'^delete-review/(?P<review_id>\d*)$', "delete_review", name="lfs_delete_review"),
# )

# Reviews
urlpatterns += patterns('lfs.manage.views.review',
    url(r'^reviews$', "reviews", name="lfs_manage_reviews"),
    url(r'^reviews-inline$', "reviews_inline", name="lfs_reviews_inline"),
    url(r'^review/(?P<review_id>\d*)$', "review", name="lfs_manage_review"),
    url(r'^review-inline/(?P<review_id>\d*)$', "review_inline", name="lfs_review_inline"),
    url(r'^set-review-filters$', "set_review_filters", name="lfs_set_review_filters"),
    url(r'^reset-review-filters$', "reset_review_filters", name="lfs_reset_review_filters"),
    url(r'^set-review-ordering/(?P<ordering>\w*)$', "set_ordering", name="lfs_set_review_ordering"),
    url(r'^selectable-reviews-inline$', "selectable_reviews_inline", name="lfs_selectable_reviews_inline"),
    url(r'^set-review-state/(?P<review_id>\d*)$', "set_state", name="lfs_set_review_state"),
    url(r'^delete-review/(?P<review_id>\d*)$', "delete_review", name="lfs_delete_review"),
)

# Shop
urlpatterns += patterns('lfs.manage.views.shop',
    url(r'^shop$', "manage_shop", name="lfs_manage_shop"),
    url(r'^save-shop-default-values$', "save_default_values", name="lfs_save_shop_default_values"),
)

# Shop action
urlpatterns += patterns('lfs.manage.views.actions',
    url(r'^add-action$', "add_action", name="lfs_add_action"),
    url(r'^delete-action/(?P<id>\d*)$', "delete_action", name="lfs_delete_action"),
    url(r'^manage-actions$', "manage_actions", name="lfs_manage_actions"),
    url(r'^manage-action/(?P<id>\d*)$', "manage_action", name="lfs_manage_action"),
)

# Tax
urlpatterns += patterns('lfs.manage.views.tax',
    url(r'^add-tax$', "add_tax", name="lfs_add_tax"),
    url(r'^delete-tax/(?P<id>\d*)$', "delete_tax", name="lfs_delete_tax"),
    url(r'^manage-taxes$', "manage_taxes", name="lfs_manage_taxes"),
    url(r'^manage-tax/(?P<id>\d*)$', "manage_tax", name="lfs_manage_tax"),
)

# Utils
urlpatterns += patterns('lfs.manage.views.utils',
    url(r'^utilities$', "utilities", name="lfs_manage_utils"),
    url(r'^clear-cache$', "clear_cache", name="lfs_clear_cache"),
    url(r'^set-category-levels$', "set_category_levels", name="lfs_set_category_levels"),
    url(r'^update-effective-price$', "update_effective_price", name="lfs_update_effective_price"),
    url(r'^reindex-topseller$', "reindex_topseller", name="lfs_reindex_topseller"),
)
