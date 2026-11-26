"""Action links (footer, tabs): absolute URLs, paths within the shop, and mailto: are stored; unsafe ones are not.

Saved through the real edit view of the management interface, checking what ends up in the database.
"""

import pytest
from django.urls import reverse

from lfs.core.models import Action, ActionGroup


@pytest.fixture
def action(db):
    group = ActionGroup.objects.create(name="Footer")
    return Action.objects.create(group=group, title="Imprint", link="https://example.com/old", active=True)


def save_link(client, action, link):
    client.post(reverse("lfs_manage_action", kwargs={"pk": action.pk}), {"title": "Imprint", "link": link, "active": "on"})
    action.refresh_from_db()
    return action.link


@pytest.mark.parametrize(
    "link",
    [
        "https://example.com/terms",
        "http://example.com/path?query=value",
        "/page/imprint",
        "/page/imprint/#contact",
        "mailto:shop@example.com",
    ],
)
def test_valid_link_is_stored(admin_client, action, link):
    assert save_link(admin_client, action, link) == link


@pytest.mark.parametrize(
    "link",
    [
        "javascript:alert(1)",  # runs script on click
        "//evil.example.com/",  # browsers treat it as another site
        "/\\evil.example.com/",  # browsers read the backslash as a slash: another site
        "/\t/evil.example.com/",  # browsers drop the tab: another site
        "/page/imp rint",  # whitespace inside a link
        "page/imprint",  # relative to the current page, breaks on every other page
        "mailto:",  # no address
        "mailto:not-an-address",
        "ftp://example.com/file",  # not a web or mail link
        "",
    ],
)
def test_invalid_link_is_rejected_and_the_old_one_kept(admin_client, action, link):
    assert save_link(admin_client, action, link) == "https://example.com/old"
