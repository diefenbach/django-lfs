from django.urls import path, re_path, include
import lfs.manage
import lfs.manage.customer_tax.views
import lfs.manage.images.views
import lfs.manage.information.views
import lfs.manage.products

# Removed imports for non-existent product modules
import lfs.manage.product_taxes.views
import lfs.manage.shipping_methods.views
import lfs.manage.views.criteria
import lfs.manage.views.export
import lfs.manage.views.payment
import lfs.manage.views.utils
from lfs.catalog.models import Product
from lfs.catalog.models import Category
from lfs.core.models import Shop
from lfs.manage.products.forms import SEOForm as ProductSEOForm
from lfs.manage.views.shop import ShopSEOView
from lfs.manage.seo.views import SEOView
from lfs.manage.manufacturers import views as manufacturers_views
from lfs.manage.manufacturers import products as manufacturers_products_views
from lfs.manufacturer.models import Manufacturer


urlpatterns = [
    path("", include("lfs.manage.dashboard.urls")),
    # Delivery Times
    path("", include("lfs.manage.delivery_times.urls")),
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
    path("", include("lfs.manage.featured.urls")),
    # Marketing
    path("", include("lfs.manage.review_mails.urls")),
    # Topseller Products
    path("", include("lfs.manage.topseller.urls")),
    # Voucher Groups
    path("", include("lfs.manage.voucher.urls")),
    # Portlets
    path("", include("lfs.manage.portlets.urls")),
    # Product
    # Product management URLs are now handled by modern class-based views in products/urls.py
    re_path(r"^imagebrowser$", lfs.manage.images.views.imagebrowser, name="lfs_manage_imagebrowser"),
    re_path(r"^global-images$", lfs.manage.images.views.images, name="lfs_manage_global_images"),
    re_path(r"^global-images-list$", lfs.manage.images.views.images_list, name="lfs_manage_global_images_list"),
    re_path(r"^delete-global-images$", lfs.manage.images.views.delete_images, name="lfs_manage_delete_images"),
    re_path(r"^add-global-images$", lfs.manage.images.views.add_images, name="lfs_manage_add_global_image"),
    # Property Groups
    path("", include("lfs.manage.property_groups.urls")),
    # Properties
    path("", include("lfs.manage.properties.urls")),
    # Product properties
    re_path(
        r"^update-product-properties/(?P<id>\d*)$",
        lfs.manage.products.views.ProductPropertiesView.as_view(),
        name="lfs_update_product_properties",
    ),
    re_path(
        r"^update-product-property-groups/(?P<id>\d*)$",
        lfs.manage.products.views.ProductPropertiesView.as_view(),
        name="lfs_update_product_property_groups",
    ),
    # Carts
    path("", include("lfs.manage.carts.urls")),
    # Categories
    path("", include("lfs.manage.categories.urls")),
    # Customers (refactored views)
    path("", include("lfs.manage.customers.urls")),
    # Products (refactored views)
    path("", include("lfs.manage.products.urls")),
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
    path("", include("lfs.manage.discounts.urls")),
    # Pages
    path("", include("lfs.manage.pages.urls")),
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
    path("", include("lfs.manage.orders.urls")),
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
    path("", include("lfs.manage.static_blocks.urls")),
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
    path("", include("lfs.manage.actions.urls")),
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
urlpatterns += SEOView.get_seo_urlpattern(Product, form_klass=ProductSEOForm, template_name="manage/products/seo.html")
urlpatterns += SEOView.get_seo_urlpattern(Category)
