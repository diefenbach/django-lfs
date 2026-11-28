"""Every page and action of the management interface is closed to visitors and to customers: they are sent to the
login or refused, and never see or change anything. This replaces one copied ``permission_required`` assertion per
view with a real request against every URL."""

from collections.abc import Iterator

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import URLPattern, URLResolver, reverse
from django.urls.resolvers import RoutePattern

import lfs.manage.urls

# Placeholder values for URL arguments; the permission check runs before any object is looked up.
ARGUMENT_VALUES = {"int": 1}


def manage_urls(patterns: list = lfs.manage.urls.urlpatterns) -> Iterator[str]:
    """Yield the path of every named URL of the management interface, filled with placeholder arguments."""
    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            yield from manage_urls(pattern.url_patterns)
        elif isinstance(pattern, URLPattern) and pattern.name:
            if isinstance(pattern.pattern, RoutePattern):
                kwargs = {
                    name: ARGUMENT_VALUES.get(type(converter).__name__.removesuffix("Converter").lower(), "x")
                    for name, converter in pattern.pattern.converters.items()
                }
            else:
                kwargs = {name: "1" for name in pattern.pattern.regex.groupindex}
            yield reverse(pattern.name, kwargs=kwargs)


URLS = sorted(set(manage_urls()))


def assert_refused(client: Client, method: str, url: str) -> None:
    """Assert that ``method`` on ``url`` sends the visitor to the login or refuses the request. A redirect to
    another management page (such as ``/manage/`` to the dashboard) is followed."""
    response = getattr(client, method)(url)
    while response.status_code == 302 and response["Location"].startswith("/manage/"):
        response = client.get(response["Location"])
    if response.status_code == 302:
        assert "login" in response["Location"], f"{url} redirects to {response['Location']}"
    else:
        assert response.status_code in (401, 403), f"{url} answered {response.status_code}"


def test_there_are_management_urls():
    assert len(URLS) > 100


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["get", "post"])
@pytest.mark.parametrize("url", URLS)
def test_management_url_is_refused_to_anonymous_visitors(client: Client, url: str, method: str):
    assert_refused(client, method, url)


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["get", "post"])
@pytest.mark.parametrize("url", URLS)
def test_management_url_is_refused_to_customers(client: Client, url: str, method: str):
    client.force_login(User.objects.create_user(username="customer", password="x"))

    assert_refused(client, method, url)
