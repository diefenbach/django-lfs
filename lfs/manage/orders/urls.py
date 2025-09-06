from django.urls import path, re_path
import lfs.manage.orders.views

urlpatterns = [
    re_path(r"^manage-orders$", lfs.manage.orders.views.manage_orders, name="lfs_manage_orders"),
    re_path(r"^orders$", lfs.manage.orders.views.orders_view, name="lfs_orders"),
    # Inline endpoints no longer used after clean cut; keep temporarily for compatibility if referenced
    re_path(r"^order/(?P<order_id>\d*)$", lfs.manage.orders.views.order_view, name="lfs_manage_order"),
    re_path(
        r"^delete-order/(?P<order_id>\d*)$", lfs.manage.orders.views.OrderDeleteView.as_view(), name="lfs_delete_order"
    ),
    re_path(r"^send-order/(?P<order_id>\d*)$", lfs.manage.orders.views.send_order, name="lfs_send_order"),
    # Order filters (class-based equivalents wired through function delegations for now)
    path("set-orders-filter", lfs.manage.orders.views.ApplyOrderFiltersView.as_view(), name="lfs_set_order_filter"),
    path(
        "set-orders-filter-date/<str:filter_type>",
        lfs.manage.orders.views.ApplyPredefinedOrderFilterView.as_view(),
        name="lfs_apply_predefined_order_filter",
    ),
    path("reset-order-filter", lfs.manage.orders.views.ResetOrderFiltersView.as_view(), name="lfs_reset_order_filters"),
    # Deprecated: inline pagination endpoints removed in clean cut
    re_path(r"^change-order-state$", lfs.manage.orders.views.change_order_state, name="lfs_change_order_state"),
]
