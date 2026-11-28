"""The pages shown when there are no manufacturers or shipping methods yet look like the other empty pages of the
management interface: a Bootstrap button that opens the add form in the modal, not an unstyled form that loads the
modal's content as a page of its own."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    "page,add_url",
    [
        ("lfs_manage_no_manufacturers", "lfs_manage_add_manufacturer"),
        ("lfs_manage_no_shipping_methods", "lfs_manage_add_shipping_method"),
    ],
)
def test_empty_page_opens_the_add_form_in_the_modal(client, admin_user, shop, page: str, add_url: str):
    client.force_login(admin_user)

    content = client.get(reverse(page)).content.decode()

    assert f'hx-get="{reverse(add_url)}"' in content
    assert 'id="modal-body-lg"' in content
    assert 'class="button"' not in content
