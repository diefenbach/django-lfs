from django.urls import path, re_path
from . import views, views_new

urlpatterns = [
    re_path(r"^checkout-dispatcher/$", views.checkout_dispatcher, name="lfs_checkout_dispatcher"),
    re_path(r"^checkout-login/$", views.login, name="lfs_checkout_login"),
    re_path(r"^checkout/$", views.one_page_checkout, name="lfs_checkout"),
    re_path(r"^thank-you/$", views.thank_you, name="lfs_thank_you"),
    re_path(r"^changed-checkout/$", views.changed_checkout, name="lfs_changed_checkout"),
    re_path(r"^changed-invoice-country/$", views.changed_invoice_country, name="lfs_changed_invoice_country"),
    re_path(r"^changed-shipping-country/$", views.changed_shipping_country, name="lfs_changed_shipping_country"),
    re_path(r"^check-voucher/$", views.check_voucher, name="lfs_check_voucher"),
    path("checkout/addresses", views_new.addresses, name="lfs_checkout_addresses"),
    path("checkout/payment-and-shipping", views_new.payment_and_delivery, name="lfs_checkout_payment_and_shipping"),
    path("checkout/check-and-pay", views_new.check_and_pay, name="lfs_checkout_check_and_pay"),
    path("checkout/delete-voucher", views_new.delete_voucher, name="lfs_delete_voucher"),
    path("checkout/set-voucher", views_new.set_voucher, name="lfs_set_voucher"),
]
