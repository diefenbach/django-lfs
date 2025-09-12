from django.urls import path
import lfs.manage.payment_methods.views

urlpatterns = [
    path(
        "payment-methods/",
        lfs.manage.payment_methods.views.ManagePaymentsView.as_view(),
        name="lfs_manage_payment_methods",
    ),
    path(
        "payment-method/<int:id>/",
        lfs.manage.payment_methods.views.PaymentMethodDataView.as_view(),
        name="lfs_manage_payment_method",
    ),
    path(
        "payment-method/<int:id>/criteria/",
        lfs.manage.payment_methods.views.PaymentMethodCriteriaView.as_view(),
        name="lfs_manage_payment_method_criteria",
    ),
    path(
        "payment-method/<int:id>/prices/",
        lfs.manage.payment_methods.views.PaymentMethodPricesView.as_view(),
        name="lfs_manage_payment_method_prices",
    ),
    path(
        "payment-method/add",
        lfs.manage.payment_methods.views.PaymentMethodCreateView.as_view(),
        name="lfs_manage_add_payment_method",
    ),
    path(
        "payment-method/<int:id>/delete-confirm",
        lfs.manage.payment_methods.views.PaymentMethodDeleteConfirmView.as_view(),
        name="lfs_manage_delete_payment_method_confirm",
    ),
    path(
        "payment-method/<int:id>/delete",
        lfs.manage.payment_methods.views.PaymentMethodDeleteView.as_view(),
        name="lfs_manage_delete_payment_method",
    ),
    path(
        "payment-methods/no",
        lfs.manage.payment_methods.views.NoPaymentMethodsView.as_view(),
        name="lfs_manage_no_payment_methods",
    ),
]
