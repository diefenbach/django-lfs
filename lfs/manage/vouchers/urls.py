from django.urls import path
import lfs.manage.vouchers.views

urlpatterns = [
    path(
        "vouchers",
        lfs.manage.vouchers.views.ManageVoucherGroupsView.as_view(),
        name="lfs_manage_voucher_groups",
    ),
    path(
        "voucher-group/<int:id>/data",
        lfs.manage.vouchers.views.VoucherGroupDataView.as_view(),
        name="lfs_manage_voucher_group",
    ),
    path(
        "voucher-group/<int:id>/vouchers",
        lfs.manage.vouchers.views.VoucherGroupVouchersView.as_view(),
        name="lfs_manage_voucher_group_vouchers",
    ),
    path(
        "voucher-group/<int:id>/options",
        lfs.manage.vouchers.views.VoucherGroupOptionsView.as_view(),
        name="lfs_manage_voucher_group_options",
    ),
    path(
        "add-voucher-group",
        lfs.manage.vouchers.views.VoucherGroupCreateView.as_view(),
        name="lfs_manage_add_voucher_group",
    ),
    path(
        "delete-voucher-group-confirm/<int:id>",
        lfs.manage.vouchers.views.VoucherGroupDeleteConfirmView.as_view(),
        name="lfs_manage_delete_voucher_group_confirm",
    ),
    path(
        "delete-voucher-group/<int:id>",
        lfs.manage.vouchers.views.VoucherGroupDeleteView.as_view(),
        name="lfs_delete_voucher_group",
    ),
    path(
        "no-voucher-groups",
        lfs.manage.vouchers.views.NoVoucherGroupsView.as_view(),
        name="lfs_manage_no_voucher_groups",
    ),
]
