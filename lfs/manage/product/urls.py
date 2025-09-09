from django.urls import path

from .views import (
    ManageProductsView,
    NoProductsView,
    ProductDataView,
    ProductCategoriesView,
    ProductImagesView,
    ProductAttachmentsView,
    ProductBulkPricesView,
    ProductPortletsView,
    ProductVariantsView,
    ProductAccessoriesView,
    ProductRelatedProductsView,
    ProductSEOView,
    ProductStockView,
)

urlpatterns = [
    path("", ManageProductsView.as_view(), name="lfs_manage_products2"),
    path("no-products/", NoProductsView.as_view(), name="lfs_manage_no_products"),

    path("<int:id>/data/", ProductDataView.as_view(), name="lfs_manage_product_data"),
    path("<int:id>/categories/", ProductCategoriesView.as_view(), name="lfs_manage_product_categories"),
    path("<int:id>/images/", ProductImagesView.as_view(), name="lfs_manage_product_images"),
    path("<int:id>/attachments/", ProductAttachmentsView.as_view(), name="lfs_manage_product_attachments"),
    path("<int:id>/bulk-prices/", ProductBulkPricesView.as_view(), name="lfs_manage_product_bulk_prices"),
    path("<int:id>/variants/", ProductVariantsView.as_view(), name="lfs_manage_product_variants"),
    path("<int:id>/accessories/", ProductAccessoriesView.as_view(), name="lfs_manage_product_accessories"),
    path("<int:id>/related/", ProductRelatedProductsView.as_view(), name="lfs_manage_product_related"),
    path("<int:id>/stock/", ProductStockView.as_view(), name="lfs_manage_product_stock"),
    path("<int:id>/seo/", ProductSEOView.as_view(), name="lfs_manage_product_seo"),
    path("<int:id>/portlets/", ProductPortletsView.as_view(), name="lfs_manage_product_portlets"),
]
