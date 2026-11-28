"""The start page of the management interface (/manage/) leads to the dashboard."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_manage_root_shows_the_dashboard(client, admin_user, shop):
    client.force_login(admin_user)

    response = client.get("/manage/", follow=True)

    assert response.redirect_chain == [(reverse("lfs_manage_dashboard"), 302)]
    assert response.status_code == 200
    assert "manage/dashboard/dashboard.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_manage_root_sends_anonymous_users_to_the_login_with_the_dashboard_as_next(client, shop):
    response = client.get("/manage/")
    response = client.get(response["Location"])

    assert response.status_code == 302
    assert response["Location"].startswith("/login/")
    assert "next=" + reverse("lfs_manage_dashboard") in response["Location"]
