from django.urls import path
import lfs.manage.discounts.views

urlpatterns = [
    path(
        "discounts/",
        lfs.manage.discounts.views.ManageDiscountsView.as_view(),
        name="lfs_manage_discounts",
    ),
    path(
        "discount/<int:id>/data",
        lfs.manage.discounts.views.DiscountDataView.as_view(),
        name="lfs_manage_discount",
    ),
    path(
        "discount/<int:id>/criteria/",
        lfs.manage.discounts.views.DiscountCriteriaView.as_view(),
        name="lfs_manage_discount_criteria",
    ),
    path(
        "discount/<int:id>/products/",
        lfs.manage.discounts.views.DiscountProductsView.as_view(),
        name="lfs_manage_discount_products",
    ),
    path(
        "discount/add",
        lfs.manage.discounts.views.DiscountCreateView.as_view(),
        name="lfs_manage_add_discount",
    ),
    path(
        "discount/<int:id>/delete-confirm",
        lfs.manage.discounts.views.DiscountDeleteConfirmView.as_view(),
        name="lfs_manage_delete_discount_confirm",
    ),
    path(
        "discount/<int:id>/delete",
        lfs.manage.discounts.views.DiscountDeleteView.as_view(),
        name="lfs_manage_delete_discount",
    ),
    path(
        "discounts/no",
        lfs.manage.discounts.views.NoDiscountsView.as_view(),
        name="lfs_manage_no_discounts",
    ),
]
