from django.conf.urls import url

import lfs.manage
import lfs.manage.actions.views
import lfs.manage.categories.category
import lfs.manage.categories.portlet
import lfs.manage.categories.products
import lfs.manage.categories.view
import lfs.manage.customer_tax.views
import lfs.manage.discounts.views
import lfs.manage.images.views
import lfs.manage.information.views
import lfs.manage.product
import lfs.manage.product.accessories
import lfs.manage.product.categories
import lfs.manage.product.related_products
import lfs.manage.product.variants
import lfs.manage.product_taxes.views
import lfs.manage.property.views
import lfs.manage.property_groups.views
import lfs.manage.shipping_methods.views
import lfs.manage.static_blocks.views
import lfs.manage.views.carts
import lfs.manage.views.customer
import lfs.manage.views.criteria
import lfs.manage.views.dashboard
import lfs.manage.views.export
import lfs.manage.views.marketing.marketing
import lfs.manage.views.marketing.featured
import lfs.manage.views.marketing.rating_mails
import lfs.manage.views.marketing.topseller
import lfs.manage.views.orders
import lfs.manage.views.payment
import lfs.manage.views.review
import lfs.manage.views.utils
from lfs.catalog.models import Product
from lfs.catalog.models import Category
from lfs.core.models import Shop
from lfs.manage.product.seo import SEOForm as ProductSEOForm
from lfs.manage.pages.views import PageSEOView
from lfs.manage.views.shop import ShopSEOView
from lfs.manage.seo.views import SEOView
from lfs.manage.delivery_times import views as delivery_times_views
from lfs.manage.manufacturers import views as manufacturers_views
from lfs.manage.manufacturers import products as manufacturers_products_views
from lfs.manage.voucher import views as voucher_views
from lfs.manage.views import lfs_portlets
from lfs.manage.product import product
from lfs.manufacturer.models import Manufacturer
from lfs.page.models import Page


