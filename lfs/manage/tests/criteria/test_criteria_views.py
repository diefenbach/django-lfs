"""The criteria rows of the management (used on shipping and payment methods, their prices and discounts), tested
through real requests as a shop manager: a new row shows the first criterion type, changing the type shows that
type's row, only types listed in LFS_CRITERIA are accepted, and removing a row only removes it from the page."""

import re

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

COUNTRY = "lfs.criteria.models.CountryCriterion"


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def selected_type(html: str) -> str:
    """Return the criterion type selected in a rendered criterion row."""
    return re.search(r'<option selected="selected" value="([^"]+)">', html).group(1)


def test_a_new_row_shows_the_first_criterion_type(manager, settings):
    html = manager.get(reverse("lfs_manage_add_criterion")).content.decode()

    assert selected_type(html) == "lfs.criteria.models.CartPriceCriterion"
    assert re.search(r'name="operator-\d+"', html) and re.search(r'name="value-\d+"', html)


def test_changing_the_type_shows_that_types_row(manager):
    html = manager.post(reverse("lfs_manage_change_criterion_form"), {"type": COUNTRY}).content.decode()

    assert selected_type(html) == COUNTRY


@pytest.mark.parametrize("type_", ["lfs.catalog.models.Product", "os.system", "price", ""])
def test_changing_to_a_type_not_in_lfs_criteria_is_refused(manager, type_: str):
    response = manager.post(reverse("lfs_manage_change_criterion_form"), {"type": type_})

    assert response.status_code == 400


def test_removing_a_row_returns_nothing_for_htmx_to_swap_in(manager):
    response = manager.delete(reverse("lfs_manage_delete_criterion"), HTTP_HX_REQUEST="true")

    assert (response.status_code, response.content) == (200, b"")


def test_removing_a_row_needs_delete(manager):
    assert manager.post(reverse("lfs_manage_delete_criterion")).status_code == 405
