from django.urls import path
from lfs.manage.delivery_times import views as delivery_times_views

urlpatterns = [
    path(
        "delivery-times",
        delivery_times_views.ManageDeliveryTimesView.as_view(),
        name="lfs_manage_delivery_times",
    ),
    path(
        "delivery-time/<int:pk>",
        delivery_times_views.DeliveryTimeUpdateView.as_view(),
        name="lfs_manage_delivery_time",
    ),
    path(
        "delivery-time/add",
        delivery_times_views.DeliveryTimeCreateView.as_view(),
        name="lfs_manage_add_delivery_time",
    ),
    path(
        "delivery-time/<int:pk>/delete",
        delivery_times_views.DeliveryTimeDeleteView.as_view(),
        name="lfs_manage_delete_delivery_time",
    ),
    path(
        "delivery-time/<int:pk>/delete-confirm",
        delivery_times_views.DeliveryTimeDeleteConfirmView.as_view(),
        name="lfs_manage_delete_delivery_time_confirm",
    ),
    path(
        "delivery-times/no",
        delivery_times_views.NoDeliveryTimesView.as_view(),
        name="lfs_no_delivery_times",
    ),
]
