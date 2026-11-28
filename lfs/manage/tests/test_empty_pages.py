"""The pages shown when there are no manufacturers, shipping methods or properties yet open the add form in the modal,
like the other empty pages of the management interface, instead of loading the modal's content as an unstyled page of
its own."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    "page,add_url",
    [
        ("lfs_manage_no_manufacturers", "lfs_manage_add_manufacturer"),
        ("lfs_manage_no_shipping_methods", "lfs_manage_add_shipping_method"),
        ("lfs_manage_no_properties", "lfs_add_property"),
    ],
)
def test_empty_page_opens_the_add_form_in_the_modal(client, admin_user, shop, page: str, add_url: str):
    client.force_login(admin_user)

    content = client.get(reverse(page)).content.decode()

    assert f'hx-get="{reverse(add_url)}"' in content
    assert 'id="modal-body-lg"' in content
    assert 'class="button"' not in content
