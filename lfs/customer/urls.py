from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^login/$", views.login, name="lfs_login"),
    re_path(r"^logout/$", views.logout, name="lfs_logout"),
    re_path(r"^my-account/$", views.account, name="lfs_my_account"),
    re_path(r"^my-addresses/$", views.addresses, name="lfs_my_addresses"),
    re_path(r"^my-email/$", views.email, name="lfs_my_email"),
    re_path(r"^my-orders/$", views.orders, name="lfs_my_orders"),
    re_path(r"^my-order/(?P<id>\d+)/$", views.order, name="lfs_my_order"),
    re_path(r"^my-password/$", views.password, name="lfs_my_password"),
]
