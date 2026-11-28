"""The shop settings, tested through real requests as a shop manager: the data (including the logo), the default
values, the order numbers, SEO and portlets. Whether the carousel tab appears is tested in
test_shop_carousel_optional.py."""

import io

import pytest
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from lfs.core.models import Country, Shop
from lfs.core.utils import get_default_shop
from lfs_order_numbers.models import OrderNumberGenerator

pytestmark = pytest.mark.django_db


def png() -> bytes:
    """Return a small PNG image."""
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), "red").save(buffer, "PNG")
    return buffer.getvalue()


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    """Store uploaded files in a temporary folder."""
    settings.MEDIA_ROOT = str(tmp_path)


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def form_data(response, form: str = "form") -> dict:
    """Return the data of the page's form as the browser would send it."""
    f = response.context[form]
    data = {}
    for name in f.fields:
        value = f[name].value()
        if name == "image" or value is None or value is False:
            continue
        data[name] = value
    return data


def shop() -> Shop:
    """Return the shop the views edit; other test folders may leave a shop of their own behind."""
    return get_default_shop()


def test_the_tabs_lead_to_every_setting(manager):
    tabs = manager.get(reverse("lfs_manage_shop_data")).context["tabs"]

    assert [name for name, _ in tabs][:5] == ["data", "default_values", "order_numbers", "seo", "portlets"]


class TestData:
    URL = reverse("lfs_manage_shop_data")

    def test_saves_the_data(self, manager):
        data = form_data(manager.get(self.URL)) | {
            "name": "Lamp shop",
            "notification_emails": "a@example.com, b@example.com",
        }

        response = manager.post(self.URL, data)

        assert (shop().name, shop().get_notification_emails()) == ("Lamp shop", ["a@example.com", "b@example.com"])
        assert response["Location"] == self.URL
        assert messages_of(response) == ["Shop data has been saved."]

    def test_refuses_an_invalid_sender_address(self, manager):
        data = form_data(manager.get(self.URL)) | {"from_email": "not an address"}

        response = manager.post(self.URL, data)

        assert response.context["form"].errors["from_email"]
        assert shop().from_email != "not an address"

    def test_uploads_and_clears_the_logo(self, manager):
        data = form_data(manager.get(self.URL))

        manager.post(self.URL, data | {"image": SimpleUploadedFile("logo.png", png(), content_type="image/png")})
        assert shop().image.name.endswith(".png")

        manager.post(self.URL, data | {"image-clear": "on"})
        assert not shop().image


class TestDefaultValues:
    URL = reverse("lfs_manage_shop_default_values")

    def test_saves_the_countries_and_returns(self, manager):
        austria = Country.objects.create(code="at", name="Austria")
        data = form_data(manager.get(self.URL)) | {
            "invoice_countries": [austria.id],
            "shipping_countries": [austria.id],
            "default_country": austria.id,
            "return_days": 30,
        }

        response = manager.post(self.URL, data)

        assert list(shop().invoice_countries.all()) == [austria]
        assert (shop().default_country, shop().return_days) == (austria, 30)
        assert messages_of(response) == ["Shop default values have been saved."]


class TestOrderNumbers:
    URL = reverse("lfs_manage_shop_order_numbers")

    def test_shows_the_generator_created_on_first_visit(self, manager):
        response = manager.get(self.URL)

        assert response.context["order_numbers_form"].instance == OrderNumberGenerator.objects.get(id="order_number")

    def test_saves_the_last_number_and_the_format(self, manager):
        manager.get(self.URL)

        response = manager.post(self.URL, {"last": 41, "format": "LFS-%05d"})

        assert OrderNumberGenerator.objects.get(id="order_number").get_next() == "LFS-00042"
        assert response["Location"] == self.URL
        assert messages_of(response) == ["Order numbers have been saved."]

    def test_refuses_a_last_number_that_is_not_a_number(self, manager):
        manager.get(self.URL)

        response = manager.post(self.URL, {"last": "many", "format": ""})

        assert OrderNumberGenerator.objects.get(id="order_number").last == 0
        assert messages_of(response) == ["Please correct the indicated errors."]


def test_saves_the_seo_data(manager):
    url = reverse("lfs_manage_shop_seo")

    response = manager.post(url, {"meta_title": "Lamps", "meta_description": "Lamps and more", "meta_keywords": "lamp"})

    assert (shop().meta_title, shop().meta_description, shop().meta_keywords) == ("Lamps", "Lamps and more", "lamp")
    assert response["Location"] == url
    assert messages_of(response) == ["SEO data has been saved."]


def test_shows_the_portlets_tab(manager):
    response = manager.get(reverse("lfs_manage_shop_portlets"))

    assert response.context["active_tab"] == "portlets" and response.context["portlets"]
