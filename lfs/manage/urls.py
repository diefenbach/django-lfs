from django.urls import path, re_path, include
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
import lfs.manage.carts.views
import lfs.manage.views.customer
import lfs.manage.views.criteria
import lfs.manage.views.dashboard
import lfs.manage.views.export
import lfs.manage.views.marketing.rating_mails
import lfs.manage.topseller.views
import lfs.manage.orders.views
import lfs.manage.views.payment
import lfs.manage.views.utils
import lfs.manage.pages.views
from lfs.catalog.models import Product
from lfs.catalog.models import Category
from lfs.core.models import Shop
from lfs.manage.product.seo import SEOForm as ProductSEOForm
from lfs.manage.views.shop import ShopSEOView
from lfs.manage.seo.views import SEOView
from lfs.manage.delivery_times import views as delivery_times_views
from lfs.manage.manufacturers import views as manufacturers_views
from lfs.manage.manufacturers import products as manufacturers_products_views
from lfs.manage.featured import views as featured_views
import lfs.manage.voucher.views
from lfs.manage.views import lfs_portlets
from lfs.manage.product import product
from lfs.manufacturer.models import Manufacturer


urlpatterns = [
    path("", lfs.manage.views.dashboard.dashboard, name="lfs_manage_dashboard"),
    # Delivery Times
    path(
        "delivery-times",
        delivery_times_views.ManageDeliveryTimesView.as_view(),
        name="lfs_manage_delivery_times",
    ),
    path(
        "delivery-time/<int:pk>",
        delivery_times_views.DeliveryTimeUpdateView.as_view(),
        name="lfs_manage_delivery_time",
    ),
    path(
        "add-delivery-time",
        delivery_times_views.DeliveryTimeCreateView.as_view(),
        name="lfs_manage_add_delivery_time",
    ),
    path(
        "delete-delivery-time/<int:pk>",
        delivery_times_views.DeliveryTimeDeleteView.as_view(),
        name="lfs_manage_delete_delivery_time",
    ),
    path(
        "delete-delivery-time-confirm/<int:pk>",
        delivery_times_views.DeliveryTimeDeleteConfirmView.as_view(),
        name="lfs_manage_delete_delivery_time_confirm",
    ),
    path(
        "no-delivery-times",
        delivery_times_views.NoDeliveryTimesView.as_view(),
        name="lfs_no_delivery_times",
    ),
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
    # Featured Products
    path(
        "featured",
        featured_views.ManageFeaturedView.as_view(),
        name="lfs_manage_featured",
    ),
    path(
        "add-featured",
        featured_views.add_featured,
        name="lfs_manage_add_featured",
    ),
    path(
        "update-featured",
        featured_views.update_featured,
        name="lfs_manage_update_featured",
    ),
    path(
        "sort-featured",
        featured_views.sort_featured,
        name="lfs_manage_sort_featured",
    ),
    # Marketing
    re_path(
        r"^manage-rating-mails$",
        lfs.manage.views.marketing.rating_mails.manage_rating_mails,
        name="lfs_manage_rating_mails",
    ),
    re_path(
        r"^send-rating-mails$", lfs.manage.views.marketing.rating_mails.send_rating_mails, name="lfs_send_rating_mails"
    ),
    # Topseller Products
    path(
        "topseller",
        lfs.manage.topseller.views.ManageTopsellerView.as_view(),
        name="lfs_manage_topseller",
    ),
    path(
        "add-topseller",
        lfs.manage.topseller.views.add_topseller,
        name="lfs_manage_add_topseller",
    ),
    path(
        "update-topseller",
        lfs.manage.topseller.views.update_topseller,
        name="lfs_manage_update_topseller",
    ),
    path(
        "sort-topseller",
        lfs.manage.topseller.views.sort_topseller,
        name="lfs_manage_sort_topseller",
    ),
    re_path(
        r"^topseller-inline$",
        lfs.manage.topseller.views.manage_topseller_inline,
        name="lfs_manage_topseller_inline",
    ),
    # Voucher Groups
    re_path(
        r"^vouchers$",
        lfs.manage.voucher.views.ManageVoucherGroupsView.as_view(),
        name="lfs_manage_voucher_groups",
    ),
    re_path(
        r"^voucher-group/(?P<id>\d+)$",
        lfs.manage.voucher.views.VoucherGroupDataView.as_view(),
        name="lfs_manage_voucher_group",
    ),
    re_path(
        r"^voucher-group/(?P<id>\d+)/vouchers$",
        lfs.manage.voucher.views.VoucherGroupVouchersView.as_view(),
        name="lfs_manage_voucher_group_vouchers",
    ),
    re_path(
        r"^voucher-group/(?P<id>\d+)/options$",
        lfs.manage.voucher.views.VoucherGroupOptionsView.as_view(),
        name="lfs_manage_voucher_group_options",
    ),
    re_path(
        r"^add-voucher-group$",
        lfs.manage.voucher.views.VoucherGroupCreateView.as_view(),
        name="lfs_manage_add_voucher_group",
    ),
    re_path(
        r"^delete-voucher-group-confirm/(?P<id>\d+)$",
        lfs.manage.voucher.views.VoucherGroupDeleteConfirmView.as_view(),
        name="lfs_manage_delete_voucher_group_confirm",
    ),
    re_path(
        r"^delete-voucher-group/(?P<id>\d+)$",
        lfs.manage.voucher.views.VoucherGroupDeleteView.as_view(),
        name="lfs_delete_voucher_group",
    ),
    re_path(
        r"^no-voucher-groups$",
        lfs.manage.voucher.views.NoVoucherGroupsView.as_view(),
        name="lfs_manage_no_voucher_groups",
    ),
    # Portlets
    re_path(
        r"^add-portlet/(?P<object_type_id>\d+)/(?P<object_id>\d+)$",
        lfs_portlets.AddPortletView.as_view(),
        name="lfs_add_portlet",
    ),
    re_path(
        r"^update-portlets/(?P<object_type_id>\d+)/(?P<object_id>\d+)$",
        lfs_portlets.UpdatePortletsView.as_view(),
        name="lfs_update_portlets",
    ),
    re_path(
        r"^delete-portlet/(?P<portletassignment_id>\d+)$",
        lfs_portlets.DeletePortletView.as_view(),
        name="lfs_delete_portlet",
    ),
    re_path(
        r"^edit-portlet/(?P<portletassignment_id>\d+)$", lfs_portlets.EditPortletView.as_view(), name="lfs_edit_portlet"
    ),
    re_path(
        r"^move-portlet/(?P<portletassignment_id>\d+)$", lfs_portlets.MovePortletView.as_view(), name="lfs_move_portlet"
    ),
    re_path(r"^sort-portlets$", lfs_portlets.SortPortletsView.as_view(), name="lfs_sort_portlets"),
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
    path(
        "carts",
        lfs.manage.carts.views.CartListView.as_view(),
        name="lfs_manage_carts",
    ),
    path(
        "cart/<int:id>/",
        lfs.manage.carts.views.CartDataView.as_view(),
        name="lfs_manage_cart",
    ),
    path(
        "cart/<int:id>/apply-filters/",
        lfs.manage.carts.views.ApplyCartFiltersView.as_view(),
        name="lfs_apply_cart_filters",
    ),
    path(
        "cart/<int:id>/apply-predefined-filter/<str:filter_type>/",
        lfs.manage.carts.views.ApplyPredefinedCartFilterView.as_view(),
        name="lfs_apply_predefined_cart_filter",
    ),
    path(
        "carts/apply-filters/",
        lfs.manage.carts.views.ApplyCartFiltersView.as_view(),
        name="lfs_apply_cart_filters_list",
    ),
    path(
        "carts/apply-predefined-filter/<str:filter_type>/",
        lfs.manage.carts.views.ApplyPredefinedCartFilterView.as_view(),
        name="lfs_apply_predefined_cart_filter_list",
    ),
    path(
        "delete-cart-confirm/<int:id>",
        lfs.manage.carts.views.CartDeleteConfirmView.as_view(),
        name="lfs_manage_delete_cart_confirm",
    ),
    path(
        "delete-cart/<int:id>",
        lfs.manage.carts.views.CartDeleteView.as_view(),
        name="lfs_delete_cart",
    ),
    path(
        "no-carts",
        lfs.manage.carts.views.NoCartsView.as_view(),
        name="lfs_manage_no_carts",
    ),
    path(
        "reset-cart-filters",
        lfs.manage.carts.views.ResetCartFiltersView.as_view(),
        name="lfs_reset_cart_filters",
    ),
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
    path("discounts/", lfs.manage.discounts.views.ManageDiscountsView.as_view(), name="lfs_manage_discounts"),
    path("discount/<int:id>/", lfs.manage.discounts.views.DiscountDataView.as_view(), name="lfs_manage_discount"),
    path(
        "discount/<int:id>/criteria/",
        lfs.manage.discounts.views.DiscountCriteriaView.as_view(),
        name="lfs_manage_discount_criteria",
    ),
    path(
        "discount/<int:id>/products/",
        lfs.manage.discounts.views.DiscountProductsView.as_view(),
        name="lfs_manage_discount_products",
    ),
    path("add-discount/", lfs.manage.discounts.views.DiscountCreateView.as_view(), name="lfs_manage_add_discount"),
    path(
        "delete-discount-confirm/<int:id>/",
        lfs.manage.discounts.views.DiscountDeleteConfirmView.as_view(),
        name="lfs_manage_delete_discount_confirm",
    ),
    path(
        "delete-discount/<int:id>/",
        lfs.manage.discounts.views.DiscountDeleteView.as_view(),
        name="lfs_manage_delete_discount",
    ),
    path("no-discounts/", lfs.manage.discounts.views.NoDiscountsView.as_view(), name="lfs_manage_no_discounts"),
    # Pages
    re_path(r"^add-page$", lfs.manage.pages.views.PageCreateView.as_view(), name="lfs_add_page"),
    re_path(r"^delete-page/(?P<id>\d*)$", lfs.manage.pages.views.PageDeleteView.as_view(), name="lfs_delete_page"),
    re_path(
        r"^delete-page-confirm/(?P<id>\d*)$",
        lfs.manage.pages.views.PageDeleteConfirmView.as_view(),
        name="lfs_delete_page_confirm",
    ),
    re_path(r"^manage-pages$", lfs.manage.pages.views.ManagePagesView.as_view(), name="lfs_manage_pages"),
    re_path(r"^manage-page/(?P<id>\d*)$", lfs.manage.pages.views.PageDataView.as_view(), name="lfs_manage_page"),
    re_path(r"^manage-page-seo/(?P<id>\d*)$", lfs.manage.pages.views.PageSEOView.as_view(), name="lfs_manage_page_seo"),
    re_path(
        r"^manage-page-portlets/(?P<id>\d*)$",
        lfs.manage.pages.views.PagePortletsView.as_view(),
        name="lfs_manage_page_portlets",
    ),
    re_path(r"^page-by-id/(?P<id>\d*)$", lfs.manage.pages.views.PageViewByIDView.as_view(), name="lfs_page_view_by_id"),
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
    re_path(r"^manage-orders$", lfs.manage.orders.views.manage_orders, name="lfs_manage_orders"),
    re_path(r"^orders$", lfs.manage.orders.views.orders_view, name="lfs_orders"),
    # Inline endpoints no longer used after clean cut; keep temporarily for compatibility if referenced
    re_path(r"^order/(?P<order_id>\d*)$", lfs.manage.orders.views.order_view, name="lfs_manage_order"),
    re_path(
        r"^delete-order/(?P<order_id>\d*)$", lfs.manage.orders.views.OrderDeleteView.as_view(), name="lfs_delete_order"
    ),
    re_path(r"^send-order/(?P<order_id>\d*)$", lfs.manage.orders.views.send_order, name="lfs_send_order"),
    # Order filters (class-based equivalents wired through function delegations for now)
    path("set-orders-filter", lfs.manage.orders.views.ApplyOrderFiltersView.as_view(), name="lfs_set_order_filter"),
    path(
        "set-orders-filter-date/<str:filter_type>",
        lfs.manage.orders.views.ApplyPredefinedOrderFilterView.as_view(),
        name="lfs_apply_predefined_order_filter",
    ),
    path("reset-order-filter", lfs.manage.orders.views.ResetOrderFiltersView.as_view(), name="lfs_reset_order_filters"),
    # Deprecated: inline pagination endpoints removed in clean cut
    re_path(r"^change-order-state$", lfs.manage.orders.views.change_order_state, name="lfs_change_order_state"),
    # Order numbers
    re_path(
        r"^save-order-numbers-tab$", lfs.manage.views.shop.save_order_numbers_tab, name="lfs_save_order_numbers_tab"
    ),
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
    # Static blocks
    path(
        "add-static-block",
        lfs.manage.static_blocks.views.StaticBlockCreateView.as_view(),
        name="lfs_manage_add_static_block",
    ),
    path(
        "delete-static-block-confirm/<int:id>",
        lfs.manage.static_blocks.views.StaticBlockDeleteConfirmView.as_view(),
        name="lfs_manage_delete_static_block_confirm",
    ),
    path(
        "delete-static-block/<int:id>",
        lfs.manage.static_blocks.views.StaticBlockDeleteView.as_view(),
        name="lfs_delete_static_block",
    ),
    path(
        "preview-static-block/<int:id>",
        lfs.manage.static_blocks.views.StaticBlockPreviewView.as_view(),
        name="lfs_preview_static_block",
    ),
    path(
        "static-blocks",
        lfs.manage.static_blocks.views.ManageStaticBlocksView.as_view(),
        name="lfs_manage_static_blocks",
    ),
    path(
        "static-block/<int:id>/",
        lfs.manage.static_blocks.views.StaticBlockDataView.as_view(),
        name="lfs_manage_static_block",
    ),
    path(
        "static-block/<int:id>/files/",
        lfs.manage.static_blocks.views.StaticBlockFilesView.as_view(),
        name="lfs_manage_static_block_files",
    ),
    path(
        "update_files/<str:id>",
        lfs.manage.static_blocks.views.StaticBlockFilesView.as_view(),
        name="lfs_manage_update_files_sb",
    ),
    path(
        "no-static-blocks",
        lfs.manage.static_blocks.views.NoStaticBlocksView.as_view(),
        name="lfs_manage_no_static_blocks",
    ),
    # Reviews
    path("reviews/", include("lfs.manage.reviews.urls")),
    # Shop
    re_path(r"^shop$", lfs.manage.views.shop.manage_shop, name="lfs_manage_shop"),
    re_path(r"^save-shop-data-tab$", lfs.manage.views.shop.save_data_tab, name="lfs_save_shop_data_tab"),
    re_path(
        r"^save-shop-default-values-tab$",
        lfs.manage.views.shop.save_default_values_tab,
        name="lfs_save_shop_default_values_tab",
    ),
    # Actions
    path("actions/", lfs.manage.actions.views.manage_actions, name="lfs_manage_actions"),
    path("action/<int:pk>/", lfs.manage.actions.views.ActionUpdateView.as_view(), name="lfs_manage_action"),
    path("add-action/", lfs.manage.actions.views.ActionCreateView.as_view(), name="lfs_add_action"),
    path(
        "delete-action-confirm/<int:pk>/",
        lfs.manage.actions.views.ActionDeleteConfirmView.as_view(),
        name="lfs_manage_delete_action_confirm",
    ),
    path("delete-action/<int:pk>/", lfs.manage.actions.views.ActionDeleteView.as_view(), name="lfs_delete_action"),
    path("no-actions/", lfs.manage.actions.views.NoActionsView.as_view(), name="lfs_no_actions"),
    path("sort-actions/", lfs.manage.actions.views.sort_actions, name="lfs_sort_actions"),
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
urlpatterns += SEOView.get_seo_urlpattern(Product, form_klass=ProductSEOForm, template_name="manage/product/seo.html")
urlpatterns += SEOView.get_seo_urlpattern(Category)
