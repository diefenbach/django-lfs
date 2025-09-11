from django.urls import path
from . import views

urlpatterns = [
    path(
        "property-groups/",
        views.ManagePropertyGroupsView.as_view(),
        name="lfs_manage_property_groups",
    ),
    path(
        "add-property-group/",
        views.PropertyGroupCreateView.as_view(),
        name="lfs_manage_add_property_group",
    ),
    path(
        "no-property-groups/",
        views.NoPropertyGroupsView.as_view(),
        name="lfs_manage_no_property_groups",
    ),
    path(
        "sort-property-groups/",
        views.sort_property_groups,
        name="lfs_manage_sort_property_groups",
    ),
    # Property Group Detail Views
    path(
        "property-group/<int:id>/products/",
        views.PropertyGroupProductsView.as_view(),
        name="lfs_manage_property_group_products",
    ),
    path(
        "property-group/<int:id>/properties/",
        views.PropertyGroupPropertiesView.as_view(),
        name="lfs_manage_property_group_properties",
    ),
    path(
        "property-group/<int:id>/",
        views.PropertyGroupDataView.as_view(),
        name="lfs_manage_property_group",
    ),
    path(
        "delete-property-group/<int:id>/confirm/",
        views.PropertyGroupDeleteConfirmView.as_view(),
        name="lfs_delete_property_group_confirm",
    ),
    path(
        "delete-property-group/<int:id>/",
        views.PropertyGroupDeleteView.as_view(),
        name="lfs_delete_property_group",
    ),
]
