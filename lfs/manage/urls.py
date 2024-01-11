from django.urls import re_path
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
    re_path(r"^$", lfs.manage.views.dashboard.dashboard, name="lfs_manage_dashboard"),
    # Delivery Times
    re_path(r"^delivery_times$", delivery_times_views.manage_delivery_times, name="lfs_manage_delivery_times"),
    re_path(r"^delivery_time/(?P<id>\d*)$", delivery_times_views.manage_delivery_time, name="lfs_manage_delivery_time"),
    re_path(r"^add-delivery-time$", delivery_times_views.add_delivery_time, name="lfs_manage_add_delivery_time"),
    re_path(
        r"^delete-delivery-time/(?P<id>\d*)$",
        delivery_times_views.delete_delivery_time,
        name="lfs_delete_delivery_time",
    ),
    re_path(r"^no-times$", delivery_times_views.no_delivery_times, name="lfs_no_delivery_times"),
    # Manufacturer
    re_path(
        r"^manufacturer-dispatcher$", manufacturers_views.manufacturer_dispatcher, name="lfs_manufacturer_dispatcher"
    ),
    re_path(
        r"^manufacturer/(?P<manufacturer_id>\d*)$",
        manufacturers_views.manage_manufacturer,
        name="lfs_manage_manufacturer",
    ),
    re_path(
        r"^update-manufacturer-data/(?P<manufacturer_id>\d*)$",
        manufacturers_views.update_data,
        name="lfs_manufacturer_update_manufacturer_data",
    ),
    re_path(r"^add-manufacturer$", manufacturers_views.add_manufacturer, name="lfs_manufacturer_add_manufacturer"),
    re_path(
        r"^delete-manufacturer/(?P<manufacturer_id>\d*)$",
        manufacturers_views.delete_manufacturer,
        name="lfs_manufacturer_delete_manufacturer",
    ),
    re_path(
        r"^edit-category-manufacturer/(?P<manufacturer_id>\d*)/(?P<category_id>\d*)$",
        manufacturers_views.edit_category,
        name="lfs_manufacturer_edit_category",
    ),
    re_path(
        r"^edit-product-manufacturer/(?P<manufacturer_id>\d*)/(?P<product_id>\d*)$",
        manufacturers_views.edit_product,
        name="lfs_manufacturer_edit_product",
    ),
    re_path(
        r"^category-state-manufacturer/(?P<manufacturer_id>\d*)/(?P<category_id>\d*)$",
        manufacturers_views.category_state,
        name="lfs_manufacturer_category_state",
    ),
    re_path(
        r"^manufacturer-inline/(?P<manufacturer_id>\d*)/(?P<category_id>\d*)$",
        manufacturers_views.manufacturer_inline,
        name="lfs_manufacturer_inline",
    ),
    re_path(r"^manufacturers-ajax/$", manufacturers_views.manufacturers_ajax, name="lfs_manufacturers_ajax"),
    re_path(r"^no-manufacturers$", manufacturers_views.no_manufacturers, name="lfs_manage_no_manufacturers"),
    re_path(
        r"^edit-manufacturer-view/(?P<manufacturer_id>\d*)$",
        manufacturers_views.manufacturer_view,
        name="lfs_manage_manufacturer_view",
    ),
    re_path(
        r"^manufacturer-products-inline/(?P<manufacturer_id>\d*)$",
        manufacturers_products_views.products_inline,
        name="lfs_manage_manufacturer_products_inline",
    ),
    re_path(
        r"^manufacturer-selected-products/(?P<manufacturer_id>\d*)$",
        manufacturers_products_views.selected_products,
        name="lfs_manage_manufacturer_selected_products",
    ),
    re_path(
        r"^manufacturer-add-products/(?P<manufacturer_id>\d*)$",
        manufacturers_products_views.add_products,
        name="lfs_manage_manufacturer_add_products",
    ),
    re_path(
        r"^manufacturer-remove-products/(?P<manufacturer_id>\d*)$",
        manufacturers_products_views.remove_products,
        name="lfs_manage_manufacturer_remove_products",
    ),
    re_path(
        r"^manufacturer-load-products-tab/(?P<manufacturer_id>\d*)$",
        manufacturers_products_views.products_tab,
        name="lfs_manufacturer_load_products_tab",
    ),
    # Marketing
    re_path(r"^featured$", lfs.manage.views.marketing.marketing.manage_featured_page, name="lfs_manage_featured"),
    re_path(r"^marketing$", lfs.manage.views.marketing.marketing.manage_marketing, name="lfs_manage_marketing"),
    re_path(r"^add-featured$", lfs.manage.views.marketing.featured.add_featured, name="lfs_manage_add_featured"),
    re_path(
        r"^update-featured$", lfs.manage.views.marketing.featured.update_featured, name="lfs_manage_update_featured"
    ),
    re_path(
        r"^featured-inline$",
        lfs.manage.views.marketing.featured.manage_featured_inline,
        name="lfs_manage_featured_inline",
    ),
    re_path(
        r"^manage-rating-mails$",
        lfs.manage.views.marketing.rating_mails.manage_rating_mails,
        name="lfs_manage_rating_mails",
    ),
    re_path(
        r"^send-rating-mails$", lfs.manage.views.marketing.rating_mails.send_rating_mails, name="lfs_send_rating_mails"
    ),
    re_path(r"^add-topseller$", lfs.manage.views.marketing.topseller.add_topseller, name="lfs_manage_add_topseller"),
    re_path(
        r"^update-topseller$", lfs.manage.views.marketing.topseller.update_topseller, name="lfs_manage_update_topseller"
    ),
    re_path(
        r"^topseller-inline$",
        lfs.manage.views.marketing.topseller.manage_topseller_inline,
        name="lfs_manage_topseller_inline",
    ),
    # Voucher
    re_path(r"^vouchers$", voucher_views.manage_vouchers, name="lfs_manage_vouchers"),
    re_path(r"^no-vouchers$", voucher_views.no_vouchers, name="lfs_no_vouchers"),
    re_path(r"^add-voucher-group$", voucher_views.add_voucher_group, name="lfs_manage_add_voucher_group"),
    re_path(r"^voucher-group/(?P<id>\d+)$", voucher_views.voucher_group, name="lfs_manage_voucher_group"),
    re_path(r"^delete-voucher-group/(?P<id>\d+)$", voucher_views.delete_voucher_group, name="lfs_delete_voucher_group"),
    re_path(
        r"^save-voucher-group-data/(?P<id>\d+)$",
        voucher_views.save_voucher_group_data,
        name="lfs_manage_save_voucher_group_data",
    ),
    re_path(r"^save-voucher-options$", voucher_views.save_voucher_options, name="lfs_manage_save_voucher_options"),
    re_path(r"^add-vouchers/(?P<group_id>\d+)$", voucher_views.add_vouchers, name="lfs_manage_add_vouchers"),
    re_path(r"^delete-vouchers/(?P<group_id>\d+)$", voucher_views.delete_vouchers, name="lfs_manage_delete_vouchers"),
    re_path(r"^set-vouchers-page$", voucher_views.set_vouchers_page, name="lfs_set_vouchers_page"),
    # Portlets
    re_path(
        r"^add-portlet/(?P<object_type_id>\d+)/(?P<object_id>\d+)$", lfs_portlets.add_portlet, name="lfs_add_portlet"
    ),
    re_path(
        r"^update-portlets/(?P<object_type_id>\d+)/(?P<object_id>\d+)$",
        lfs_portlets.update_portlets,
        name="lfs_update_portlets",
    ),
    re_path(r"^delete-portlet/(?P<portletassignment_id>\d+)$", lfs_portlets.delete_portlet, name="lfs_delete_portlet"),
    re_path(r"^edit-portlet/(?P<portletassignment_id>\d+)$", lfs_portlets.edit_portlet, name="lfs_edit_portlet"),
    re_path(r"^move-portlet/(?P<portletassignment_id>\d+)$", lfs_portlets.move_portlet, name="lfs_move_portlet"),
    # Product
    re_path(r"^product-dispatcher$", product.product_dispatcher, name="lfs_manage_product_dispatcher"),
    re_path(r"^product-by-id/(?P<product_id>\d*)$", product.product_by_id, name="lfs_manage_product_by_id"),
    re_path(r"^product/(?P<product_id>\d*)$", product.manage_product, name="lfs_manage_product"),
    re_path(r"^product-data-form/(?P<product_id>\d*)$", product.product_data_form),
    re_path(r"^add-product$", product.add_product, name="lfs_manage_add_product"),
    re_path(r"^edit-product-data/(?P<product_id>\d*)$", product.edit_product_data, name="lfs_manage_edit_product_data"),
    re_path(r"^delete-product/(?P<product_id>\d*)$", product.delete_product, name="lfs_manage_delete_product"),
    re_path(
        r"^selectable-products-inline$",
        product.selectable_products_inline,
        name="lfs_manage_selectable_products_inline",
    ),
    re_path(r"^save-product-stock/(?P<product_id>\d*)$", product.stock, name="lfs_save_product_stock"),
    re_path(r"^change-product-subtype/(?P<product_id>\d*)$", product.change_subtype, name="lfs_change_product_subtype"),
    re_path(r"^products$", product.products, name="lfs_manage_products"),
    re_path(r"^products-inline$", product.products_inline, name="lfs_products_inline"),
    re_path(r"^save-products$", product.save_products, name="lfs_manage_save_products"),
    re_path(r"^set-product-filters$", product.set_filters, name="lfs_set_product_filters"),
    re_path(r"^set-product-name-filter$", product.set_name_filter, name="lfs_set_product_name_filter"),
    re_path(r"^reset-product-filters$", product.reset_filters, name="lfs_reset_product_filters"),
    re_path(r"^set-products-page$", product.set_products_page, name="lfs_set_products_page"),
    re_path(r"^no-products$", product.no_products, name="lfs_manage_no_products"),
    re_path(
        r"^product-categories-tab/(?P<product_id>\d*)$",
        lfs.manage.product.categories.manage_categories,
        name="lfs_product_categories_tab",
    ),
    re_path(
        r"^product-accessories-tab/(?P<product_id>\d*)$",
        lfs.manage.product.accessories.load_tab,
        name="lfs_manage_product_accessories_tab",
    ),
    re_path(
        r"^product-relateds-tab/(?P<product_id>\d*)$",
        lfs.manage.product.related_products.load_tab,
        name="lfs_manage_product_related_products_tab",
    ),
    re_path(
        r"^product-variants-tab/(?P<product_id>\d*)$",
        lfs.manage.product.variants.manage_variants,
        name="lfs_manage_product_variants_tab",
    ),
    re_path(
        r"^change-product-categories/(?P<product_id>\d*)$",
        lfs.manage.product.categories.change_categories,
        name="lfs_manage_product_categories",
    ),
    # Product Images
    re_path(r"^add-image/(?P<product_id>\d*)$", lfs.manage.product.images.add_image, name="lfs_manage_add_image"),
    re_path(
        r"^update-images/(?P<product_id>\d*)$", lfs.manage.product.images.update_images, name="lfs_manage_update_images"
    ),
    re_path(r"^product-images/(?P<product_id>\d*)$", lfs.manage.product.images.list_images, name="lfs_manage_images"),
    re_path(
        r"^update-active-images/(?P<product_id>\d*)$",
        lfs.manage.product.images.update_active_images,
        name="lfs_manage_update_active_images",
    ),
    re_path(r"^move-image/(?P<id>\d+)$", lfs.manage.product.images.move_image, name="lfs_move_image"),
    # Product Attachments
    re_path(
        r"^add-attachment/(?P<product_id>\d*)$",
        lfs.manage.product.attachments.add_attachment,
        name="lfs_manage_add_attachment",
    ),
    re_path(
        r"^update-attachments/(?P<product_id>\d*)$",
        lfs.manage.product.attachments.update_attachments,
        name="lfs_manage_update_attachments",
    ),
    re_path(
        r"^product-attachments/(?P<product_id>\d*)$",
        lfs.manage.product.attachments.list_attachments,
        name="lfs_manage_attachments",
    ),
    re_path(
        r"^move-product-attachments/(?P<id>\d+)$",
        lfs.manage.product.attachments.move_attachment,
        name="lfs_move_product_attachment",
    ),
    # Product variants
    re_path(
        r"^properties/(?P<product_id>\d*)$", lfs.manage.product.variants.manage_variants, name="lfs_manage_variants"
    ),
    re_path(
        r"^add-property/(?P<product_id>\d*)$", lfs.manage.product.variants.add_property, name="lfs_manage_add_property"
    ),
    re_path(
        r"^add-property-option/(?P<product_id>\d*)$",
        lfs.manage.product.variants.add_property_option,
        name="lfs_manage_add_property_option",
    ),
    re_path(
        r"^delete-property/(?P<product_id>\d*)/(?P<property_id>\d*)$",
        lfs.manage.product.variants.delete_property,
        name="lfs_manage_delete_property",
    ),
    re_path(
        r"^delete-property-option/(?P<product_id>\d*)/(?P<option_id>\d*)$",
        lfs.manage.product.variants.delete_property_option,
        name="lfs_manage_delete_property_option",
    ),
    re_path(
        r"^change-property-position$",
        lfs.manage.product.variants.change_property_position,
        name="lfs_manage_change_property_position",
    ),
    re_path(
        r"^update-variants/(?P<product_id>\d*)$",
        lfs.manage.product.variants.update_variants,
        name="lfs_manage_update_variants",
    ),
    re_path(
        r"^add-variants/(?P<product_id>\d*)$", lfs.manage.product.variants.add_variants, name="lfs_manage_add_variants"
    ),
    re_path(
        r"^edit-sub-type/(?P<product_id>\d*)$",
        lfs.manage.product.variants.edit_sub_type,
        name="lfs_manage_edit_sub_type",
    ),
    re_path(
        r"^update-category-variant/(?P<product_id>\d*)$",
        lfs.manage.product.variants.update_category_variant,
        name="lfs_update_category_variant",
    ),
    # Global Images
    re_path(r"^imagebrowser$", lfs.manage.images.views.imagebrowser, name="lfs_manage_imagebrowser"),
    re_path(r"^global-images$", lfs.manage.images.views.images, name="lfs_manage_global_images"),
    re_path(r"^global-images-list$", lfs.manage.images.views.images_list, name="lfs_manage_global_images_list"),
    re_path(r"^delete-global-images$", lfs.manage.images.views.delete_images, name="lfs_manage_delete_images"),
    re_path(r"^add-global-images$", lfs.manage.images.views.add_images, name="lfs_manage_add_global_image"),
    # Property Groups
    re_path(
        r"^property-groups", lfs.manage.property_groups.views.manage_property_groups, name="lfs_manage_property_groups"
    ),
    re_path(
        r"^property-group/(?P<id>\d*)",
        lfs.manage.property_groups.views.manage_property_group,
        name="lfs_manage_property_group",
    ),
    re_path(
        r"^add-property-group",
        lfs.manage.property_groups.views.add_property_group,
        name="lfs_manage_add_property_group",
    ),
    re_path(
        r"^delete-property-group/(?P<id>\d*)",
        lfs.manage.property_groups.views.delete_property_group,
        name="lfs_delete_property_group",
    ),
    re_path(
        r"^assign-properties/(?P<group_id>\d*)",
        lfs.manage.property_groups.views.assign_properties,
        name="lfs_assign_properties",
    ),
    re_path(
        r"^update-properties/(?P<group_id>\d*)",
        lfs.manage.property_groups.views.update_properties,
        name="lfs_update_properties",
    ),
    re_path(
        r"^no-property-groups$",
        lfs.manage.property_groups.views.no_property_groups,
        name="lfs_manage_no_property_groups",
    ),
    re_path(
        r"^sort-property-groups$",
        lfs.manage.property_groups.views.sort_property_groups,
        name="lfs_manage_sort_property_groups",
    ),
    # Property Groups / Products
    re_path(
        r"^assign-products-to-property-group/(?P<group_id>\d*)",
        lfs.manage.property_groups.views.assign_products,
        name="lfs_assign_products_to_property_group",
    ),
    re_path(
        r"^remove-products-from-property-group/(?P<group_id>\d*)",
        lfs.manage.property_groups.views.remove_products,
        name="lfs_pg_remove_products",
    ),
    re_path(
        r"^pg-products-inline/(?P<product_group_id>\d*)",
        lfs.manage.property_groups.views.products_inline,
        name="lfs_pg_products_inline",
    ),
    # Shop Properties
    re_path(r"^shop-properties$", lfs.manage.property.views.manage_properties, name="lfs_manage_shop_properties"),
    re_path(r"^shop-property/(?P<id>\d*)", lfs.manage.property.views.manage_property, name="lfs_manage_shop_property"),
    re_path(
        r"^update-shop-property-type/(?P<id>\d*)",
        lfs.manage.property.views.update_property_type,
        name="lfs_update_shop_property_type",
    ),
    re_path(r"^add-shop-property$", lfs.manage.property.views.add_property, name="lfs_add_shop_property"),
    re_path(
        r"^delete-shop-property/(?P<id>\d*)", lfs.manage.property.views.delete_property, name="lfs_delete_shop_property"
    ),
    re_path(
        r"^add-shop-property-option/(?P<property_id>\d*)",
        lfs.manage.property.views.add_option,
        name="lfs_add_shop_property_option",
    ),
    re_path(
        r"^add-shop-property-step/(?P<property_id>\d*)",
        lfs.manage.property.views.add_step,
        name="lfs_add_shop_property_step",
    ),
    re_path(
        r"^save-shop-property-step/(?P<property_id>\d*)",
        lfs.manage.property.views.save_step_range,
        name="lfs_save_shop_property_step_range",
    ),
    re_path(
        r"^save-shop-property-step-type/(?P<property_id>\d*)",
        lfs.manage.property.views.save_step_type,
        name="lfs_save_shop_property_step_type",
    ),
    re_path(
        r"^delete-shop-property-option/(?P<id>\d*)",
        lfs.manage.property.views.delete_option,
        name="lfs_delete_shop_property_option",
    ),
    re_path(
        r"^delete-shop-property-step/(?P<id>\d*)",
        lfs.manage.property.views.delete_step,
        name="lfs_delete_shop_property_step",
    ),
    re_path(
        r"^save-number-field-validators/(?P<property_id>\d*)",
        lfs.manage.property.views.save_number_field_validators,
        name="lfs_save_number_field_validators",
    ),
    re_path(
        r"^save-select-field/(?P<property_id>\d*)",
        lfs.manage.property.views.save_select_field,
        name="lfs_save_select_field",
    ),
    re_path(r"^no-properties$", lfs.manage.property.views.no_properties, name="lfs_manage_no_shop_properties"),
    re_path(
        r"^set-property-name-filter$", lfs.manage.property.views.set_name_filter, name="lfs_set_property_name_filter"
    ),
    re_path(r"^set-property-page$", lfs.manage.property.views.set_properties_page, name="lfs_set_properties_page"),
    # Product properties
    re_path(
        r"^update-product-properties/(?P<product_id>\d*)$",
        lfs.manage.product.properties.update_properties,
        name="lfs_update_product_properties",
    ),
    re_path(
        r"^update-product-property-groups/(?P<product_id>\d*)$",
        lfs.manage.product.properties.update_property_groups,
        name="lfs_update_product_property_groups",
    ),
    # Accesories
    re_path(
        r"^accessories/(?P<product_id>\d*)$",
        lfs.manage.product.accessories.manage_accessories,
        name="lfs_manage_accessories",
    ),
    re_path(
        r"^accessories-inline/(?P<product_id>\d*)$",
        lfs.manage.product.accessories.manage_accessories_inline,
        name="lfs_manage_accessories_inline",
    ),
    re_path(
        r"^add-accessories/(?P<product_id>\d*)$",
        lfs.manage.product.accessories.add_accessories,
        name="lfs_manage_add_accessories",
    ),
    re_path(
        r"^remove-accessories/(?P<product_id>\d*)$",
        lfs.manage.product.accessories.remove_accessories,
        name="lfs_manage_remove_accessories",
    ),
    re_path(
        r"^update-accessories/(?P<product_id>\d*)$",
        lfs.manage.product.accessories.update_accessories,
        name="lfs_manage_update_accessories",
    ),
    # Related Products
    re_path(
        r"^related-products/(?P<product_id>\d*)$",
        lfs.manage.product.related_products.manage_related_products,
        name="lfs_manage_related_products",
    ),
    re_path(
        r"^related-products-inline/(?P<product_id>\d*)$",
        lfs.manage.product.related_products.manage_related_products_inline,
        name="lfs_manage_related_products_inline",
    ),
    re_path(
        r"^add-related-products/(?P<product_id>\d*)$",
        lfs.manage.product.related_products.add_related_products,
        name="lfs_manage_add_related_products",
    ),
    re_path(
        r"^remove-related-products/(?P<product_id>\d*)$",
        lfs.manage.product.related_products.remove_related_products,
        name="lfs_manage_remove_related_products",
    ),
    re_path(
        r"^manage-related-products/(?P<product_id>\d*)$",
        lfs.manage.product.related_products.update_related_products,
        name="lfs_manage_update_related_products",
    ),
    # Carts
    re_path(r"^carts$", lfs.manage.views.carts.carts_view, name="lfs_manage_carts"),
    re_path(r"^carts-inline$", lfs.manage.views.carts.carts_inline, name="lfs_carts_inline"),
    re_path(r"^cart-inline/(?P<cart_id>\d*)$", lfs.manage.views.carts.cart_inline, name="lfs_cart_inline"),
    re_path(r"^cart/(?P<cart_id>\d*)$", lfs.manage.views.carts.cart_view, name="lfs_manage_cart"),
    re_path(
        r"^selectable-carts-inline$", lfs.manage.views.carts.selectable_carts_inline, name="lfs_selectable_carts_inline"
    ),
    re_path(r"^set-cart-filters$", lfs.manage.views.carts.set_cart_filters, name="lfs_set_cart_filters"),
    re_path(r"^set-cart-filters-date$", lfs.manage.views.carts.set_cart_filters_date, name="lfs_set_cart_filters_date"),
    re_path(r"^reset-cart-filters$", lfs.manage.views.carts.reset_cart_filters, name="lfs_reset_cart_filters"),
    re_path(r"^set-carts-page$", lfs.manage.views.carts.set_carts_page, name="lfs_set_carts_page"),
    re_path(r"^set-cart-page$", lfs.manage.views.carts.set_cart_page, name="lfs_set_cart_page"),
    # Categories
    re_path(r"^categories$", lfs.manage.categories.category.manage_categories, name="lfs_manage_categories"),
    re_path(
        r"^category/(?P<category_id>\d*)$", lfs.manage.categories.category.manage_category, name="lfs_manage_category"
    ),
    re_path(
        r"^category-by-id/(?P<category_id>\d*)$",
        lfs.manage.categories.category.category_by_id,
        name="lfs_category_by_id",
    ),
    re_path(
        r"^add-products/(?P<category_id>\d*)$",
        lfs.manage.categories.products.add_products,
        name="lfs_manage_category_add_products",
    ),
    re_path(
        r"^remove-products/(?P<category_id>\d*)$",
        lfs.manage.categories.products.remove_products,
        name="lfs_manage_category_remove_products",
    ),
    re_path(r"^add-top-category$", lfs.manage.categories.category.add_category, name="lfs_manage_add_top_category"),
    re_path(
        r"^add-category/(?P<category_id>\d*)$",
        lfs.manage.categories.category.add_category,
        name="lfs_manage_add_category",
    ),
    re_path(
        r"^delete-category/(?P<id>[-\w]*)$", lfs.manage.categories.category.delete_category, name="lfs_delete_category"
    ),
    re_path(
        r"^products-inline/(?P<category_id>\d*)$",
        lfs.manage.categories.products.products_inline,
        name="lfs_manage_category_products_inline",
    ),
    re_path(
        r"^edit-category-data/(?P<category_id>\d*)$",
        lfs.manage.categories.category.edit_category_data,
        name="lfs_manage_category_edit_data",
    ),
    re_path(
        r"^edit-category-view/(?P<category_id>\d*)$",
        lfs.manage.categories.category.category_view,
        name="lfs_manage_category_view",
    ),
    re_path(
        r"^selected-products/(?P<category_id>\d*)$",
        lfs.manage.categories.products.selected_products,
        name="lfs_selected_products",
    ),
    re_path(
        r"^load-products-tab/(?P<category_id>\d*)$",
        lfs.manage.categories.products.products_tab,
        name="lfs_load_products_tab",
    ),
    re_path(r"^sort-categories$", lfs.manage.categories.category.sort_categories, name="lfs_sort_categories"),
    re_path(r"^no-categories$", lfs.manage.categories.view.no_categories, name="lfs_manage_no_categories"),
    # Customers
    re_path(r"^customers$", lfs.manage.views.customer.customers, name="lfs_manage_customers"),
    re_path(r"^customers-inline$", lfs.manage.views.customer.customers_inline, name="lfs_customers_inline"),
    re_path(r"^customer/(?P<customer_id>\d*)$", lfs.manage.views.customer.customer, name="lfs_manage_customer"),
    re_path(
        r"^customer-inline/(?P<customer_id>\d*)$", lfs.manage.views.customer.customer_inline, name="lfs_customer_inline"
    ),
    re_path(r"^set-customer-filters$", lfs.manage.views.customer.set_customer_filters, name="lfs_set_customer_filters"),
    re_path(
        r"^reset-customer-filters$", lfs.manage.views.customer.reset_customer_filters, name="lfs_reset_customer_filters"
    ),
    re_path(
        r"^set-customer-ordering/(?P<ordering>\w*)$",
        lfs.manage.views.customer.set_ordering,
        name="lfs_set_customer_ordering",
    ),
    re_path(
        r"^selectable-customers-inline$",
        lfs.manage.views.customer.selectable_customers_inline,
        name="lfs_selectable_customers_inline",
    ),
    re_path(
        r"^set-selectable-customers-page$",
        lfs.manage.views.customer.set_selectable_customers_page,
        name="lfs_set_selectable_customers_page",
    ),
    re_path(r"^set-customers-page$", lfs.manage.views.customer.set_customers_page, name="lfs_set_customers_page"),
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
    re_path(r"^shipping$", lfs.manage.shipping_methods.views.manage_shipping, name="lfs_manage_shipping"),
    re_path(
        r"^shipping-method/(?P<shipping_method_id>\d*)$",
        lfs.manage.shipping_methods.views.manage_shipping_method,
        name="lfs_manage_shipping_method",
    ),
    re_path(
        r"^add-shipping-method",
        lfs.manage.shipping_methods.views.add_shipping_method,
        name="lfs_manage_add_shipping_method",
    ),
    re_path(
        r"^save-shipping-data/(?P<shipping_method_id>\d*)$",
        lfs.manage.shipping_methods.views.save_shipping_method_data,
        name="lfs_manage_save_shipping_method_data",
    ),
    re_path(
        r"^delete-shipping-method/(?P<shipping_method_id>\d*)$",
        lfs.manage.shipping_methods.views.delete_shipping_method,
        name="lfs_manage_delete_shipping_method",
    ),
    re_path(
        r"^add-shipping-price/(?P<shipping_method_id>\d*)$",
        lfs.manage.shipping_methods.views.add_shipping_price,
        name="lfs_manage_add_shipping_price",
    ),
    re_path(
        r"^update-shipping-prices/(?P<shipping_method_id>\d*)$",
        lfs.manage.shipping_methods.views.update_shipping_prices,
        name="lfs_manage_update_shipping_prices",
    ),
    re_path(
        r"^shipping-price-criteria/(?P<shipping_price_id>\d*)$",
        lfs.manage.shipping_methods.views.shipping_price_criteria,
        name="lfs_manage_shipping_price_criteria",
    ),
    re_path(
        r"^save-shipping-price-criteria/(?P<shipping_price_id>\d*)$",
        lfs.manage.shipping_methods.views.save_shipping_price_criteria,
        name="lfs_manage_save_shipping_price_criteria",
    ),
    re_path(
        r"^save-shipping-method-criteria/(?P<shipping_method_id>\d*)$",
        lfs.manage.shipping_methods.views.save_shipping_method_criteria,
        name="lfs_manage_save_shipping_method_criteria",
    ),
    re_path(
        r"^sort-shipping-methods$",
        lfs.manage.shipping_methods.views.sort_shipping_methods,
        name="lfs_sort_shipping_methods",
    ),
    re_path(
        r"^no-shipping-methods$",
        lfs.manage.shipping_methods.views.no_shipping_methods,
        name="lfs_manage_no_shipping_methods",
    ),
    # Discounts
    re_path(r"^discounts$", lfs.manage.discounts.views.manage_discounts, name="lfs_manage_discounts"),
    re_path(r"^discount/(?P<id>\d*)$", lfs.manage.discounts.views.manage_discount, name="lfs_manage_discount"),
    re_path(r"^add-discount", lfs.manage.discounts.views.add_discount, name="lfs_manage_add_discount"),
    re_path(
        r"^save-discount-data/(?P<id>\d*)$",
        lfs.manage.discounts.views.save_discount_data,
        name="lfs_manage_save_discount_data",
    ),
    re_path(
        r"^delete-discount/(?P<id>\d*)$", lfs.manage.discounts.views.delete_discount, name="lfs_manage_delete_discount"
    ),
    re_path(
        r"^save-discount-criteria/(?P<id>\d*)$",
        lfs.manage.discounts.views.save_discount_criteria,
        name="lfs_manage_save_discount_criteria",
    ),
    re_path(r"^no-discounts$", lfs.manage.discounts.views.no_discounts, name="lfs_manage_no_discounts"),
    # Discounts / Products
    re_path(
        r"^assign-products-to-discount/(?P<discount_id>\d*)",
        lfs.manage.discounts.views.assign_products,
        name="lfs_assign_products_to_discount",
    ),
    re_path(
        r"^remove-products-from-discount/(?P<discount_id>\d*)",
        lfs.manage.discounts.views.remove_products,
        name="lfs_discount_remove_products",
    ),
    re_path(
        r"^discount-products-inline/(?P<discount_id>\d*)",
        lfs.manage.discounts.views.products_inline,
        name="lfs_discount_products_inline",
    ),
    # Pages
    re_path(r"^add-page$", lfs.manage.pages.views.add_page, name="lfs_add_page"),
    re_path(r"^delete-page/(?P<id>\d*)$", lfs.manage.pages.views.delete_page, name="lfs_delete_page"),
    re_path(r"^manage-pages$", lfs.manage.pages.views.manage_pages, name="lfs_manage_pages"),
    re_path(r"^manage-page/(?P<id>\d*)$", lfs.manage.pages.views.manage_page, name="lfs_manage_page"),
    re_path(r"^page-by-id/(?P<id>\d*)$", lfs.manage.pages.views.page_view_by_id, name="lfs_page_view_by_id"),
    re_path(r"^sort-pages$", lfs.manage.pages.views.sort_pages, name="lfs_sort_pages"),
    re_path(r"^save-page-data-tab/(?P<id>\d*)$", lfs.manage.pages.views.save_data_tab, name="lfs_save_page_data_tab"),
    # Payment
    re_path(r"^payment$", lfs.manage.views.payment.manage_payment, name="lfs_manage_payment"),
    re_path(
        r"^payment-method/(?P<payment_method_id>\d*)$",
        lfs.manage.views.payment.manage_payment_method,
        name="lfs_manage_payment_method",
    ),
    re_path(r"^add-payment-method", lfs.manage.views.payment.add_payment_method, name="lfs_add_payment_method"),
    re_path(
        r"^save-payment-data/(?P<payment_method_id>\d*)$",
        lfs.manage.views.payment.save_payment_method_data,
        name="lfs_manage_save_payment_method_data",
    ),
    re_path(
        r"^delete-payment-method/(?P<payment_method_id>\d*)$",
        lfs.manage.views.payment.delete_payment_method,
        name="lfs_delete_payment_method",
    ),
    re_path(
        r"^add-payment-price/(?P<payment_method_id>\d*)$",
        lfs.manage.views.payment.add_payment_price,
        name="lfs_manage_add_payment_price",
    ),
    re_path(
        r"^update-payment-prices/(?P<payment_method_id>\d*)$",
        lfs.manage.views.payment.update_payment_prices,
        name="lfs_manage_update_payment_prices",
    ),
    re_path(
        r"^payment-price-criteria/(?P<payment_price_id>\d*)$",
        lfs.manage.views.payment.payment_price_criteria,
        name="lfs_manage_payment_price_criteria",
    ),
    re_path(
        r"^save-payment-price-criteria/(?P<payment_price_id>\d*)$",
        lfs.manage.views.payment.save_payment_price_criteria,
        name="lfs_manage_save_payment_price_criteria",
    ),
    re_path(
        r"^save-payment-method-criteria/(?P<payment_method_id>\d*)$",
        lfs.manage.views.payment.save_payment_method_criteria,
        name="lfs_manage_save_payment_method_criteria",
    ),
    re_path(r"^sort-payment-methods$", lfs.manage.views.payment.sort_payment_methods, name="lfs_sort_payment_methods"),
    # Orders
    re_path(r"^manage-orders$", lfs.manage.views.orders.manage_orders, name="lfs_manage_orders"),
    re_path(r"^orders$", lfs.manage.views.orders.orders_view, name="lfs_orders"),
    re_path(r"^orders-inline$", lfs.manage.views.orders.orders_inline, name="lfs_orders_inline"),
    re_path(r"^order/(?P<order_id>\d*)$", lfs.manage.views.orders.order_view, name="lfs_manage_order"),
    re_path(r"^delete-order/(?P<order_id>\d*)$", lfs.manage.views.orders.delete_order, name="lfs_delete_order"),
    re_path(r"^send-order/(?P<order_id>\d*)$", lfs.manage.views.orders.send_order, name="lfs_send_order"),
    re_path(r"^set-orders-filter$", lfs.manage.views.orders.set_order_filters, name="lfs_set_order_filter"),
    re_path(
        r"^set-orders-filter-date$", lfs.manage.views.orders.set_order_filters_date, name="lfs_set_order_filters_date"
    ),
    re_path(r"^reset-order-filter$", lfs.manage.views.orders.reset_order_filters, name="lfs_reset_order_filters"),
    re_path(
        r"^set-selectable-orders-page$",
        lfs.manage.views.orders.set_selectable_orders_page,
        name="lfs_set_selectable_orders_page",
    ),
    re_path(r"^set-orders-page$", lfs.manage.views.orders.set_orders_page, name="lfs_set_orders_page"),
    re_path(r"^change-order-state$", lfs.manage.views.orders.change_order_state, name="lfs_change_order_state"),
    # Order numbers
    re_path(
        r"^save-order-numbers-tab$", lfs.manage.views.shop.save_order_numbers_tab, name="lfs_save_order_numbers_tab"
    ),
    # Criteria
    re_path(r"^add-criterion", lfs.manage.views.criteria.add_criterion, name="lfs_add_criterion"),
    re_path(
        r"^change-criterion",
        lfs.manage.views.criteria.change_criterion_form,
        name="lfs_manage_criteria_change_criterion_form",
    ),
    # Static blocks
    re_path(r"^add-static-block$", lfs.manage.static_blocks.views.add_static_block, name="lfs_manage_add_static_block"),
    re_path(
        r"^delete-static-block/(?P<id>\d*)$",
        lfs.manage.static_blocks.views.delete_static_block,
        name="lfs_delete_static_block",
    ),
    re_path(
        r"^preview-static-block/(?P<id>\d*)$",
        lfs.manage.static_blocks.views.preview_static_block,
        name="lfs_preview_static_block",
    ),
    re_path(r"^static-blocks$", lfs.manage.static_blocks.views.manage_static_blocks, name="lfs_manage_static_blocks"),
    re_path(
        r"^static-block/(?P<id>\d*)$",
        lfs.manage.static_blocks.views.manage_static_block,
        name="lfs_manage_static_block",
    ),
    re_path(
        r"^add_files/(?P<id>[-\w]*)", lfs.manage.static_blocks.views.add_files, name="lfs_add_files_to_static_block"
    ),
    re_path(
        r"^update_files/(?P<id>[-\w]*)", lfs.manage.static_blocks.views.update_files, name="lfs_manage_update_files_sb"
    ),
    re_path(r"^reload_files/(?P<id>[-\w]*)", lfs.manage.static_blocks.views.reload_files, name="lfs_reload_files"),
    re_path(r"^sort-static-blocks$", lfs.manage.static_blocks.views.sort_static_blocks, name="lfs_sort_static_blocks"),
    re_path(r"^no-static-blocks$", lfs.manage.static_blocks.views.no_static_blocks, name="lfs_manage_no_static_blocks"),
    # Reviews
    re_path(r"^reviews$", lfs.manage.views.review.reviews, name="lfs_manage_reviews"),
    re_path(r"^review/(?P<review_id>\d*)$", lfs.manage.views.review.review, name="lfs_manage_review"),
    re_path(r"^set-review-filters$", lfs.manage.views.review.set_review_filters, name="lfs_set_review_filters"),
    re_path(r"^reset-review-filters$", lfs.manage.views.review.reset_review_filters, name="lfs_reset_review_filters"),
    re_path(
        r"^set-review-ordering/(?P<ordering>\w*)$", lfs.manage.views.review.set_ordering, name="lfs_set_review_ordering"
    ),
    re_path(
        r"^set-review-state/(?P<review_id>\d*)$", lfs.manage.views.review.set_review_state, name="lfs_set_review_state"
    ),
    re_path(r"^delete-review/(?P<review_id>\d*)$", lfs.manage.views.review.delete_review, name="lfs_delete_review"),
    re_path(r"^set-reviews-page$", lfs.manage.views.review.set_reviews_page, name="lfs_set_reviews_page"),
    re_path(
        r"^set-selectable-reviews-page$",
        lfs.manage.views.review.set_selectable_reviews_page,
        name="lfs_set_selectable_reviews_page",
    ),
    # Shop
    re_path(r"^shop$", lfs.manage.views.shop.manage_shop, name="lfs_manage_shop"),
    re_path(r"^save-shop-data-tab$", lfs.manage.views.shop.save_data_tab, name="lfs_save_shop_data_tab"),
    re_path(
        r"^save-shop-default-values-tab$",
        lfs.manage.views.shop.save_default_values_tab,
        name="lfs_save_shop_default_values_tab",
    ),
    # Actions
    re_path(r"^actions$", lfs.manage.actions.views.manage_actions, name="lfs_manage_actions"),
    re_path(r"^action/(?P<id>\d*)$", lfs.manage.actions.views.manage_action, name="lfs_manage_action"),
    re_path(r"^no-actions$", lfs.manage.actions.views.no_actions, name="lfs_no_actions"),
    re_path(r"^add-action$", lfs.manage.actions.views.add_action, name="lfs_add_action"),
    re_path(r"^delete-action/(?P<id>\d*)$", lfs.manage.actions.views.delete_action, name="lfs_delete_action"),
    re_path(r"^save-action/(?P<id>\d*)$", lfs.manage.actions.views.save_action, name="lfs_save_action"),
    re_path(r"^sort-actions$", lfs.manage.actions.views.sort_actions, name="lfs_sort_actions"),
    # Product Taxes
    re_path(r"^add-product-tax$", lfs.manage.product_taxes.views.add_tax, name="lfs_manage_add_tax"),
    re_path(r"^delete-product-tax/(?P<id>\d*)$", lfs.manage.product_taxes.views.delete_tax, name="lfs_delete_tax"),
    re_path(r"^product-taxes$", lfs.manage.product_taxes.views.manage_taxes, name="lfs_manage_taxes"),
    re_path(r"^product-tax/(?P<id>\d*)$", lfs.manage.product_taxes.views.manage_tax, name="lfs_manage_tax"),
    re_path(r"^no-product-taxes$", lfs.manage.product_taxes.views.no_taxes, name="lfs_manage_no_taxes"),
    # Customer tax
    re_path(r"^add-customer-tax$", lfs.manage.customer_tax.views.add_customer_tax, name="lfs_add_customer_tax"),
    re_path(
        r"^delete-customer-tax/(?P<id>\d*)$",
        lfs.manage.customer_tax.views.delete_customer_tax,
        name="lfs_delete_customer_tax",
    ),
    re_path(r"^customer-taxes$", lfs.manage.customer_tax.views.manage_customer_taxes, name="lfs_manage_customer_taxes"),
    re_path(
        r"^customer-tax/(?P<id>\d*)$", lfs.manage.customer_tax.views.manage_customer_tax, name="lfs_manage_customer_tax"
    ),
    re_path(
        r"^no-customer-taxes$", lfs.manage.customer_tax.views.no_customer_taxes, name="lfs_manage_no_customer_taxes"
    ),
    re_path(
        r"^save-customer-tax-criteria/(?P<id>\d*)$",
        lfs.manage.customer_tax.views.save_criteria,
        name="lfs_manage_save_customer_tax_criteria",
    ),
    re_path(
        r"^save-customer-tax-data/(?P<id>\d*)$",
        lfs.manage.customer_tax.views.save_data,
        name="lfs_manage_save_customer_tax_data",
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
urlpatterns += PageSEOView.get_seo_urlpattern(Page)
urlpatterns += SEOView.get_seo_urlpattern(Product, form_klass=ProductSEOForm, template_name="manage/product/seo.html")
urlpatterns += SEOView.get_seo_urlpattern(Category)
