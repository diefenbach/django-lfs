from django.urls import path
from lfs.manage.product_taxes import views as product_taxes_views

urlpatterns = [
    path(
        "taxes",
        product_taxes_views.ManageTaxesView.as_view(),
        name="lfs_manage_taxes",
    ),
    path(
        "tax/<int:pk>/data",
        product_taxes_views.TaxUpdateView.as_view(),
        name="lfs_manage_tax",
    ),
    path(
        "tax/add",
        product_taxes_views.TaxCreateView.as_view(),
        name="lfs_manage_add_tax",
    ),
    path(
        "tax/<int:pk>/delete",
        product_taxes_views.TaxDeleteView.as_view(),
        name="lfs_delete_tax",
    ),
    path(
        "tax/<int:pk>/delete-confirm",
        product_taxes_views.TaxDeleteConfirmView.as_view(),
        name="lfs_manage_delete_tax_confirm",
    ),
    path(
        "taxes/no",
        product_taxes_views.NoTaxesView.as_view(),
        name="lfs_no_taxes",
    ),
    path(
        "no-product-taxes",
        product_taxes_views.NoTaxesView.as_view(),
        name="lfs_manage_no_taxes",
    ),
]
