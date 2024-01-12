from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^checkout-dispatcher/$", views.checkout_dispatcher, name="lfs_checkout_dispatcher"),
    re_path(r"^checkout-login/$", views.login, name="lfs_checkout_login"),
    re_path(r"^checkout/$", views.one_page_checkout, name="lfs_checkout"),
    re_path(r"^thank-you/$", views.thank_you, name="lfs_thank_you"),
    re_path(r"^changed-checkout/$", views.changed_checkout, name="lfs_changed_checkout"),
    re_path(r"^changed-invoice-country/$", views.changed_invoice_country, name="lfs_changed_invoice_country"),
    re_path(r"^changed-shipping-country/$", views.changed_shipping_country, name="lfs_changed_shipping_country"),
    re_path(r"^check-voucher/$", views.check_voucher, name="lfs_check_voucher"),
]
