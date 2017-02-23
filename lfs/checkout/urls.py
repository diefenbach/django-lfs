from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^checkout-dispatcher/$', views.checkout_dispatcher, name="lfs_checkout_dispatcher"),
    url(r'^checkout-login/$', views.login, name="lfs_checkout_login"),
    url(r'^checkout/$', views.one_page_checkout, name="lfs_checkout"),
    url(r'^thank-you/$', views.thank_you, name="lfs_thank_you"),
    url(r'^changed-checkout/$', views.changed_checkout, name="lfs_changed_checkout"),
    url(r'^changed-invoice-country/$', views.changed_invoice_country, name="lfs_changed_invoice_country"),
    url(r'^changed-shipping-country/$', views.changed_shipping_country, name="lfs_changed_shipping_country"),
    url(r'^check-voucher/$', views.check_voucher, name="lfs_check_voucher"),
]
