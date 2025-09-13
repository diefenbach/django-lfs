from django.urls import path

import lfs.manage.information.views


urlpatterns = [
    path(
        "environment",
        lfs.manage.information.views.environment,
        name="lfs_manage_environment",
    ),
]
