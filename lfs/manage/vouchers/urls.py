from django.urls import re_path
import lfs.manage.vouchers.views

urlpatterns = [
    re_path(
        r"^vouchers$",
        lfs.manage.vouchers.views.ManageVoucherGroupsView.as_view(),
        name="lfs_manage_voucher_groups",
    ),
    re_path(
        r"^voucher-group/(?P<id>\d+)$",
        lfs.manage.vouchers.views.VoucherGroupDataView.as_view(),
        name="lfs_manage_voucher_group",
    ),
    re_path(
        r"^voucher-group/(?P<id>\d+)/vouchers$",
        lfs.manage.vouchers.views.VoucherGroupVouchersView.as_view(),
        name="lfs_manage_voucher_group_vouchers",
    ),
    re_path(
        r"^voucher-group/(?P<id>\d+)/options$",
        lfs.manage.vouchers.views.VoucherGroupOptionsView.as_view(),
        name="lfs_manage_voucher_group_options",
    ),
    re_path(
        r"^add-voucher-group$",
        lfs.manage.vouchers.views.VoucherGroupCreateView.as_view(),
        name="lfs_manage_add_voucher_group",
    ),
    re_path(
        r"^delete-voucher-group-confirm/(?P<id>\d+)$",
        lfs.manage.vouchers.views.VoucherGroupDeleteConfirmView.as_view(),
        name="lfs_manage_delete_voucher_group_confirm",
    ),
    re_path(
        r"^delete-voucher-group/(?P<id>\d+)$",
        lfs.manage.vouchers.views.VoucherGroupDeleteView.as_view(),
        name="lfs_delete_voucher_group",
    ),
    re_path(
        r"^no-voucher-groups$",
        lfs.manage.vouchers.views.NoVoucherGroupsView.as_view(),
        name="lfs_manage_no_voucher_groups",
    ),
]
