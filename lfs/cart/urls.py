from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add-to-cart/$', views.add_to_cart, name="lfs_add_to_cart"),
    url(r'^add-accessory-to-cart/(?P<product_id>\d*)/$', views.add_accessory_to_cart, name="lfs_add_accessory_to_cart"),
    url(r'^added-to-cart/$', views.added_to_cart, name="lfs_added_to_cart"),
    url(r'^delete-cart-item/(?P<cart_item_id>\d*)/$', views.delete_cart_item, name="lfs_delete_cart_item"),
    url(r'^refresh-cart/$', views.refresh_cart, name="lfs_refresh_cart"),
    url(r'^cart/$', views.cart, name="lfs_cart"),
    url(r'^check-voucher-cart/$', views.check_voucher, name="lfs_check_voucher_cart"),
]
