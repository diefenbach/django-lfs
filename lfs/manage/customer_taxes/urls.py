from django.urls import path
import lfs.manage.customer_taxes.views

urlpatterns = [
    path(
        "customer-taxes/",
        lfs.manage.customer_taxes.views.ManageCustomerTaxesView.as_view(),
        name="lfs_manage_customer_taxes",
    ),
    path(
        "customer-tax/<int:id>/data",
        lfs.manage.customer_taxes.views.CustomerTaxDataView.as_view(),
        name="lfs_manage_customer_tax",
    ),
    path(
        "customer-tax/<int:id>/criteria/",
        lfs.manage.customer_taxes.views.CustomerTaxCriteriaView.as_view(),
        name="lfs_manage_customer_tax_criteria",
    ),
    path(
        "customer-tax/add",
        lfs.manage.customer_taxes.views.CustomerTaxCreateView.as_view(),
        name="lfs_manage_add_customer_tax",
    ),
    path(
        "customer-tax/<int:id>/delete-confirm",
        lfs.manage.customer_taxes.views.CustomerTaxDeleteConfirmView.as_view(),
        name="lfs_manage_delete_customer_tax_confirm",
    ),
    path(
        "customer-tax/<int:id>/delete",
        lfs.manage.customer_taxes.views.CustomerTaxDeleteView.as_view(),
        name="lfs_manage_delete_customer_tax",
    ),
    path(
        "customer-taxes/no",
        lfs.manage.customer_taxes.views.NoCustomerTaxesView.as_view(),
        name="lfs_manage_no_customer_taxes",
    ),
]
