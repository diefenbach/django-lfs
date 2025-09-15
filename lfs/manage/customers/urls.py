from django.urls import path
from . import views

urlpatterns = [
    # Customer list views
    path(
        "customers/",
        views.CustomerListView.as_view(),
        name="lfs_manage_customers",
    ),
    path(
        "customers/no",
        views.NoCustomersView.as_view(),
        name="lfs_manage_no_customers",
    ),
    # Individual customer views
    path(
        "customer/<int:customer_id>/",
        views.CustomerDataView.as_view(),
        name="lfs_manage_customer",
    ),
    # Filter and ordering actions
    path(
        "customers/apply-filters/",
        views.ApplyCustomerFiltersView.as_view(),
        name="lfs_manage_apply_customer_filters",
    ),
    path(
        "customers/apply-filters-list/",
        views.ApplyCustomerFiltersView.as_view(),
        name="lfs_manage_apply_customer_filters_list",
    ),
    path(
        "customer/<int:customer_id>/apply-predefined-filter/<str:filter_type>/",
        views.ApplyPredefinedCustomerFilterView.as_view(),
        name="lfs_manage_apply_predefined_customer_filter",
    ),
    path(
        "customers/apply-predefined-filter-list/<str:filter_type>/",
        views.ApplyPredefinedCustomerFilterView.as_view(),
        name="lfs_manage_apply_predefined_customer_filter_list",
    ),
    path(
        "customers/reset-filters/",
        views.ResetCustomerFiltersView.as_view(),
        name="lfs_manage_reset_customer_filters",
    ),
    path(
        "customers/set-ordering/<str:ordering>/",
        views.SetCustomerOrderingView.as_view(),
        name="lfs_manage_set_customer_ordering",
    ),
]
