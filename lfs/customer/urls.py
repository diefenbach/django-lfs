from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.login, name="lfs_login"),
    url(r'^logout/$', views.logout, name="lfs_logout"),
    url(r'^my-account/$', views.account, name="lfs_my_account"),
    url(r'^my-addresses/$', views.addresses, name="lfs_my_addresses"),
    url(r'^my-email/$', views.email, name="lfs_my_email"),
    url(r'^my-orders/$', views.orders, name="lfs_my_orders"),
    url(r'^my-order/(?P<id>\d+)/$', views.order, name="lfs_my_order"),
    url(r'^my-password/$', views.password, name="lfs_my_password"),
]
