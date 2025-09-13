from typing import Dict, List, Tuple, Any, Optional

# django imports
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, CreateView, DeleteView, RedirectView, TemplateView

# lfs imports
from lfs.customer_tax.models import CustomerTax
from lfs.manage.customer_taxes.forms import CustomerTaxForm
from lfs.manage.mixins import DirectDeleteMixin


class ManageCustomerTaxesView(PermissionRequiredMixin, RedirectView):
    """Dispatches to the first customer tax or to the add customer tax form."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        try:
            customer_tax = CustomerTax.objects.all().order_by("rate")[0]
            return reverse("lfs_manage_customer_tax", kwargs={"id": customer_tax.id})
        except IndexError:
            return reverse("lfs_manage_no_customer_taxes")


class NoCustomerTaxesView(PermissionRequiredMixin, TemplateView):
    """Displays that no customer taxes exist."""

    permission_required = "core.manage_shop"
    template_name = "manage/customer_taxes/no_customer_taxes.html"


class CustomerTaxTabMixin:
    """Mixin for tab navigation in CustomerTax views."""

    template_name = "manage/customer_taxes/customer_tax.html"
    tab_name: Optional[str] = None

    def get_customer_tax(self) -> CustomerTax:
        """Gets the CustomerTax object."""
        return get_object_or_404(CustomerTax, pk=self.kwargs["id"])

    def get_customer_taxes_queryset(self):
        """Returns filtered CustomerTaxes based on search parameter."""
        queryset = CustomerTax.objects.all().order_by("rate")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(Q(rate__icontains=search_query) | Q(description__icontains=search_query))

        return queryset

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with tab navigation and CustomerTax."""
        ctx = super().get_context_data(**kwargs)
        customer_tax = getattr(self, "object", None) or self.get_customer_tax()

        ctx.update(
            {
                "customer_tax": customer_tax,
                "customer_taxes": self.get_customer_taxes_queryset(),
                "search_query": self.request.GET.get("q", ""),
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(customer_tax),
            }
        )
        return ctx

    def _get_tabs(self, customer_tax: CustomerTax) -> List[Tuple[str, str]]:
        """Creates tab navigation URLs with search parameter."""
        search_query = self.request.GET.get("q", "").strip()

        data_url = reverse("lfs_manage_customer_tax", args=[customer_tax.pk])
        criteria_url = reverse("lfs_manage_customer_tax_criteria", args=[customer_tax.pk])

        # Add search parameter if present
        if search_query:
            from urllib.parse import urlencode

            query_params = urlencode({"q": search_query})
            data_url += "?" + query_params
            criteria_url += "?" + query_params

        return [
            ("data", data_url),
            ("criteria", criteria_url),
        ]

    def _get_navigation_context(self):
        """Get navigation context for templates."""
        return {
            "search_query": self.request.GET.get("q", ""),
        }


class CustomerTaxDataView(PermissionRequiredMixin, CustomerTaxTabMixin, UpdateView):
    """View for data tab of a CustomerTax."""

    model = CustomerTax
    form_class = CustomerTaxForm
    tab_name = "data"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the data tab after successful save."""
        return reverse("lfs_manage_customer_tax", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        response = super().form_valid(form)
        messages.success(self.request, _("Customer tax has been saved."))
        return response


class CustomerTaxCriteriaView(PermissionRequiredMixin, CustomerTaxTabMixin, TemplateView):
    """View for criteria tab of a CustomerTax."""

    tab_name = "criteria"
    template_name = "manage/customer_taxes/customer_tax.html"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the criteria tab."""
        return reverse("lfs_manage_customer_tax_criteria", kwargs={"id": self.kwargs["id"]})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles criteria saving."""
        customer_tax = self.get_customer_tax()
        customer_tax.save_criteria(request)

        messages.success(self.request, _("Criteria have been saved."))

        # Check if this is an HTMX request
        if request.headers.get("HX-Request"):
            # Return the updated criteria tab content
            return render(request, "manage/customer_taxes/tabs/_criteria.html", self.get_context_data())

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with criteria."""
        ctx = super().get_context_data(**kwargs)
        customer_tax = self.get_customer_tax()

        criteria = []
        position = 0
        for criterion_object in customer_tax.get_criteria():
            position += 10
            criterion_html = criterion_object.render(self.request, position)
            criteria.append(criterion_html)

        ctx.update(
            {
                "criteria": criteria,
            }
        )
        return ctx


class CustomerTaxCreateView(PermissionRequiredMixin, CreateView):
    """Provides a modal form to add a new customer tax."""

    model = CustomerTax
    form_class = CustomerTaxForm
    template_name = "manage/customer_taxes/add_customer_tax.html"
    permission_required = "core.manage_shop"

    def form_valid(self, form):
        """Saves customer tax and redirects."""
        customer_tax = form.save()

        messages.success(self.request, _("Customer tax has been created."))
        return HttpResponseRedirect(reverse("lfs_manage_customer_tax", kwargs={"id": customer_tax.id}))

    def get_success_url(self):
        """Return the URL to redirect to after successful form submission."""
        return reverse("lfs_manage_customer_tax", kwargs={"id": self.object.id})


class CustomerTaxDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a customer tax."""

    template_name = "manage/customer_taxes/delete_customer_tax.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer_tax"] = get_object_or_404(CustomerTax, pk=self.kwargs["id"])
        return context


class CustomerTaxDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes customer tax with passed id."""

    model = CustomerTax
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"
    success_message = _("Customer tax has been deleted.")

    def get_success_url(self):
        return reverse("lfs_manage_customer_taxes")
