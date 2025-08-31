from typing import Dict, List, Tuple, Any, Optional

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, FormView, CreateView, DeleteView, RedirectView, TemplateView

import lfs.core.utils
import lfs.voucher.utils
from lfs.manage.mixins import DirectDeleteMixin
from lfs.tax.models import Tax
from lfs.voucher.models import Voucher
from lfs.voucher.models import VoucherGroup
from lfs.voucher.models import VoucherOptions
from lfs.manage.voucher.forms import VoucherForm
from lfs.manage.voucher.forms import VoucherGroupAddForm
from lfs.manage.voucher.forms import VoucherOptionsForm


class ManageVoucherGroupsView(PermissionRequiredMixin, RedirectView):
    """Dispatches to the first voucher group or to the add voucher group form."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        try:
            vg = VoucherGroup.objects.all().order_by("name")[0]
            return reverse("lfs_manage_voucher_group", kwargs={"id": vg.id})
        except IndexError:
            return reverse("lfs_manage_no_voucher_groups")


class NoVoucherGroupsView(PermissionRequiredMixin, TemplateView):
    """Displays that no voucher groups exist."""

    permission_required = "core.manage_shop"
    template_name = "manage/voucher/no_voucher_groups.html"


class VoucherGroupTabMixin:
    """Mixin for tab navigation in VoucherGroup views."""

    template_name = "manage/voucher/voucher_group.html"
    tab_name: Optional[str] = None

    def get_voucher_group(self) -> VoucherGroup:
        """Gets the VoucherGroup object."""
        return get_object_or_404(VoucherGroup, pk=self.kwargs["id"])

    def get_voucher_groups_queryset(self):
        """Returns filtered VoucherGroups based on search parameter."""
        queryset = VoucherGroup.objects.all().order_by("name")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with tab navigation and VoucherGroup."""
        ctx = super().get_context_data(**kwargs)
        voucher_group = getattr(self, "object", None) or self.get_voucher_group()

        ctx.update(
            {
                "voucher_group": voucher_group,
                "voucher_groups": self.get_voucher_groups_queryset(),
                "search_query": self.request.GET.get("q", ""),
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(voucher_group),
            }
        )
        return ctx

    def _get_tabs(self, voucher_group: VoucherGroup) -> List[Tuple[str, str]]:
        """Creates tab navigation URLs with search parameter."""
        search_query = self.request.GET.get("q", "").strip()

        data_url = reverse("lfs_manage_voucher_group", args=[voucher_group.pk])
        vouchers_url = reverse("lfs_manage_voucher_group_vouchers", args=[voucher_group.pk])
        options_url = reverse("lfs_manage_voucher_group_options", args=[voucher_group.pk])

        # Add search parameter if present
        if search_query:
            from urllib.parse import urlencode

            query_params = urlencode({"q": search_query})
            data_url += "?" + query_params
            vouchers_url += "?" + query_params
            options_url += "?" + query_params

        return [
            ("data", data_url),
            ("vouchers", vouchers_url),
            ("options", options_url),
        ]


