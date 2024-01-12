from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^add-to-cart/$", views.add_to_cart, name="lfs_add_to_cart"),
    re_path(
        r"^add-accessory-to-cart/(?P<product_id>\d*)/$", views.add_accessory_to_cart, name="lfs_add_accessory_to_cart"
    ),
    re_path(r"^added-to-cart/$", views.added_to_cart, name="lfs_added_to_cart"),
    re_path(r"^delete-cart-item/(?P<cart_item_id>\d*)/$", views.delete_cart_item, name="lfs_delete_cart_item"),
    re_path(r"^refresh-cart/$", views.refresh_cart, name="lfs_refresh_cart"),
    re_path(r"^cart/$", views.cart, name="lfs_cart"),
    re_path(r"^check-voucher-cart/$", views.check_voucher, name="lfs_check_voucher_cart"),
]
