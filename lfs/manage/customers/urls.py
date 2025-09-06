from django.urls import path
from . import views

urlpatterns = [
    # Customer list views
    path("", views.CustomerListView.as_view(), name="lfs_manage_customers"),
    path("no-customers/", views.NoCustomersView.as_view(), name="lfs_manage_no_customers"),
    # Individual customer views
    path("<int:customer_id>/", views.CustomerDataView.as_view(), name="lfs_manage_customer"),
    # Filter and ordering actions
    path("apply-filters/", views.ApplyCustomerFiltersView.as_view(), name="lfs_apply_customer_filters"),
    path("apply-filters-list/", views.ApplyCustomerFiltersView.as_view(), name="lfs_apply_customer_filters_list"),
    path(
        "<int:customer_id>/apply-predefined-filter/<str:filter_type>/",
        views.ApplyPredefinedCustomerFilterView.as_view(),
        name="lfs_apply_predefined_customer_filter",
    ),
    path(
        "apply-predefined-filter-list/<str:filter_type>/",
        views.ApplyPredefinedCustomerFilterView.as_view(),
        name="lfs_apply_predefined_customer_filter_list",
    ),
    path("reset-filters/", views.ResetCustomerFiltersView.as_view(), name="lfs_reset_customer_filters"),
    path("set-ordering/<str:ordering>/", views.SetCustomerOrderingView.as_view(), name="lfs_set_customer_ordering"),
]
