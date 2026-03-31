from django.urls import path
import lfs.manage.shop.views

urlpatterns = [
    path(
        "shop/data/",
        lfs.manage.shop.views.ShopDataView.as_view(),
        name="lfs_manage_shop_data",
    ),
    path(
        "shop/default-values/",
        lfs.manage.shop.views.ShopDefaultValuesView.as_view(),
        name="lfs_manage_shop_default_values",
    ),
    path(
        "shop/order-numbers/",
        lfs.manage.shop.views.ShopOrderNumbersView.as_view(),
        name="lfs_manage_shop_order_numbers",
    ),
    path(
        "shop/seo/",
        lfs.manage.shop.views.ShopSEOTabView.as_view(),
        name="lfs_manage_shop_seo",
    ),
    path(
        "shop/portlets/",
        lfs.manage.shop.views.ShopPortletsView.as_view(),
        name="lfs_manage_shop_portlets",
    ),
    path(
        "shop/carousel/",
        lfs.manage.shop.views.ShopCarouselView.as_view(),
        name="lfs_manage_shop_carousel",
    ),
]
