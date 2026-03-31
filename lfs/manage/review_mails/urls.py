# django imports
from django.urls import path

# lfs imports
from . import views

urlpatterns = [
    path(
        "review-mails/",
        views.RatingMailManageView.as_view(),
        name="lfs_manage_rating_mails",
    ),
    path(
        "review-mails/send/",
        views.RatingMailSendView.as_view(),
        name="lfs_send_rating_mails",
    ),
]
