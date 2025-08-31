"""
Tests for Voucher views in the manage package.

Following TDD principles:
- Test behavior, not implementation
- Clear test names
- Arrange-Act-Assert structure
- One assertion per test (when practical)
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseRedirect
from decimal import Decimal

from lfs.voucher.models import VoucherGroup, VoucherOptions, Voucher
from lfs.tax.models import Tax
from lfs.manage.voucher.views import (
    VoucherGroupDataView,
    VoucherGroupVouchersView,
    VoucherGroupOptionsView,
    VoucherGroupTabMixin,
    VoucherGroupCreateView,
    ManageVoucherGroupsView,
    VoucherGroupDeleteView,
    NoVoucherGroupsView,
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestVoucherGroupTabMixin:
    """Tests for VoucherGroupTabMixin functionality."""

    def test_get_voucher_group_returns_correct_object(self, voucher_group):
        """Should return the VoucherGroup for given id."""
        mixin = VoucherGroupTabMixin()
        mixin.kwargs = {"id": voucher_group.id}

        result = mixin.get_voucher_group()

        assert result == voucher_group

    def test_get_voucher_group_raises_404_for_nonexistent_id(self):
        """Should raise Http404 for non-existent VoucherGroup id."""
        mixin = VoucherGroupTabMixin()
        mixin.kwargs = {"id": 99999}

        with pytest.raises(Http404):
            mixin.get_voucher_group()

    def test_get_tabs_returns_correct_navigation_urls_without_search(self, voucher_group, rf):
        """Should return list of tab navigation URLs without search parameters."""
        mixin = VoucherGroupTabMixin()
        mixin.request = rf.get("/test/")

        tabs = mixin._get_tabs(voucher_group)

        assert len(tabs) == 3
        assert tabs[0] == ("data", reverse("lfs_manage_voucher_group", args=[voucher_group.pk]))
        assert tabs[1] == ("vouchers", reverse("lfs_manage_voucher_group_vouchers", args=[voucher_group.pk]))
        assert tabs[2] == ("options", reverse("lfs_manage_voucher_group_options", args=[voucher_group.pk]))

    def test_get_tabs_returns_correct_navigation_urls_with_search(self, voucher_group, rf):
        """Should return list of tab navigation URLs with search parameters."""
        mixin = VoucherGroupTabMixin()
        mixin.request = rf.get("/test/?q=search_term")

        tabs = mixin._get_tabs(voucher_group)

        expected_data_url = reverse("lfs_manage_voucher_group", args=[voucher_group.pk]) + "?q=search_term"
        expected_vouchers_url = reverse("lfs_manage_voucher_group_vouchers", args=[voucher_group.pk]) + "?q=search_term"
        expected_options_url = reverse("lfs_manage_voucher_group_options", args=[voucher_group.pk]) + "?q=search_term"

        assert tabs[0] == ("data", expected_data_url)
        assert tabs[1] == ("vouchers", expected_vouchers_url)
        assert tabs[2] == ("options", expected_options_url)

    def test_get_voucher_groups_queryset_returns_all_groups_without_search(self, multiple_voucher_groups, rf):
        """Should return all voucher groups when no search query."""
        mixin = VoucherGroupTabMixin()
        mixin.request = rf.get("/test/")

        queryset = mixin.get_voucher_groups_queryset()

        assert queryset.count() == 3
        assert list(queryset) == list(VoucherGroup.objects.all().order_by("name"))

    def test_get_voucher_groups_queryset_filters_by_search_query(self, multiple_voucher_groups, rf):
        """Should filter voucher groups by search query."""
        mixin = VoucherGroupTabMixin()
        mixin.request = rf.get("/test/?q=Group 1")

        queryset = mixin.get_voucher_groups_queryset()

        assert queryset.count() == 1
        assert queryset.first().name == "Group 1"

    def test_get_voucher_groups_queryset_case_insensitive_search(self, multiple_voucher_groups, rf):
        """Should perform case-insensitive search."""
        mixin = VoucherGroupTabMixin()
        mixin.request = rf.get("/test/?q=group")

        queryset = mixin.get_voucher_groups_queryset()

        assert queryset.count() == 3  # All groups contain "group" (case-insensitive)


@pytest.mark.django_db
@pytest.mark.unit
class TestVoucherGroupDataView:
    """Tests for VoucherGroupDataView."""

    def test_view_uses_correct_template(self):
        """Should use the correct template."""
        view = VoucherGroupDataView()
        assert view.template_name == "manage/voucher/voucher_group.html"

    def test_view_uses_correct_model(self):
        """Should use VoucherGroup model."""
        view = VoucherGroupDataView()
        assert view.model == VoucherGroup

    def test_view_has_correct_tab_name(self):
        """Should have 'data' as tab name."""
        view = VoucherGroupDataView()
        assert view.tab_name == "data"

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = VoucherGroupDataView()
        assert view.permission_required == "core.manage_shop"

    def test_get_success_url_returns_data_tab_url(self, voucher_group):
        """Should return URL to data tab after successful save."""
        view = VoucherGroupDataView()
        view.object = voucher_group

        success_url = view.get_success_url()

        expected_url = reverse("lfs_manage_voucher_group", kwargs={"id": voucher_group.pk})
        assert success_url == expected_url


@pytest.mark.django_db
@pytest.mark.unit
class TestVoucherGroupVouchersView:
    """Tests for VoucherGroupVouchersView."""

    def test_view_uses_correct_template(self):
        """Should use the correct template."""
        view = VoucherGroupVouchersView()
        assert view.template_name == "manage/voucher/voucher_group.html"

    def test_view_has_correct_tab_name(self):
        """Should have 'vouchers' as tab name."""
        view = VoucherGroupVouchersView()
        assert view.tab_name == "vouchers"

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = VoucherGroupVouchersView()
        assert view.permission_required == "core.manage_shop"

    def test_get_success_url_returns_vouchers_tab_url(self, voucher_group):
        """Should return URL to vouchers tab after successful operation."""
        view = VoucherGroupVouchersView()
        view.kwargs = {"id": voucher_group.id}

        success_url = view.get_success_url()

        expected_url = reverse("lfs_manage_voucher_group_vouchers", kwargs={"id": voucher_group.id})
        assert success_url == expected_url

    def test_get_context_data_includes_vouchers_and_taxes(self, voucher_group, rf, manage_user):
        """Should include vouchers and taxes in context."""
        # Create test data
        tax = Tax.objects.create(rate=Decimal("19.00"))
        voucher = Voucher.objects.create(
            number="TEST123", group=voucher_group, creator=manage_user, kind_of=0, value=Decimal("25.00")
        )

        view = VoucherGroupVouchersView()
        view.request = rf.get("/test/")
        view.kwargs = {"id": voucher_group.id}

        context = view.get_context_data()

        assert "vouchers" in context
        assert "taxes" in context
        assert voucher in context["vouchers"]
        assert tax in context["taxes"]

    def test_get_context_data_filters_vouchers_by_search(self, voucher_group, rf, manage_user):
        """Should filter vouchers by search query."""
        # Create test vouchers
        voucher1 = Voucher.objects.create(
            number="SEARCH123", group=voucher_group, creator=manage_user, kind_of=0, value=Decimal("25.00")
        )
        voucher2 = Voucher.objects.create(
            number="OTHER456", group=voucher_group, creator=manage_user, kind_of=0, value=Decimal("25.00")
        )

        view = VoucherGroupVouchersView()
        view.request = rf.get("/test/?voucher_search=SEARCH")
        view.kwargs = {"id": voucher_group.id}

        context = view.get_context_data()

        assert voucher1 in context["vouchers"]
        assert voucher2 not in context["vouchers"]
        assert context["voucher_search"] == "SEARCH"

    def test_get_context_data_filters_vouchers_by_usage_status_used(self, voucher_group, rf, manage_user):
        """Should filter vouchers by used status."""
        # Create test vouchers
        used_voucher = Voucher.objects.create(
            number="USED123",
            group=voucher_group,
            creator=manage_user,
            kind_of=0,
            value=Decimal("25.00"),
            used_amount=Decimal("25.00"),
        )
        unused_voucher = Voucher.objects.create(
            number="UNUSED456", group=voucher_group, creator=manage_user, kind_of=0, value=Decimal("25.00")
        )

        view = VoucherGroupVouchersView()
        view.request = rf.get("/test/?usage_filter=used")
        view.kwargs = {"id": voucher_group.id}

        context = view.get_context_data()

        assert used_voucher in context["vouchers"]
        assert unused_voucher not in context["vouchers"]
        assert context["usage_filter"] == "used"

    def test_get_context_data_filters_vouchers_by_usage_status_unused(self, voucher_group, rf, manage_user):
        """Should filter vouchers by unused status."""
        # Create test vouchers
        used_voucher = Voucher.objects.create(
            number="USED123",
            group=voucher_group,
            creator=manage_user,
            kind_of=0,
            value=Decimal("25.00"),
            used_amount=Decimal("25.00"),
        )
        unused_voucher = Voucher.objects.create(
            number="UNUSED456", group=voucher_group, creator=manage_user, kind_of=0, value=Decimal("25.00")
        )

        view = VoucherGroupVouchersView()
        view.request = rf.get("/test/?usage_filter=unused")
        view.kwargs = {"id": voucher_group.id}

        context = view.get_context_data()

        assert used_voucher not in context["vouchers"]
        assert unused_voucher in context["vouchers"]
        assert context["usage_filter"] == "unused"


@pytest.mark.django_db
@pytest.mark.unit
class TestVoucherGroupOptionsView:
    """Tests for VoucherGroupOptionsView."""

    def test_view_uses_correct_model(self):
        """Should use VoucherOptions model."""
        view = VoucherGroupOptionsView()
        assert view.model == VoucherOptions

    def test_view_has_correct_tab_name(self):
        """Should have 'options' as tab name."""
        view = VoucherGroupOptionsView()
        assert view.tab_name == "options"

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = VoucherGroupOptionsView()
        assert view.permission_required == "core.manage_shop"

    def test_get_object_returns_existing_options(self):
        """Should return existing VoucherOptions object."""
        existing_options = VoucherOptions.objects.create(number_prefix="TEST-")
        view = VoucherGroupOptionsView()

        result = view.get_object()

        assert result == existing_options

    def test_get_object_creates_options_if_none_exist(self):
        """Should create VoucherOptions if none exist."""
        view = VoucherGroupOptionsView()

        result = view.get_object()

        assert isinstance(result, VoucherOptions)
        assert VoucherOptions.objects.count() == 1

    def test_get_success_url_returns_options_tab_url(self, voucher_group):
        """Should return URL to options tab after successful save."""
        view = VoucherGroupOptionsView()
        view.kwargs = {"id": voucher_group.id}

        success_url = view.get_success_url()

        expected_url = reverse("lfs_manage_voucher_group_options", kwargs={"id": voucher_group.id})
        assert success_url == expected_url


@pytest.mark.django_db
@pytest.mark.unit
class TestManageVoucherGroupsView:
    """Tests for ManageVoucherGroupsView."""

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = ManageVoucherGroupsView()
        assert view.permission_required == "core.manage_shop"

    def test_get_redirect_url_redirects_to_first_voucher_group(self, multiple_voucher_groups):
        """Should redirect to first voucher group when groups exist."""
        view = ManageVoucherGroupsView()

        redirect_url = view.get_redirect_url()

        first_group = VoucherGroup.objects.all().order_by("name")[0]
        expected_url = reverse("lfs_manage_voucher_group", kwargs={"id": first_group.id})
        assert redirect_url == expected_url

    def test_get_redirect_url_redirects_to_no_groups_when_none_exist(self):
        """Should redirect to no groups view when no groups exist."""
        view = ManageVoucherGroupsView()

        redirect_url = view.get_redirect_url()

        expected_url = reverse("lfs_manage_no_voucher_groups")
        assert redirect_url == expected_url


@pytest.mark.django_db
@pytest.mark.unit
class TestNoVoucherGroupsView:
    """Tests for NoVoucherGroupsView."""

    def test_view_uses_correct_template(self):
        """Should use the correct template."""
        view = NoVoucherGroupsView()
        assert view.template_name == "manage/voucher/no_voucher_groups.html"

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = NoVoucherGroupsView()
        assert view.permission_required == "core.manage_shop"


@pytest.mark.django_db
@pytest.mark.unit
class TestVoucherGroupCreateView:
    """Tests for VoucherGroupCreateView."""

    def test_view_uses_correct_model(self):
        """Should use VoucherGroup model."""
        view = VoucherGroupCreateView()
        assert view.model == VoucherGroup

    def test_view_uses_correct_template(self):
        """Should use the correct template."""
        view = VoucherGroupCreateView()
        assert view.template_name == "manage/voucher/add_voucher_group.html"

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = VoucherGroupCreateView()
        assert view.permission_required == "core.manage_shop"

    def test_get_success_url_returns_voucher_group_url(self, voucher_group):
        """Should return URL to voucher group after successful creation."""
        view = VoucherGroupCreateView()
        view.object = voucher_group

        success_url = view.get_success_url()

        expected_url = reverse("lfs_manage_voucher_group", kwargs={"id": voucher_group.id})
        assert success_url == expected_url


@pytest.mark.django_db
@pytest.mark.unit
class TestVoucherGroupDeleteView:
    """Tests for VoucherGroupDeleteView."""

    def test_view_uses_correct_model(self):
        """Should use VoucherGroup model."""
        view = VoucherGroupDeleteView()
        assert view.model == VoucherGroup

    def test_view_requires_permission(self):
        """Should require 'core.manage_shop' permission."""
        view = VoucherGroupDeleteView()
        assert view.permission_required == "core.manage_shop"

    def test_post_deletes_voucher_group_and_redirects(self, request_factory, voucher_group, monkeypatch):
        """Should delete voucher group and redirect with success message."""
        request = request_factory.post("/")

        view = VoucherGroupDeleteView()
        view.request = request
        view.kwargs = {"id": voucher_group.id}

        def mock_messages_success(request, message):
            pass  # Mock the messages.success call

        monkeypatch.setattr("lfs.manage.voucher.views.messages.success", mock_messages_success)

        response = view.post(request)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse("lfs_manage_voucher_groups")


@pytest.mark.django_db
@pytest.mark.integration
class TestVoucherViewsIntegration:
    """Integration tests for voucher views."""

    def test_voucher_group_data_view_get_request(self, client, manage_user, voucher_group, shop):
        """Should render voucher group data view successfully."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_voucher_group", kwargs={"id": voucher_group.id})

        response = client.get(url)

        assert response.status_code == 200
        assert "voucher_group" in response.context
        assert response.context["voucher_group"] == voucher_group
        assert response.context["active_tab"] == "data"

    def test_voucher_group_vouchers_view_get_request(self, client, manage_user, voucher_group, shop):
        """Should render voucher group vouchers view successfully."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_voucher_group_vouchers", kwargs={"id": voucher_group.id})

        response = client.get(url)

        assert response.status_code == 200
        assert "voucher_group" in response.context
        assert response.context["voucher_group"] == voucher_group
        assert response.context["active_tab"] == "vouchers"
        assert "vouchers" in response.context
        assert "taxes" in response.context

    def test_voucher_group_options_view_get_request(self, client, manage_user, voucher_group, shop):
        """Should render voucher group options view successfully."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_voucher_group_options", kwargs={"id": voucher_group.id})

        response = client.get(url)

        assert response.status_code == 200
        assert "voucher_group" in response.context
        assert response.context["voucher_group"] == voucher_group
        assert response.context["active_tab"] == "options"

    def test_manage_voucher_groups_redirects_to_first_group(self, client, manage_user, voucher_group, shop):
        """Should redirect to first voucher group."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_voucher_groups")

        response = client.get(url)

        expected_url = reverse("lfs_manage_voucher_group", kwargs={"id": voucher_group.id})
        assert response.status_code == 302
        assert response.url == expected_url

    def test_manage_voucher_groups_redirects_to_no_groups_when_empty(self, client, manage_user, shop):
        """Should redirect to no groups view when no groups exist."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_voucher_groups")

        response = client.get(url)

        expected_url = reverse("lfs_manage_no_voucher_groups")
        assert response.status_code == 302
        assert response.url == expected_url

    def test_no_voucher_groups_view_renders_correctly(self, client, manage_user, shop):
        """Should render no voucher groups view successfully."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_no_voucher_groups")

        response = client.get(url)

        assert response.status_code == 200

    def test_add_voucher_group_view_get_request(self, client, manage_user, shop):
        """Should render add voucher group form successfully."""
        client.force_login(manage_user)
        url = reverse("lfs_manage_add_voucher_group")

        response = client.get(url)

        assert response.status_code == 200
        assert "form" in response.context

    def test_voucher_views_require_authentication(self, client, voucher_group):
        """Should require authentication for all voucher views."""
        urls = [
            reverse("lfs_manage_voucher_groups"),
            reverse("lfs_manage_voucher_group", kwargs={"id": voucher_group.id}),
            reverse("lfs_manage_voucher_group_vouchers", kwargs={"id": voucher_group.id}),
            reverse("lfs_manage_voucher_group_options", kwargs={"id": voucher_group.id}),
            reverse("lfs_manage_add_voucher_group"),
            reverse("lfs_manage_no_voucher_groups"),
        ]

        for url in urls:
            response = client.get(url)
            # Should redirect to login or return 403/401
            assert response.status_code in [302, 403, 401]