urlpatterns = [
    url(r'^$', lfs.manage.views.dashboard.dashboard, name="lfs_manage_dashboard"),

    # Delivery Times
    url(r'^delivery_times$', delivery_times_views.manage_delivery_times, name="lfs_manage_delivery_times"),
    url(r'^delivery_time/(?P<id>\d*)$', delivery_times_views.manage_delivery_time, name="lfs_manage_delivery_time"),
    url(r'^add-delivery-time$', delivery_times_views.add_delivery_time, name="lfs_manage_add_delivery_time"),
    url(r'^delete-delivery-time/(?P<id>\d*)$', delivery_times_views.delete_delivery_time, name="lfs_delete_delivery_time"),
    url(r'^no-times$', delivery_times_views.no_delivery_times, name="lfs_no_delivery_times"),

    # Manufacturer
    url(r'^manufacturer-dispatcher$', manufacturers_views.manufacturer_dispatcher, name="lfs_manufacturer_dispatcher"),
    url(r'^manufacturer/(?P<manufacturer_id>\d*)$', manufacturers_views.manage_manufacturer, name="lfs_manage_manufacturer"),
    url(r'^update-manufacturer-data/(?P<manufacturer_id>\d*)$', manufacturers_views.update_data, name="lfs_manufacturer_update_manufacturer_data"),
    url(r'^add-manufacturer$', manufacturers_views.add_manufacturer, name="lfs_manufacturer_add_manufacturer"),
    url(r'^delete-manufacturer/(?P<manufacturer_id>\d*)$', manufacturers_views.delete_manufacturer, name="lfs_manufacturer_delete_manufacturer"),
    url(r'^edit-category-manufacturer/(?P<manufacturer_id>\d*)/(?P<category_id>\d*)$', manufacturers_views.edit_category, name="lfs_manufacturer_edit_category"),
    url(r'^edit-product-manufacturer/(?P<manufacturer_id>\d*)/(?P<product_id>\d*)$', manufacturers_views.edit_product, name="lfs_manufacturer_edit_product"),
    url(r'^category-state-manufacturer/(?P<manufacturer_id>\d*)/(?P<category_id>\d*)$', manufacturers_views.category_state, name="lfs_manufacturer_category_state"),
    url(r'^manufacturer-inline/(?P<manufacturer_id>\d*)/(?P<category_id>\d*)$', manufacturers_views.manufacturer_inline, name="lfs_manufacturer_inline"),
    url(r'^manufacturers-ajax/$', manufacturers_views.manufacturers_ajax, name="lfs_manufacturers_ajax"),
    url(r'^no-manufacturers$', manufacturers_views.no_manufacturers, name="lfs_manage_no_manufacturers"),
    url(r'^edit-manufacturer-view/(?P<manufacturer_id>\d*)$', manufacturers_views.manufacturer_view, name="lfs_manage_manufacturer_view"),

    url(r'^manufacturer-products-inline/(?P<manufacturer_id>\d*)$', manufacturers_products_views.products_inline, name="lfs_manage_manufacturer_products_inline"),
    url(r'^manufacturer-selected-products/(?P<manufacturer_id>\d*)$', manufacturers_products_views.selected_products, name="lfs_manage_manufacturer_selected_products"),
    url(r'^manufacturer-add-products/(?P<manufacturer_id>\d*)$', manufacturers_products_views.add_products, name="lfs_manage_manufacturer_add_products"),
    url(r'^manufacturer-remove-products/(?P<manufacturer_id>\d*)$', manufacturers_products_views.remove_products, name="lfs_manage_manufacturer_remove_products"),
    url(r'^manufacturer-load-products-tab/(?P<manufacturer_id>\d*)$', manufacturers_products_views.products_tab, name="lfs_manufacturer_load_products_tab"),

    # Marketing
    url(r'^featured$', lfs.manage.views.marketing.marketing.manage_featured_page, name="lfs_manage_featured"),
    url(r'^marketing$', lfs.manage.views.marketing.marketing.manage_marketing, name="lfs_manage_marketing"),
    url(r'^add-featured$', lfs.manage.views.marketing.featured.add_featured, name="lfs_manage_add_featured"),
    url(r'^update-featured$', lfs.manage.views.marketing.featured.update_featured, name="lfs_manage_update_featured"),
    url(r'^featured-inline$', lfs.manage.views.marketing.featured.manage_featured_inline, name="lfs_manage_featured_inline"),
    url(r'^manage-rating-mails$', lfs.manage.views.marketing.rating_mails.manage_rating_mails, name="lfs_manage_rating_mails"),
    url(r'^send-rating-mails$', lfs.manage.views.marketing.rating_mails.send_rating_mails, name="lfs_send_rating_mails"),
    url(r'^add-topseller$', lfs.manage.views.marketing.topseller.add_topseller, name="lfs_manage_add_topseller"),
    url(r'^update-topseller$', lfs.manage.views.marketing.topseller.update_topseller, name="lfs_manage_update_topseller"),
    url(r'^topseller-inline$', lfs.manage.views.marketing.topseller.manage_topseller_inline, name="lfs_manage_topseller_inline"),

    # Voucher
    url(r'^vouchers$', voucher_views.manage_vouchers, name="lfs_manage_vouchers"),
    url(r'^no-vouchers$', voucher_views.no_vouchers, name="lfs_no_vouchers"),
    url(r'^add-voucher-group$', voucher_views.add_voucher_group, name="lfs_manage_add_voucher_group"),
    url(r'^voucher-group/(?P<id>\d+)$', voucher_views.voucher_group, name="lfs_manage_voucher_group"),
    url(r'^delete-voucher-group/(?P<id>\d+)$', voucher_views.delete_voucher_group, name="lfs_delete_voucher_group"),
    url(r'^save-voucher-group-data/(?P<id>\d+)$', voucher_views.save_voucher_group_data, name="lfs_manage_save_voucher_group_data"),
    url(r'^save-voucher-options$', voucher_views.save_voucher_options, name="lfs_manage_save_voucher_options"),
    url(r'^add-vouchers/(?P<group_id>\d+)$', voucher_views.add_vouchers, name="lfs_manage_add_vouchers"),
    url(r'^delete-vouchers/(?P<group_id>\d+)$', voucher_views.delete_vouchers, name="lfs_manage_delete_vouchers"),
    url(r'^set-vouchers-page$', voucher_views.set_vouchers_page, name="lfs_set_vouchers_page"),

    # Portlets
    url(r'^add-portlet/(?P<object_type_id>\d+)/(?P<object_id>\d+)$', lfs_portlets.add_portlet, name="lfs_add_portlet"),
    url(r'^update-portlets/(?P<object_type_id>\d+)/(?P<object_id>\d+)$', lfs_portlets.update_portlets, name="lfs_update_portlets"),
    url(r'^delete-portlet/(?P<portletassignment_id>\d+)$', lfs_portlets.delete_portlet, name="lfs_delete_portlet"),
    url(r'^edit-portlet/(?P<portletassignment_id>\d+)$', lfs_portlets.edit_portlet, name="lfs_edit_portlet"),
    url(r'^move-portlet/(?P<portletassignment_id>\d+)$', lfs_portlets.move_portlet, name="lfs_move_portlet"),

    # Product
    url(r'^product-dispatcher$', product.product_dispatcher, name="lfs_manage_product_dispatcher"),
    url(r'^product-by-id/(?P<product_id>\d*)$', product.product_by_id, name="lfs_manage_product_by_id"),
    url(r'^product/(?P<product_id>\d*)$', product.manage_product, name="lfs_manage_product"),
    url(r'^product-data-form/(?P<product_id>\d*)$', product.product_data_form),
    url(r'^add-product$', product.add_product, name="lfs_manage_add_product"),
    url(r'^edit-product-data/(?P<product_id>\d*)$', product.edit_product_data, name="lfs_manage_edit_product_data"),
    url(r'^delete-product/(?P<product_id>\d*)$', product.delete_product, name="lfs_manage_delete_product"),
    url(r'^selectable-products-inline$', product.selectable_products_inline, name="lfs_manage_selectable_products_inline"),
    url(r'^save-product-stock/(?P<product_id>\d*)$', product.stock, name="lfs_save_product_stock"),
    url(r'^change-product-subtype/(?P<product_id>\d*)$', product.change_subtype, name="lfs_change_product_subtype"),
    url(r'^products$', product.products, name="lfs_manage_products"),
    url(r'^products-inline$', product.products_inline, name="lfs_products_inline"),
    url(r'^save-products$', product.save_products, name="lfs_manage_save_products"),
    url(r'^set-product-filters$', product.set_filters, name="lfs_set_product_filters"),
    url(r'^set-product-name-filter$', product.set_name_filter, name="lfs_set_product_name_filter"),
    url(r'^reset-product-filters$', product.reset_filters, name="lfs_reset_product_filters"),
    url(r'^set-products-page$', product.set_products_page, name="lfs_set_products_page"),
    url(r'^no-products$', product.no_products, name="lfs_manage_no_products"),

    url(r'^product-categories-tab/(?P<product_id>\d*)$', lfs.manage.product.categories.manage_categories, name="lfs_product_categories_tab"),
    url(r'^product-accessories-tab/(?P<product_id>\d*)$', lfs.manage.product.accessories.load_tab, name="lfs_manage_product_accessories_tab"),
    url(r'^product-relateds-tab/(?P<product_id>\d*)$', lfs.manage.product.related_products.load_tab, name="lfs_manage_product_related_products_tab"),
    url(r'^product-variants-tab/(?P<product_id>\d*)$', lfs.manage.product.variants.manage_variants, name="lfs_manage_product_variants_tab"),

    url(r'^change-product-categories/(?P<product_id>\d*)$', lfs.manage.product.categories.change_categories, name="lfs_manage_product_categories"),

    # Product Images
    url(r'^add-image/(?P<product_id>\d*)$', lfs.manage.product.images.add_image, name="lfs_manage_add_image"),
    url(r'^update-images/(?P<product_id>\d*)$', lfs.manage.product.images.update_images, name="lfs_manage_update_images"),
    url(r'^product-images/(?P<product_id>\d*)$', lfs.manage.product.images.list_images, name="lfs_manage_images"),
    url(r'^update-active-images/(?P<product_id>\d*)$', lfs.manage.product.images.update_active_images, name="lfs_manage_update_active_images"),
    url(r'^move-image/(?P<id>\d+)$', lfs.manage.product.images.move_image, name="lfs_move_image"),

    # Product Attachments
    url(r'^add-attachment/(?P<product_id>\d*)$', lfs.manage.product.attachments.add_attachment, name="lfs_manage_add_attachment"),
    url(r'^update-attachments/(?P<product_id>\d*)$', lfs.manage.product.attachments.update_attachments, name="lfs_manage_update_attachments"),
    url(r'^product-attachments/(?P<product_id>\d*)$', lfs.manage.product.attachments.list_attachments, name="lfs_manage_attachments"),
    url(r'^move-product-attachments/(?P<id>\d+)$', lfs.manage.product.attachments.move_attachment, name="lfs_move_product_attachment"),

    # Product variants
    url(r'^properties/(?P<product_id>\d*)$', lfs.manage.product.variants.manage_variants, name="lfs_manage_variants"),
    url(r'^add-property/(?P<product_id>\d*)$', lfs.manage.product.variants.add_property, name="lfs_manage_add_property"),
    url(r'^add-property-option/(?P<product_id>\d*)$', lfs.manage.product.variants.add_property_option, name="lfs_manage_add_property_option"),
    url(r'^delete-property/(?P<product_id>\d*)/(?P<property_id>\d*)$', lfs.manage.product.variants.delete_property, name="lfs_manage_delete_property"),
    url(r'^delete-property-option/(?P<product_id>\d*)/(?P<option_id>\d*)$', lfs.manage.product.variants.delete_property_option, name="lfs_manage_delete_property_option"),
    url(r'^change-property-position$', lfs.manage.product.variants.change_property_position, name="lfs_manage_change_property_position"),
    url(r'^update-variants/(?P<product_id>\d*)$', lfs.manage.product.variants.update_variants, name="lfs_manage_update_variants"),
    url(r'^add-variants/(?P<product_id>\d*)$', lfs.manage.product.variants.add_variants, name="lfs_manage_add_variants"),
    url(r'^edit-sub-type/(?P<product_id>\d*)$', lfs.manage.product.variants.edit_sub_type, name="lfs_manage_edit_sub_type"),
    url(r'^update-category-variant/(?P<product_id>\d*)$', lfs.manage.product.variants.update_category_variant, name="lfs_update_category_variant"),

    # Global Images
    url(r'^imagebrowser$', lfs.manage.images.views.imagebrowser, name="lfs_manage_imagebrowser"),
    url(r'^global-images$', lfs.manage.images.views.images, name="lfs_manage_global_images"),
    url(r'^global-images-list$', lfs.manage.images.views.images_list, name="lfs_manage_global_images_list"),
    url(r'^delete-global-images$', lfs.manage.images.views.delete_images, name="lfs_manage_delete_images"),
    url(r'^add-global-images$', lfs.manage.images.views.add_images, name="lfs_manage_add_global_image"),

    # Property Groups
    url(r'^property-groups', lfs.manage.property_groups.views.manage_property_groups, name="lfs_manage_property_groups"),
    url(r'^property-group/(?P<id>\d*)', lfs.manage.property_groups.views.manage_property_group, name="lfs_manage_property_group"),
    url(r'^add-property-group', lfs.manage.property_groups.views.add_property_group, name="lfs_manage_add_property_group"),
    url(r'^delete-property-group/(?P<id>\d*)', lfs.manage.property_groups.views.delete_property_group, name="lfs_delete_property_group"),
    url(r'^assign-properties/(?P<group_id>\d*)', lfs.manage.property_groups.views.assign_properties, name="lfs_assign_properties"),
    url(r'^update-properties/(?P<group_id>\d*)', lfs.manage.property_groups.views.update_properties, name="lfs_update_properties"),
    url(r'^no-property-groups$', lfs.manage.property_groups.views.no_property_groups, name="lfs_manage_no_property_groups"),
    url(r'^sort-property-groups$', lfs.manage.property_groups.views.sort_property_groups, name="lfs_manage_sort_property_groups"),

    # Property Groups / Products
    url(r'^assign-products-to-property-group/(?P<group_id>\d*)', lfs.manage.property_groups.views.assign_products, name="lfs_assign_products_to_property_group"),
    url(r'^remove-products-from-property-group/(?P<group_id>\d*)', lfs.manage.property_groups.views.remove_products, name="lfs_pg_remove_products"),
    url(r'^pg-products-inline/(?P<product_group_id>\d*)', lfs.manage.property_groups.views.products_inline, name="lfs_pg_products_inline"),

    # Shop Properties
    url(r'^shop-properties$', lfs.manage.property.views.manage_properties, name="lfs_manage_shop_properties"),
    url(r'^shop-property/(?P<id>\d*)', lfs.manage.property.views.manage_property, name="lfs_manage_shop_property"),
    url(r'^update-shop-property-type/(?P<id>\d*)', lfs.manage.property.views.update_property_type, name="lfs_update_shop_property_type"),
    url(r'^add-shop-property$', lfs.manage.property.views.add_property, name="lfs_add_shop_property"),
    url(r'^delete-shop-property/(?P<id>\d*)', lfs.manage.property.views.delete_property, name="lfs_delete_shop_property"),
    url(r'^add-shop-property-option/(?P<property_id>\d*)', lfs.manage.property.views.add_option, name="lfs_add_shop_property_option"),
    url(r'^add-shop-property-step/(?P<property_id>\d*)', lfs.manage.property.views.add_step, name="lfs_add_shop_property_step"),
    url(r'^save-shop-property-step/(?P<property_id>\d*)', lfs.manage.property.views.save_step_range, name="lfs_save_shop_property_step_range"),
    url(r'^save-shop-property-step-type/(?P<property_id>\d*)', lfs.manage.property.views.save_step_type, name="lfs_save_shop_property_step_type"),
    url(r'^delete-shop-property-option/(?P<id>\d*)', lfs.manage.property.views.delete_option, name="lfs_delete_shop_property_option"),
    url(r'^delete-shop-property-step/(?P<id>\d*)', lfs.manage.property.views.delete_step, name="lfs_delete_shop_property_step"),
    url(r'^save-number-field-validators/(?P<property_id>\d*)', lfs.manage.property.views.save_number_field_validators, name="lfs_save_number_field_validators"),
    url(r'^save-select-field/(?P<property_id>\d*)', lfs.manage.property.views.save_select_field, name="lfs_save_select_field"),
    url(r'^no-properties$', lfs.manage.property.views.no_properties, name="lfs_manage_no_shop_properties"),
    url(r'^set-property-name-filter$', lfs.manage.property.views.set_name_filter, name="lfs_set_property_name_filter"),
    url(r'^set-property-page$', lfs.manage.property.views.set_properties_page, name="lfs_set_properties_page"),

    # Product properties
    url(r'^update-product-properties/(?P<product_id>\d*)$', lfs.manage.product.properties.update_properties, name="lfs_update_product_properties"),
    url(r'^update-product-property-groups/(?P<product_id>\d*)$', lfs.manage.product.properties.update_property_groups, name="lfs_update_product_property_groups"),

    # Accesories
    url(r'^accessories/(?P<product_id>\d*)$', lfs.manage.product.accessories.manage_accessories, name="lfs_manage_accessories"),
    url(r'^accessories-inline/(?P<product_id>\d*)$', lfs.manage.product.accessories.manage_accessories_inline, name="lfs_manage_accessories_inline"),
    url(r'^add-accessories/(?P<product_id>\d*)$', lfs.manage.product.accessories.add_accessories, name="lfs_manage_add_accessories"),
    url(r'^remove-accessories/(?P<product_id>\d*)$', lfs.manage.product.accessories.remove_accessories, name="lfs_manage_remove_accessories"),
    url(r'^update-accessories/(?P<product_id>\d*)$', lfs.manage.product.accessories.update_accessories, name="lfs_manage_update_accessories"),

    # Related Products
    url(r'^related-products/(?P<product_id>\d*)$', lfs.manage.product.related_products.manage_related_products, name="lfs_manage_related_products"),
    url(r'^related-products-inline/(?P<product_id>\d*)$', lfs.manage.product.related_products.manage_related_products_inline, name="lfs_manage_related_products_inline"),
    url(r'^add-related-products/(?P<product_id>\d*)$', lfs.manage.product.related_products.add_related_products, name="lfs_manage_add_related_products"),
    url(r'^remove-related-products/(?P<product_id>\d*)$', lfs.manage.product.related_products.remove_related_products, name="lfs_manage_remove_related_products"),
    url(r'^manage-related-products/(?P<product_id>\d*)$', lfs.manage.product.related_products.update_related_products, name="lfs_manage_update_related_products"),

    # Carts
    url(r'^carts$', lfs.manage.views.carts.carts_view, name="lfs_manage_carts"),
    url(r'^carts-inline$', lfs.manage.views.carts.carts_inline, name="lfs_carts_inline"),
    url(r'^cart-inline/(?P<cart_id>\d*)$', lfs.manage.views.carts.cart_inline, name="lfs_cart_inline"),
    url(r'^cart/(?P<cart_id>\d*)$', lfs.manage.views.carts.cart_view, name="lfs_manage_cart"),
    url(r'^selectable-carts-inline$', lfs.manage.views.carts.selectable_carts_inline, name="lfs_selectable_carts_inline"),
    url(r'^set-cart-filters$', lfs.manage.views.carts.set_cart_filters, name="lfs_set_cart_filters"),
    url(r'^set-cart-filters-date$', lfs.manage.views.carts.set_cart_filters_date, name="lfs_set_cart_filters_date"),
    url(r'^reset-cart-filters$', lfs.manage.views.carts.reset_cart_filters, name="lfs_reset_cart_filters"),
    url(r'^set-carts-page$', lfs.manage.views.carts.set_carts_page, name="lfs_set_carts_page"),
    url(r'^set-cart-page$', lfs.manage.views.carts.set_cart_page, name="lfs_set_cart_page"),

    # Categories
    url(r'^categories$', lfs.manage.categories.category.manage_categories, name="lfs_manage_categories"),
    url(r'^category/(?P<category_id>\d*)$', lfs.manage.categories.category.manage_category, name="lfs_manage_category"),
    url(r'^category-by-id/(?P<category_id>\d*)$', lfs.manage.categories.category.category_by_id, name="lfs_category_by_id"),
    url(r'^add-products/(?P<category_id>\d*)$', lfs.manage.categories.products.add_products, name="lfs_manage_category_add_products"),
    url(r'^remove-products/(?P<category_id>\d*)$', lfs.manage.categories.products.remove_products, name="lfs_manage_category_remove_products"),
    url(r'^add-top-category$', lfs.manage.categories.category.add_category, name="lfs_manage_add_top_category"),
    url(r'^add-category/(?P<category_id>\d*)$', lfs.manage.categories.category.add_category, name="lfs_manage_add_category"),
    url(r'^delete-category/(?P<id>[-\w]*)$', lfs.manage.categories.category.delete_category, name="lfs_delete_category"),
    url(r'^products-inline/(?P<category_id>\d*)$', lfs.manage.categories.products.products_inline, name="lfs_manage_category_products_inline"),
    url(r'^edit-category-data/(?P<category_id>\d*)$', lfs.manage.categories.category.edit_category_data, name="lfs_manage_category_edit_data"),
    url(r'^edit-category-view/(?P<category_id>\d*)$', lfs.manage.categories.category.category_view, name="lfs_manage_category_view"),
    url(r'^selected-products/(?P<category_id>\d*)$', lfs.manage.categories.products.selected_products, name="lfs_selected_products"),
    url(r'^load-products-tab/(?P<category_id>\d*)$', lfs.manage.categories.products.products_tab, name="lfs_load_products_tab"),
    url(r'^sort-categories$', lfs.manage.categories.category.sort_categories, name="lfs_sort_categories"),
    url(r'^no-categories$', lfs.manage.categories.view.no_categories, name="lfs_manage_no_categories"),

    # Customers
    url(r'^customers$', lfs.manage.views.customer.customers, name="lfs_manage_customers"),
    url(r'^customers-inline$', lfs.manage.views.customer.customers_inline, name="lfs_customers_inline"),
    url(r'^customer/(?P<customer_id>\d*)$', lfs.manage.views.customer.customer, name="lfs_manage_customer"),
    url(r'^customer-inline/(?P<customer_id>\d*)$', lfs.manage.views.customer.customer_inline, name="lfs_customer_inline"),
    url(r'^set-customer-filters$', lfs.manage.views.customer.set_customer_filters, name="lfs_set_customer_filters"),
    url(r'^reset-customer-filters$', lfs.manage.views.customer.reset_customer_filters, name="lfs_reset_customer_filters"),
    url(r'^set-customer-ordering/(?P<ordering>\w*)$', lfs.manage.views.customer.set_ordering, name="lfs_set_customer_ordering"),
    url(r'^selectable-customers-inline$', lfs.manage.views.customer.selectable_customers_inline, name="lfs_selectable_customers_inline"),
    url(r'^set-selectable-customers-page$', lfs.manage.views.customer.set_selectable_customers_page, name="lfs_set_selectable_customers_page"),
    url(r'^set-customers-page$', lfs.manage.views.customer.set_customers_page, name="lfs_set_customers_page"),

    # export
    url(r'^export-dispatcher$', lfs.manage.views.export.export_dispatcher, name="lfs_export_dispatcher"),
    url(r'^export/(?P<export_id>\d*)$', lfs.manage.views.export.manage_export, name="lfs_export"),
    url(r'^export-inline/(?P<export_id>\d*)/(?P<category_id>\d*)$', lfs.manage.views.export.export_inline, name="lfs_export_inline"),
    url(r'^edit-category/(?P<export_id>\d*)/(?P<category_id>\d*)$', lfs.manage.views.export.edit_category, name="lfs_export_edit_category"),
    url(r'^edit-product/(?P<export_id>\d*)/(?P<product_id>\d*)$', lfs.manage.views.export.edit_product, name="lfs_export_edit_product"),
    url(r'^category-state/(?P<export_id>\d*)/(?P<category_id>\d*)$', lfs.manage.views.export.category_state, name="lfs_export_category_state"),
    url(r'^update-export-data/(?P<export_id>\d*)$', lfs.manage.views.export.update_data, name="lfs_export_update_export_data"),
    url(r'^add-export$', lfs.manage.views.export.add_export, name="lfs_export_add_export"),
    url(r'^delete-export/(?P<export_id>\d*)$', lfs.manage.views.export.delete_export, name="lfs_export_delete_export"),
    url(r'^export-export/(?P<slug>[-\w]*)$', lfs.manage.views.export.export, name="lfs_export_export"),
    url(r'^update-category-variants-option/(?P<export_id>\d*)/(?P<category_id>\d*)$', lfs.manage.views.export.update_category_variants_option, name="lfs_export_update_category_variants_option"),

    # Shipping Methods
    url(r'^shipping$', lfs.manage.shipping_methods.views.manage_shipping, name="lfs_manage_shipping"),
    url(r'^shipping-method/(?P<shipping_method_id>\d*)$', lfs.manage.shipping_methods.views.manage_shipping_method, name="lfs_manage_shipping_method"),
    url(r'^add-shipping-method', lfs.manage.shipping_methods.views.add_shipping_method, name="lfs_manage_add_shipping_method"),
    url(r'^save-shipping-data/(?P<shipping_method_id>\d*)$', lfs.manage.shipping_methods.views.save_shipping_method_data, name="lfs_manage_save_shipping_method_data"),
    url(r'^delete-shipping-method/(?P<shipping_method_id>\d*)$', lfs.manage.shipping_methods.views.delete_shipping_method, name="lfs_manage_delete_shipping_method"),
    url(r'^add-shipping-price/(?P<shipping_method_id>\d*)$', lfs.manage.shipping_methods.views.add_shipping_price, name="lfs_manage_add_shipping_price"),
    url(r'^update-shipping-prices/(?P<shipping_method_id>\d*)$', lfs.manage.shipping_methods.views.update_shipping_prices, name="lfs_manage_update_shipping_prices"),
    url(r'^shipping-price-criteria/(?P<shipping_price_id>\d*)$', lfs.manage.shipping_methods.views.shipping_price_criteria, name="lfs_manage_shipping_price_criteria"),
    url(r'^save-shipping-price-criteria/(?P<shipping_price_id>\d*)$', lfs.manage.shipping_methods.views.save_shipping_price_criteria, name="lfs_manage_save_shipping_price_criteria"),
    url(r'^save-shipping-method-criteria/(?P<shipping_method_id>\d*)$', lfs.manage.shipping_methods.views.save_shipping_method_criteria, name="lfs_manage_save_shipping_method_criteria"),
    url(r'^sort-shipping-methods$', lfs.manage.shipping_methods.views.sort_shipping_methods, name="lfs_sort_shipping_methods"),
    url(r'^no-shipping-methods$', lfs.manage.shipping_methods.views.no_shipping_methods, name="lfs_manage_no_shipping_methods"),

    # Discounts
    url(r'^discounts$', lfs.manage.discounts.views.manage_discounts, name="lfs_manage_discounts"),
    url(r'^discount/(?P<id>\d*)$', lfs.manage.discounts.views.manage_discount, name="lfs_manage_discount"),
    url(r'^add-discount', lfs.manage.discounts.views.add_discount, name="lfs_manage_add_discount"),
    url(r'^save-discount-data/(?P<id>\d*)$', lfs.manage.discounts.views.save_discount_data, name="lfs_manage_save_discount_data"),
    url(r'^delete-discount/(?P<id>\d*)$', lfs.manage.discounts.views.delete_discount, name="lfs_manage_delete_discount"),
    url(r'^save-discount-criteria/(?P<id>\d*)$', lfs.manage.discounts.views.save_discount_criteria, name="lfs_manage_save_discount_criteria"),
    url(r'^no-discounts$', lfs.manage.discounts.views.no_discounts, name="lfs_manage_no_discounts"),

    # Discounts / Products
    url(r'^assign-products-to-discount/(?P<discount_id>\d*)', lfs.manage.discounts.views.assign_products, name="lfs_assign_products_to_discount"),
    url(r'^remove-products-from-discount/(?P<discount_id>\d*)', lfs.manage.discounts.views.remove_products, name="lfs_discount_remove_products"),
    url(r'^discount-products-inline/(?P<discount_id>\d*)', lfs.manage.discounts.views.products_inline, name="lfs_discount_products_inline"),

    # Pages
    url(r'^add-page$', lfs.manage.pages.views.add_page, name="lfs_add_page"),
    url(r'^delete-page/(?P<id>\d*)$', lfs.manage.pages.views.delete_page, name="lfs_delete_page"),
    url(r'^manage-pages$', lfs.manage.pages.views.manage_pages, name="lfs_manage_pages"),
    url(r'^manage-page/(?P<id>\d*)$', lfs.manage.pages.views.manage_page, name="lfs_manage_page"),
    url(r'^page-by-id/(?P<id>\d*)$', lfs.manage.pages.views.page_view_by_id, name="lfs_page_view_by_id"),
    url(r'^sort-pages$', lfs.manage.pages.views.sort_pages, name="lfs_sort_pages"),
    url(r'^save-page-data-tab/(?P<id>\d*)$', lfs.manage.pages.views.save_data_tab, name="lfs_save_page_data_tab"),

    # Payment
    url(r'^payment$', lfs.manage.views.payment.manage_payment, name="lfs_manage_payment"),
    url(r'^payment-method/(?P<payment_method_id>\d*)$', lfs.manage.views.payment.manage_payment_method, name="lfs_manage_payment_method"),
    url(r'^add-payment-method', lfs.manage.views.payment.add_payment_method, name="lfs_add_payment_method"),
    url(r'^save-payment-data/(?P<payment_method_id>\d*)$', lfs.manage.views.payment.save_payment_method_data, name="lfs_manage_save_payment_method_data"),
    url(r'^delete-payment-method/(?P<payment_method_id>\d*)$', lfs.manage.views.payment.delete_payment_method, name="lfs_delete_payment_method"),
    url(r'^add-payment-price/(?P<payment_method_id>\d*)$', lfs.manage.views.payment.add_payment_price, name="lfs_manage_add_payment_price"),
    url(r'^update-payment-prices/(?P<payment_method_id>\d*)$', lfs.manage.views.payment.update_payment_prices, name="lfs_manage_update_payment_prices"),
    url(r'^payment-price-criteria/(?P<payment_price_id>\d*)$', lfs.manage.views.payment.payment_price_criteria, name="lfs_manage_payment_price_criteria"),
    url(r'^save-payment-price-criteria/(?P<payment_price_id>\d*)$', lfs.manage.views.payment.save_payment_price_criteria, name="lfs_manage_save_payment_price_criteria"),
    url(r'^save-payment-method-criteria/(?P<payment_method_id>\d*)$', lfs.manage.views.payment.save_payment_method_criteria, name="lfs_manage_save_payment_method_criteria"),
    url(r'^sort-payment-methods$', lfs.manage.views.payment.sort_payment_methods, name="lfs_sort_payment_methods"),

    # Orders
    url(r'^manage-orders$', lfs.manage.views.orders.manage_orders, name="lfs_manage_orders"),
    url(r'^orders$', lfs.manage.views.orders.orders_view, name="lfs_orders"),
    url(r'^orders-inline$', lfs.manage.views.orders.orders_inline, name="lfs_orders_inline"),
    url(r'^order/(?P<order_id>\d*)$', lfs.manage.views.orders.order_view, name="lfs_manage_order"),
    url(r'^delete-order/(?P<order_id>\d*)$', lfs.manage.views.orders.delete_order, name="lfs_delete_order"),
    url(r'^send-order/(?P<order_id>\d*)$', lfs.manage.views.orders.send_order, name="lfs_send_order"),
    url(r'^set-orders-filter$', lfs.manage.views.orders.set_order_filters, name="lfs_set_order_filter"),
    url(r'^set-orders-filter-date$', lfs.manage.views.orders.set_order_filters_date, name="lfs_set_order_filters_date"),
    url(r'^reset-order-filter$', lfs.manage.views.orders.reset_order_filters, name="lfs_reset_order_filters"),
    url(r'^set-selectable-orders-page$', lfs.manage.views.orders.set_selectable_orders_page, name="lfs_set_selectable_orders_page"),
    url(r'^set-orders-page$', lfs.manage.views.orders.set_orders_page, name="lfs_set_orders_page"),
    url(r'^change-order-state$', lfs.manage.views.orders.change_order_state, name="lfs_change_order_state"),

    # Order numbers
    url(r'^save-order-numbers-tab$', lfs.manage.views.shop.save_order_numbers_tab, name="lfs_save_order_numbers_tab"),

    # Criteria
    url(r'^add-criterion', lfs.manage.views.criteria.add_criterion, name="lfs_add_criterion"),
    url(r'^change-criterion', lfs.manage.views.criteria.change_criterion_form, name="lfs_manage_criteria_change_criterion_form"),

    # Static blocks
    url(r'^add-static-block$', lfs.manage.static_blocks.views.add_static_block, name="lfs_manage_add_static_block"),
    url(r'^delete-static-block/(?P<id>\d*)$', lfs.manage.static_blocks.views.delete_static_block, name="lfs_delete_static_block"),
    url(r'^preview-static-block/(?P<id>\d*)$', lfs.manage.static_blocks.views.preview_static_block, name="lfs_preview_static_block"),
    url(r'^static-blocks$', lfs.manage.static_blocks.views.manage_static_blocks, name="lfs_manage_static_blocks"),
    url(r'^static-block/(?P<id>\d*)$', lfs.manage.static_blocks.views.manage_static_block, name="lfs_manage_static_block"),
    url(r'^add_files/(?P<id>[-\w]*)', lfs.manage.static_blocks.views.add_files, name="lfs_add_files_to_static_block"),
    url(r'^update_files/(?P<id>[-\w]*)', lfs.manage.static_blocks.views.update_files, name="lfs_manage_update_files_sb"),
    url(r'^reload_files/(?P<id>[-\w]*)', lfs.manage.static_blocks.views.reload_files, name="lfs_reload_files"),
    url(r'^sort-static-blocks$', lfs.manage.static_blocks.views.sort_static_blocks, name="lfs_sort_static_blocks"),
    url(r'^no-static-blocks$', lfs.manage.static_blocks.views.no_static_blocks, name="lfs_manage_no_static_blocks"),

    # Reviews
    url(r'^reviews$', lfs.manage.views.review.reviews, name="lfs_manage_reviews"),
    url(r'^review/(?P<review_id>\d*)$', lfs.manage.views.review.review, name="lfs_manage_review"),
    url(r'^set-review-filters$', lfs.manage.views.review.set_review_filters, name="lfs_set_review_filters"),
    url(r'^reset-review-filters$', lfs.manage.views.review.reset_review_filters, name="lfs_reset_review_filters"),
    url(r'^set-review-ordering/(?P<ordering>\w*)$', lfs.manage.views.review.set_ordering, name="lfs_set_review_ordering"),
    url(r'^set-review-state/(?P<review_id>\d*)$', lfs.manage.views.review.set_review_state, name="lfs_set_review_state"),
    url(r'^delete-review/(?P<review_id>\d*)$', lfs.manage.views.review.delete_review, name="lfs_delete_review"),
    url(r'^set-reviews-page$', lfs.manage.views.review.set_reviews_page, name="lfs_set_reviews_page"),
    url(r'^set-selectable-reviews-page$', lfs.manage.views.review.set_selectable_reviews_page, name="lfs_set_selectable_reviews_page"),

    # Shop
    url(r'^shop$', lfs.manage.views.shop.manage_shop, name="lfs_manage_shop"),
    url(r'^save-shop-data-tab$', lfs.manage.views.shop.save_data_tab, name="lfs_save_shop_data_tab"),
    url(r'^save-shop-default-values-tab$', lfs.manage.views.shop.save_default_values_tab, name="lfs_save_shop_default_values_tab"),

    # Actions
    url(r'^actions$', lfs.manage.actions.views.manage_actions, name="lfs_manage_actions"),
    url(r'^action/(?P<id>\d*)$', lfs.manage.actions.views.manage_action, name="lfs_manage_action"),
    url(r'^no-actions$', lfs.manage.actions.views.no_actions, name="lfs_no_actions"),
    url(r'^add-action$', lfs.manage.actions.views.add_action, name="lfs_add_action"),
    url(r'^delete-action/(?P<id>\d*)$', lfs.manage.actions.views.delete_action, name="lfs_delete_action"),
    url(r'^save-action/(?P<id>\d*)$', lfs.manage.actions.views.save_action, name="lfs_save_action"),
    url(r'^sort-actions$', lfs.manage.actions.views.sort_actions, name="lfs_sort_actions"),

    # Product Taxes
    url(r'^add-product-tax$', lfs.manage.product_taxes.views.add_tax, name="lfs_manage_add_tax"),
    url(r'^delete-product-tax/(?P<id>\d*)$', lfs.manage.product_taxes.views.delete_tax, name="lfs_delete_tax"),
    url(r'^product-taxes$', lfs.manage.product_taxes.views.manage_taxes, name="lfs_manage_taxes"),
    url(r'^product-tax/(?P<id>\d*)$', lfs.manage.product_taxes.views.manage_tax, name="lfs_manage_tax"),
    url(r'^no-product-taxes$', lfs.manage.product_taxes.views.no_taxes, name="lfs_manage_no_taxes"),

    # Customer tax
    url(r'^add-customer-tax$', lfs.manage.customer_tax.views.add_customer_tax, name="lfs_add_customer_tax"),
    url(r'^delete-customer-tax/(?P<id>\d*)$', lfs.manage.customer_tax.views.delete_customer_tax, name="lfs_delete_customer_tax"),
    url(r'^customer-taxes$', lfs.manage.customer_tax.views.manage_customer_taxes, name="lfs_manage_customer_taxes"),
    url(r'^customer-tax/(?P<id>\d*)$', lfs.manage.customer_tax.views.manage_customer_tax, name="lfs_manage_customer_tax"),
    url(r'^no-customer-taxes$', lfs.manage.customer_tax.views.no_customer_taxes, name="lfs_manage_no_customer_taxes"),
    url(r'^save-customer-tax-criteria/(?P<id>\d*)$', lfs.manage.customer_tax.views.save_criteria, name="lfs_manage_save_customer_tax_criteria"),
    url(r'^save-customer-tax-data/(?P<id>\d*)$', lfs.manage.customer_tax.views.save_data, name="lfs_manage_save_customer_tax_data"),

    # Utils
    url(r'^utilities$', lfs.manage.views.utils.utilities, name="lfs_manage_utils"),
    url(r'^clear-cache$', lfs.manage.views.utils.clear_cache, name="lfs_clear_cache"),
    url(r'^set-category-levels$', lfs.manage.views.utils.set_category_levels, name="lfs_set_category_levels"),
    url(r'^update-effective-price$', lfs.manage.views.utils.update_effective_price, name="lfs_update_effective_price"),
    url(r'^reindex-topseller$', lfs.manage.views.utils.reindex_topseller, name="lfs_reindex_topseller"),

    # Information
    url(r'^environment$', lfs.manage.information.views.environment, name="lfs_manage_environment"),
]

# Manufacturer / SEO
urlpatterns += SEOView.get_seo_urlpattern(Manufacturer)
urlpatterns += ShopSEOView.get_seo_urlpattern(Shop)
urlpatterns += PageSEOView.get_seo_urlpattern(Page)
urlpatterns += SEOView.get_seo_urlpattern(Product, form_klass=ProductSEOForm, template_name='manage/product/seo.html')
urlpatterns += SEOView.get_seo_urlpattern(Category)
