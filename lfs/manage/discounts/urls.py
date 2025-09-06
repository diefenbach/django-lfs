from django.urls import path
import lfs.manage.discounts.views

urlpatterns = [
    path("discounts/", lfs.manage.discounts.views.ManageDiscountsView.as_view(), name="lfs_manage_discounts"),
    path("discount/<int:id>/", lfs.manage.discounts.views.DiscountDataView.as_view(), name="lfs_manage_discount"),
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
    path("add-discount/", lfs.manage.discounts.views.DiscountCreateView.as_view(), name="lfs_manage_add_discount"),
    path(
        "delete-discount-confirm/<int:id>/",
        lfs.manage.discounts.views.DiscountDeleteConfirmView.as_view(),
        name="lfs_manage_delete_discount_confirm",
    ),
    path(
        "delete-discount/<int:id>/",
        lfs.manage.discounts.views.DiscountDeleteView.as_view(),
        name="lfs_manage_delete_discount",
    ),
    path("no-discounts/", lfs.manage.discounts.views.NoDiscountsView.as_view(), name="lfs_manage_no_discounts"),
]
