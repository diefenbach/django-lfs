"""lfs_init sets up a new shop: slots for portlets but no portlets, since the theme navigates with menus, and PayPal
only when lfs_paypal is installed."""

import pytest
from django.core.management import call_command
from portlets.models import PortletAssignment, Slot

from lfs.core.utils import import_symbol
from lfs.payment.models import PaymentMethod


@pytest.mark.django_db
def test_lfs_init_creates_the_slots_but_assigns_no_portlets():
    call_command("lfs_init")

    assert sorted(Slot.objects.values_list("name", flat=True)) == ["Left", "Right"]
    assert PortletAssignment.objects.count() == 0


@pytest.mark.django_db
def test_lfs_init_offers_paypal_when_lfs_paypal_is_installed(settings):
    if "lfs_paypal" not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = [*settings.INSTALLED_APPS, "lfs_paypal"]
    call_command("lfs_init")

    paypal = PaymentMethod.objects.get(name="PayPal")
    assert import_symbol(paypal.module).__name__ == "PayPalProcessor"


@pytest.mark.django_db
def test_lfs_init_offers_no_paypal_without_lfs_paypal(settings):
    settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != "lfs_paypal"]
    call_command("lfs_init")

    assert not PaymentMethod.objects.filter(name="PayPal").exists()
    assert PaymentMethod.objects.filter(name="Prepayment").exists()
