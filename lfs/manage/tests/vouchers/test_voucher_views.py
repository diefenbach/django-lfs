"""The voucher management, tested through real requests as a shop manager: voucher groups (start page, search, add,
save, delete), creating vouchers with generated numbers, filtering and deleting them, and the voucher number
options."""

import datetime

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from lfs.voucher.models import Voucher, VoucherGroup, VoucherOptions
from lfs.voucher.settings import ABSOLUTE, PERCENTAGE

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def xmas(db) -> VoucherGroup:
    """A voucher group."""
    return VoucherGroup.objects.create(name="Xmas", position=10)


def tab(name: str, group: VoucherGroup) -> str:
    """Return the URL of the voucher group tab ``name``."""
    return reverse(name, kwargs={"id": group.id})


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def new_vouchers(**changes) -> dict[str, str]:
    """Return the POST data of the form that creates vouchers."""
    data = {
        "add_vouchers": "1",
        "amount": "3",
        "value": "10",
        "kind_of": str(ABSOLUTE),
        "start_date": "2026-12-01",
        "end_date": "2026-12-31",
        "effective_from": "50",
        "limit": "1",
        "sums_up": "on",
    }
    data.update(changes)
    return data


def voucher(group: VoucherGroup, number: str, **fields) -> Voucher:
    """Create a voucher in ``group``."""
    return Voucher.objects.create(group=group, number=number, kind_of=ABSOLUTE, value=10.0, **fields)


class TestVoucherGroups:
    def test_start_page_opens_a_group(self, manager, xmas):
        assert manager.get(reverse("lfs_manage_voucher_groups"))["Location"] == tab("lfs_manage_voucher_group", xmas)

    def test_start_page_without_groups_shows_the_empty_page(self, manager):
        response = manager.get(reverse("lfs_manage_voucher_groups"))

        assert response["Location"] == reverse("lfs_manage_no_voucher_groups")

    def test_search_filters_the_groups_case_insensitive(self, manager, xmas):
        VoucherGroup.objects.create(name="Easter")

        response = manager.get(tab("lfs_manage_voucher_group", xmas), {"q": "XM"})

        assert list(response.context["voucher_groups"]) == [xmas]

    def test_adds_a_group_with_its_creator(self, manager, admin_user):
        response = manager.post(reverse("lfs_manage_add_voucher_group"), {"name": "Easter"})

        easter = VoucherGroup.objects.get(name="Easter")
        assert easter.creator == admin_user
        assert response["Location"] == tab("lfs_manage_voucher_group", easter)
        assert messages_of(response) == ["Voucher group has been created."]

    def test_saves_the_name(self, manager, xmas):
        response = manager.post(tab("lfs_manage_voucher_group", xmas), {"name": "Christmas"})

        xmas.refresh_from_db()
        assert xmas.name == "Christmas"
        assert messages_of(response) == ["Voucher group has been saved."]


class TestCreatingVouchers:
    def test_creates_the_amount_with_the_entered_values(self, manager, xmas, admin_user):
        response = manager.post(tab("lfs_manage_voucher_group_vouchers", xmas), new_vouchers(kind_of=str(PERCENTAGE)))

        vouchers = list(xmas.vouchers.all())
        assert len(vouchers) == 3
        assert len({v.number for v in vouchers}) == 3
        v = vouchers[0]
        assert (v.kind_of, v.value, v.effective_from, v.limit, v.sums_up, v.creator) == (
            PERCENTAGE,
            10.0,
            50.0,
            1,
            True,
            admin_user,
        )
        assert (v.start_date, v.end_date) == (datetime.date(2026, 12, 1), datetime.date(2026, 12, 31))
        assert messages_of(response) == ["Vouchers have been created."]

    def test_numbers_follow_the_options(self, manager, xmas):
        VoucherOptions.objects.create(number_prefix="X-", number_length=6, number_letters="AB")

        manager.post(tab("lfs_manage_voucher_group_vouchers", xmas), new_vouchers(amount="1"))

        number = xmas.vouchers.get().number
        assert number.startswith("X-") and len(number) == 8 and set(number[2:]) <= {"A", "B"}

    def test_refuses_an_incomplete_form(self, manager, xmas):
        manager.post(tab("lfs_manage_voucher_group_vouchers", xmas), new_vouchers(value=""))

        assert not xmas.vouchers.exists()

    def test_stops_when_the_options_allow_no_more_unique_numbers(self, manager, xmas):
        """One letter and a length of one allow a single number."""
        VoucherOptions.objects.create(number_length=1, number_letters="A")

        response = manager.post(tab("lfs_manage_voucher_group_vouchers", xmas), new_vouchers(amount="3"))

        assert xmas.vouchers.count() == 1
        assert "Unable to create unique Vouchers for the options specified." in messages_of(response)


class TestListingAndDeletingVouchers:
    def listed(self, manager, group, **params) -> list[str]:
        """Return the numbers of the vouchers listed on the group's vouchers tab."""
        return sorted(
            v.number for v in manager.get(tab("lfs_manage_voucher_group_vouchers", group), params).context["vouchers"]
        )

    def test_filters_by_number_and_usage(self, manager, xmas):
        voucher(xmas, "SUMMER1", used_amount=1)
        voucher(xmas, "SUMMER2")
        voucher(xmas, "WINTER")

        assert self.listed(manager, xmas, voucher_search="summer") == ["SUMMER1", "SUMMER2"]
        assert self.listed(manager, xmas, usage_filter="used") == ["SUMMER1"]
        assert self.listed(manager, xmas, usage_filter="unused") == ["SUMMER2", "WINTER"]

    def test_deletes_the_selected_vouchers(self, manager, xmas):
        keep, delete = voucher(xmas, "KEEP"), voucher(xmas, "DELETE")

        response = manager.post(
            tab("lfs_manage_voucher_group_vouchers", xmas), {"delete_vouchers": "1", "voucher-ids": [delete.id]}
        )

        assert list(xmas.vouchers.all()) == [keep]
        assert messages_of(response) == ["1 vouchers have been deleted."]


class TestOptions:
    def test_saves_the_number_options(self, manager, xmas):
        response = manager.post(
            tab("lfs_manage_voucher_group_options", xmas),
            {"number_prefix": "LFS-", "number_suffix": "", "number_length": "7", "number_letters": "XYZ"},
        )

        options = VoucherOptions.objects.get()
        assert (options.number_prefix, options.number_length, options.number_letters) == ("LFS-", 7, "XYZ")
        assert response["Location"] == tab("lfs_manage_voucher_group_options", xmas)
        assert messages_of(response) == ["Voucher options have been saved."]
