from typing import Dict, Any, Optional
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, RedirectView, TemplateView

from lfs.customer.models import Customer
from lfs.manage.customers.forms import CustomerFilterForm
from lfs.manage.customers.mixins import (
    CustomerFilterMixin,
    CustomerPaginationMixin,
    CustomerDataMixin,
    CustomerContextMixin,
)


class CustomerListView(
    PermissionRequiredMixin,
    CustomerFilterMixin,
    CustomerPaginationMixin,
    CustomerDataMixin,
    CustomerContextMixin,
    TemplateView,
):
    """Shows a table view of all customers with filtering and pagination."""

    permission_required = "core.manage_shop"
    template_name = "manage/customers/customer_list.html"
    model = Customer

    def get_context_data(self, **kwargs):
        """Extends context with customers and filter form."""
        ctx = super().get_context_data(**kwargs)

        try:
            customers_page = self.get_paginated_customers()
            customers_with_data = self.get_customers_with_data(customers_page)
        except Exception:
            # Handle database errors gracefully
            customers_page = None
            customers_with_data = []

        ctx.update(
            {
                "customers_page": customers_page,
                "customers_with_data": customers_with_data,
                **self.get_customer_context_data(),
            }
        )
        return ctx


class NoCustomersView(PermissionRequiredMixin, TemplateView):
    """Displays that no customers exist."""

    permission_required = "core.manage_shop"
    template_name = "manage/customers/no_customers.html"


class CustomerTabMixin(CustomerFilterMixin, CustomerPaginationMixin, CustomerContextMixin):
    """Mixin for tab navigation in Customer views."""

    template_name = "manage/customers/customer.html"
    tab_name: Optional[str] = None
    model = Customer

    def get_customer(self) -> Customer:
        """Gets the Customer object."""
        customer_id = self.kwargs.get("customer_id")
        if not customer_id:
            raise Http404("Customer ID is required")

        try:
            # Ensure customer_id is a valid integer
            customer_id = int(customer_id)
            if customer_id <= 0:
                raise Http404("Invalid customer ID")
        except (ValueError, TypeError):
            raise Http404("Invalid customer ID format")

        return get_object_or_404(Customer, pk=customer_id)

    def get_paginated_customers(self):
        """Returns paginated customers for sidebar."""
        return super().get_paginated_customers(page_size=10)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with sidebar navigation and Customer."""
        ctx = super().get_context_data(**kwargs)
        customer = getattr(self, "object", None) or self.get_customer()

        # Get paginated customers for sidebar
        customers_page = self.get_paginated_customers()

        ctx.update(
            {
                "customer": customer,
                "customers_page": customers_page,
                "active_tab": self.tab_name,
                **self.get_customer_context_data(),
            }
        )
        return ctx


class CustomerDataView(PermissionRequiredMixin, CustomerTabMixin, CustomerDataMixin, TemplateView):
    """View for displaying customer data tab."""

    tab_name = "data"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context for data tab."""
        ctx = super().get_context_data(**kwargs)
        customer = self.get_customer()

        # Get enriched customer data via service
        customer_data = self.get_customer_with_data(customer)

        ctx.update(customer_data)
        return ctx


class ApplyCustomerFiltersView(PermissionRequiredMixin, FormView):
    """Handles filter form submissions and redirects back to customer view."""

    permission_required = "core.manage_shop"
    form_class = CustomerFilterForm

    def form_valid(self, form):
        """Process filter form and update session."""
        try:
            customer_filters = self.request.session.get("customer-filters", {})
            if not isinstance(customer_filters, dict):
                customer_filters = {}

            # Update filters based on form data
            name = form.cleaned_data.get("name", "")
            if name:
                customer_filters["name"] = name
            elif "name" in customer_filters:
                del customer_filters["name"]

            start = form.cleaned_data.get("start")
            if start:
                customer_filters["start"] = start.isoformat()
            elif "start" in customer_filters:
                del customer_filters["start"]

            end = form.cleaned_data.get("end")
            if end:
                customer_filters["end"] = end.isoformat()
            elif "end" in customer_filters:
                del customer_filters["end"]

            self.request.session["customer-filters"] = customer_filters
            messages.success(self.request, _("Customer filters have been applied"))

        except Exception:
            messages.error(self.request, _("Error applying filters"))

        return self.get_success_response()

    def form_invalid(self, form):
        """Handle invalid form."""
        messages.error(self.request, _("Invalid filter data"))
        return self.get_success_response()

    def get_success_response(self):
        """Determine where to redirect after filter application."""
        # Check if we came from a specific customer
        customer_id = self.request.POST.get("customer_id") or self.request.GET.get("customer_id")
        if customer_id:
            return redirect("lfs_manage_customer", customer_id=customer_id)
        else:
            return redirect("lfs_manage_customers")


class ResetCustomerFiltersView(PermissionRequiredMixin, RedirectView):
    """Resets all customer filters."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        """Reset filters and redirect."""
        if "customer-filters" in self.request.session:
            del self.request.session["customer-filters"]

        messages.success(self.request, _("Customer filters have been reset"))

        # Check if we came from a specific customer
        customer_id = self.request.GET.get("customer_id")
        if customer_id:
            return reverse("lfs_manage_customer", kwargs={"customer_id": customer_id})
        else:
            return reverse("lfs_manage_customers")


class SetCustomerOrderingView(PermissionRequiredMixin, RedirectView):
    """Sets customer ordering."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        """Set ordering and redirect."""
        ordering = kwargs.get("ordering", "id")

        # Toggle ordering direction if same field
        if ordering == self.request.session.get("customer-ordering"):
            if self.request.session.get("customer-ordering-order", "") == "":
                self.request.session["customer-ordering-order"] = "-"
            else:
                self.request.session["customer-ordering-order"] = ""
        else:
            self.request.session["customer-ordering-order"] = ""

        self.request.session["customer-ordering"] = ordering

        # Check if we came from a specific customer
        customer_id = self.request.GET.get("customer_id")
        if customer_id:
            return reverse("lfs_manage_customer", kwargs={"customer_id": customer_id})
        else:
            return reverse("lfs_manage_customers")


class ApplyPredefinedCustomerFilterView(PermissionRequiredMixin, RedirectView):
    """Applies predefined date filters (today, week, month) to customer view."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        customer_id = self.kwargs.get("customer_id")
        filter_type = self.kwargs.get("filter_type")

        now = timezone.now()
        start_date = None

        if filter_type == "today":
            # Start of today
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            filter_name = _("Today")
        elif filter_type == "week":
            # Last 7 days including today
            start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            filter_name = _("Last 7 Days")
        elif filter_type == "month":
            # Start of current month
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            filter_name = _("This Month")
        else:
            messages.error(self.request, _("Invalid filter type."))
            return (
                reverse("lfs_manage_customer", kwargs={"customer_id": customer_id})
                if customer_id
                else reverse("lfs_manage_customers")
            )

        # Save filters to session
        customer_filters = self.request.session.get("customer-filters", {})
        customer_filters["start"] = start_date.isoformat()
        # We intentionally do not set end for presets
        if "end" in customer_filters:
            del customer_filters["end"]
        self.request.session["customer-filters"] = customer_filters

        messages.success(self.request, _("Filter applied: %(filter_name)s") % {"filter_name": filter_name})

        if customer_id:
            return reverse("lfs_manage_customer", kwargs={"customer_id": customer_id})
        else:
            return reverse("lfs_manage_customers")
