"""Registration keeps spam bots out without a captcha: a hidden honeypot field that people leave empty, and a signed
time stamp that shows the form was filled in for at least a few seconds. Both apply to the registration on the login
page and in the checkout, which share the form."""

import time

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from lfs.customer.forms import RegisterForm, sign_form_start


@pytest.fixture
def shop(db):
    """The default shop the login pages need."""
    from django.core.management import call_command

    call_command("loaddata", "lfs_shop.xml", verbosity=0)


def registration(email: str = "new@example.com", seconds_ago: float = 10, **extra: str) -> dict[str, str]:
    """Return the POST data of a registration whose form was shown ``seconds_ago``."""
    return {
        "action": "register",
        "email": email,
        "password_1": "secret",
        "password_2": "secret",
        "started": sign_form_start(time.time() - seconds_ago),
        **extra,
    }


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["lfs_login", "lfs_checkout_login"])
def test_a_person_registers(client, shop, url_name: str):
    response = client.post(reverse(url_name), registration())

    assert User.objects.filter(email="new@example.com").exists()
    assert response.status_code == 302


@pytest.mark.django_db
@pytest.mark.parametrize(
    "changes",
    [{"lfs-check": "https://spam.example"}, {"seconds_ago": 1}, {"started": "forged"}, {"started": None}],
    ids=["honeypot filled", "sent too fast", "forged time stamp", "no time stamp"],
)
def test_a_bot_is_refused_and_logged(client, shop, caplog, changes: dict):
    seconds_ago = changes.pop("seconds_ago", 10)
    data = {k: v for k, v in registration(seconds_ago=seconds_ago, **changes).items() if v is not None}

    response = client.post(reverse("lfs_login"), data)

    assert not User.objects.filter(email="new@example.com").exists()
    assert response.status_code == 200
    assert response.context["register_form"].non_field_errors()
    assert any(
        "Registration refused as a bot" in r.getMessage() and "new@example.com" in r.getMessage()
        for r in caplog.records
    )


def test_the_form_renders_the_honeypot_hidden_from_people():
    html = str(RegisterForm())

    assert 'name="lfs-check"' in html
    assert 'tabindex="-1"' in html
    assert 'autocomplete="off"' in html
    assert "captcha" not in html


@pytest.mark.django_db
def test_the_login_page_carries_the_signed_start_time(client, shop, monkeypatch):
    """A person's browser sends back the time stamp the page was rendered with; it must be accepted later."""
    import re

    html = client.get(reverse("lfs_login")).content.decode()
    started = re.search(r'name="started" value="([^"]+)"', html).group(1)
    later = time.time() + 10
    monkeypatch.setattr(time, "time", lambda: later)

    client.post(reverse("lfs_login"), {**registration(), "started": started})

    assert User.objects.filter(email="new@example.com").exists()