class VoucherGroupDataView(PermissionRequiredMixin, VoucherGroupTabMixin, UpdateView):
    """View for data tab of a VoucherGroup."""

    model = VoucherGroup
    fields = ["name"]
    tab_name = "data"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the data tab after successful save."""
        return reverse("lfs_manage_voucher_group", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        response = super().form_valid(form)
        messages.success(self.request, _("Voucher group has been saved."))
        return response


class VoucherGroupVouchersView(PermissionRequiredMixin, VoucherGroupTabMixin, FormView):
    """View for vouchers tab of a VoucherGroup."""

    tab_name = "vouchers"
    template_name = "manage/voucher/voucher_group.html"
    permission_required = "core.manage_shop"
    form_class = VoucherForm

    def get_voucher_group(self) -> VoucherGroup:
        """Overrides to use id from kwargs."""
        return get_object_or_404(VoucherGroup, pk=self.kwargs["id"])

    def get_success_url(self) -> str:
        """Stays on the vouchers tab."""
        return reverse("lfs_manage_voucher_group_vouchers", kwargs={"id": self.kwargs["id"]})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles voucher operations (add/delete)."""
        if "add_vouchers" in request.POST:
            return self._handle_add_vouchers(request)
        elif "delete_vouchers" in request.POST:
            return self._handle_delete_vouchers(request)

        return super().post(request, *args, **kwargs)

    def _handle_add_vouchers(self, request: HttpRequest) -> HttpResponse:
        """Handles adding vouchers."""
        voucher_group = self.get_voucher_group()
        form = VoucherForm(data=request.POST)

        if form.is_valid():
            try:
                amount = int(request.POST.get("amount", 0))
            except (TypeError, ValueError):
                amount = 0

            created_count = 0
            for i in range(amount):
                number = lfs.voucher.utils.create_voucher_number()
                counter = 0
                while Voucher.objects.filter(number=number).exists() and counter < 100:
                    number = lfs.voucher.utils.create_voucher_number()
                    counter += 1

                if counter == 100:
                    messages.error(self.request, _("Unable to create unique Vouchers for the options specified."))
                    break

                Voucher.objects.create(
                    number=number,
                    group=voucher_group,
                    creator=request.user,
                    kind_of=request.POST.get("kind_of", 0),
                    value=request.POST.get("value", 0.0),
                    start_date=request.POST.get("start_date") or None,
                    end_date=request.POST.get("end_date") or None,
                    effective_from=request.POST.get("effective_from") or None,
                    tax_id=request.POST.get("tax") or None,
                    limit=request.POST.get("limit") or None,
                    sums_up=bool(request.POST.get("sums_up")),
                )
                created_count += 1

            if created_count > 0:
                messages.success(self.request, _("Vouchers have been created."))

        return HttpResponseRedirect(self.get_success_url())

    def _handle_delete_vouchers(self, request: HttpRequest) -> HttpResponse:
        """Handles deleting vouchers."""
        voucher_ids = request.POST.getlist("voucher-ids")
        if voucher_ids:
            vouchers = Voucher.objects.filter(pk__in=voucher_ids)
            count = vouchers.count()
            vouchers.delete()
            messages.success(self.request, _("%(count)d vouchers have been deleted.") % {"count": count})

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with vouchers and taxes."""
        ctx = super().get_context_data(**kwargs)
        voucher_group = self.get_voucher_group()

        # Filter vouchers based on search and usage status
        vouchers = voucher_group.vouchers.all()

        # Search filter
        search_query = self.request.GET.get("voucher_search", "").strip()
        if search_query:
            vouchers = vouchers.filter(number__icontains=search_query)

        # Usage status filter
        usage_filter = self.request.GET.get("usage_filter", "").strip()
        if usage_filter == "used":
            vouchers = vouchers.filter(used_amount__gt=0)
        elif usage_filter == "unused":
            vouchers = vouchers.filter(used_amount__isnull=True) | vouchers.filter(used_amount=0)

        ctx.update(
            {
                "voucher_group": voucher_group,
                "vouchers": vouchers,
                "taxes": Tax.objects.all(),
                "voucher_search": search_query,
                "usage_filter": usage_filter,
            }
        )
        return ctx


class VoucherGroupOptionsView(PermissionRequiredMixin, VoucherGroupTabMixin, UpdateView):
    """View for options tab - global voucher options."""

    model = VoucherOptions
    form_class = VoucherOptionsForm
    tab_name = "options"
    permission_required = "core.manage_shop"

    def get_object(self, queryset=None):
        """Gets or creates the global VoucherOptions object."""
        try:
            return VoucherOptions.objects.all()[0]
        except IndexError:
            return VoucherOptions.objects.create()

    def get_success_url(self) -> str:
        """Stays on the options tab."""
        return reverse("lfs_manage_voucher_group_options", kwargs={"id": self.kwargs["id"]})

    def form_valid(self, form):
        """Saves and shows success message."""
        response = super().form_valid(form)
        messages.success(self.request, _("Voucher options have been saved."))
        return response

    def get_context_data(self, **kwargs):
        """Override to ensure correct voucher_group context."""
        ctx = super().get_context_data(**kwargs)
        # Make sure we get the correct voucher group from URL, not from the VoucherOptions object
        voucher_group = get_object_or_404(VoucherGroup, pk=self.kwargs["id"])
        ctx.update(
            {
                "voucher_group": voucher_group,
                "voucher_groups": self.get_voucher_groups_queryset(),
                "search_query": self.request.GET.get("q", ""),
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(voucher_group),
            }
        )
        return ctx


class VoucherGroupCreateView(PermissionRequiredMixin, CreateView):
    """Provides a modal form to add a new voucher group."""

    model = VoucherGroup
    form_class = VoucherGroupAddForm
    template_name = "manage/voucher/add_voucher_group.html"
    permission_required = "core.manage_shop"

    def form_valid(self, form):
        """Saves voucher group with creator and redirects."""
        voucher_group = form.save(commit=False)
        voucher_group.creator = self.request.user
        voucher_group.save()

        messages.success(self.request, _("Voucher group has been created."))
        return HttpResponseRedirect(reverse("lfs_manage_voucher_group", kwargs={"id": voucher_group.id}))

    def get_success_url(self):
        """Return the URL to redirect to after successful form submission."""
        return reverse("lfs_manage_voucher_group", kwargs={"id": self.object.id})


class VoucherGroupDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a voucher group."""

    template_name = "manage/voucher/delete_voucher_group.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["voucher_group"] = get_object_or_404(VoucherGroup, pk=self.kwargs["id"])
        return context


class VoucherGroupDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes voucher group with passed id."""

    model = VoucherGroup
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"
    success_message = _("Voucher group and assigned vouchers have been deleted.")

    def get_success_url(self):
        return reverse("lfs_manage_voucher_groups")
