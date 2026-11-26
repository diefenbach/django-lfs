"""lfs_init sets up a new shop: slots for portlets, but no portlets, since the theme navigates with menus."""

import pytest
from django.core.management import call_command
from portlets.models import PortletAssignment, Slot


@pytest.mark.django_db
def test_lfs_init_creates_the_slots_but_assigns_no_portlets():
    call_command("lfs_init")

    assert sorted(Slot.objects.values_list("name", flat=True)) == ["Left", "Right"]
    assert PortletAssignment.objects.count() == 0
