from typing import Dict, Any
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, RedirectView, TemplateView

from lfs.customer.models import Customer
from lfs.manage.customers.forms import CustomerFilterForm
from lfs.manage.customers.services import CustomerFilterService, CustomerDataService


class CustomerListView(PermissionRequiredMixin, TemplateView):
    """Shows a table view of all customers with filtering and pagination."""

    permission_required = "core.manage_shop"
    template_name = "manage/customers/customer_list.html"

    def get_context_data(self, **kwargs):
        """Extends context with customers and filter form."""
        ctx = super().get_context_data(**kwargs)

        # Initialize services
        filter_service = CustomerFilterService()
        data_service = CustomerDataService()

        try:
            # Get filters from session
            customer_filters = self.request.session.get("customer-filters", {})
            if not isinstance(customer_filters, dict):
                customer_filters = {}

            # Filter customers
            queryset = Customer.objects.all()
            filtered_customers = filter_service.filter_customers(queryset, customer_filters)

            # Apply ordering
            ordering = self.request.session.get("customer-ordering", "id")
            ordering_order = self.request.session.get("customer-ordering-order", "")
            ordering_str = filter_service.get_ordering(ordering, ordering_order)
            filtered_customers = filtered_customers.distinct().order_by(ordering_str)

            # Paginate customers
            paginator = Paginator(filtered_customers, 30)
            page_number = self.request.GET.get("page", 1)
            try:
                page_number = int(page_number)
                if page_number < 1:
                    page_number = 1
            except (ValueError, TypeError):
                page_number = 1
            customers_page = paginator.get_page(page_number)

            # Enrich customers with data
            customers_with_data = data_service.get_customers_with_data(customers_page, self.request)

        except Exception:
            # Handle database errors gracefully
            customers_page = None
            customers_with_data = []
            customer_filters = {}

        # Prepare filter form
        filter_form_initial = self._get_filter_form_initial(customer_filters, filter_service)
        filter_form = CustomerFilterForm(initial=filter_form_initial)

        ordering = self.request.session.get("customer-ordering", "id")
        if ordering is None:
            ordering = "id"

        ctx.update(
            {
                "customers_page": customers_page,
                "customers_with_data": customers_with_data,
                "customer_filters": customer_filters,
                "filter_form": filter_form,
                "ordering": ordering,
            }
        )
        return ctx

    def _get_filter_form_initial(self, customer_filters, filter_service):
        """Get initial data for filter form."""
        name = customer_filters.get("name", "")
        start = None
        end = None

        if customer_filters.get("start"):
            start = filter_service.parse_iso_date(customer_filters["start"])
        if customer_filters.get("end"):
            end = filter_service.parse_iso_date(customer_filters["end"])

        return {"name": name, "start": start, "end": end}


class NoCustomersView(PermissionRequiredMixin, TemplateView):
    """Displays that no customers exist."""

    permission_required = "core.manage_shop"
    template_name = "manage/customers/no_customers.html"


class CustomerDataView(PermissionRequiredMixin, TemplateView):
    """View for displaying customer data tab."""

    template_name = "manage/customers/customer.html"
    tab_name = "data"
    permission_required = "core.manage_shop"

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

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context for data tab."""
        ctx = super().get_context_data(**kwargs)

        # Initialize services
        filter_service = CustomerFilterService()
        data_service = CustomerDataService()

        # Get current customer
        customer = self.get_customer()

        # Get filters from session
        customer_filters = self.request.session.get("customer-filters", {})
        if not isinstance(customer_filters, dict):
            customer_filters = {}

        # Get paginated customers for sidebar
        queryset = Customer.objects.all()
        filtered_customers = filter_service.filter_customers(queryset, customer_filters)

        # Apply ordering
        ordering = self.request.session.get("customer-ordering", "id")
        ordering_order = self.request.session.get("customer-ordering-order", "")
        ordering_str = filter_service.get_ordering(ordering, ordering_order)
        filtered_customers = filtered_customers.distinct().order_by(ordering_str)

        # Paginate for sidebar
        paginator = Paginator(filtered_customers, 10)
        page_number = self.request.GET.get("page", 1)
        try:
            page_number = int(page_number)
            if page_number < 1:
                page_number = 1
        except (ValueError, TypeError):
            page_number = 1
        customers_page = paginator.get_page(page_number)

        # Get enriched customer data via service
        customer_data = data_service.get_customer_with_data(customer, self.request)

        # Prepare filter form
        filter_form_initial = self._get_filter_form_initial(customer_filters, filter_service)
        filter_form = CustomerFilterForm(initial=filter_form_initial)

        ordering = self.request.session.get("customer-ordering", "id")
        if ordering is None:
            ordering = "id"

        ctx.update(
            {
                "customer": customer,
                "customers_page": customers_page,
                "active_tab": self.tab_name,
                "customer_filters": customer_filters,
                "filter_form": filter_form,
                "ordering": ordering,
                **customer_data,
            }
        )
        return ctx

    def _get_filter_form_initial(self, customer_filters, filter_service):
        """Get initial data for filter form."""
        name = customer_filters.get("name", "")
        start = None
        end = None

        if customer_filters.get("start"):
            start = filter_service.parse_iso_date(customer_filters["start"])
        if customer_filters.get("end"):
            end = filter_service.parse_iso_date(customer_filters["end"])

        return {"name": name, "start": start, "end": end}


class ApplyCustomerFiltersView(PermissionRequiredMixin, FormView):
    """Handles filter form submissions and redirects back to customer view."""

    permission_required = "core.manage_shop"
    form_class = CustomerFilterForm
    template_name = "manage/customers/customer_list.html"  # Fallback template for form errors

    def get_success_url(self) -> str:
        """Redirects back to the customer view or customer list."""
        customer_id = self.kwargs.get("customer_id") or self.request.POST.get("customer_id")
        if customer_id:
            return reverse("lfs_manage_customer", kwargs={"customer_id": customer_id})
        return reverse("lfs_manage_customers")

    def form_valid(self, form):
        """Saves filter data to session."""
        customer_filters = self.request.session.get("customer-filters", {})

        # Update filters
        name = form.cleaned_data.get("name", "")
        if name:
            customer_filters["name"] = name
        elif "name" in customer_filters:
            del customer_filters["name"]

        start = form.cleaned_data.get("start")
        end = form.cleaned_data.get("end")

        filter_service = CustomerFilterService()
        if start:
            customer_filters["start"] = filter_service.format_iso_date(start)
        elif "start" in customer_filters:
            del customer_filters["start"]

        if end:
            customer_filters["end"] = filter_service.format_iso_date(end)
        elif "end" in customer_filters:
            del customer_filters["end"]

        self.request.session["customer-filters"] = customer_filters

        messages.success(self.request, _("Customer filters have been updated."))
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle invalid form data by redirecting with error message."""
        messages.error(self.request, _("Invalid filter data provided. Please check your input."))
        return super().form_valid(form)


class ResetCustomerFiltersView(PermissionRequiredMixin, RedirectView):
    """Resets all customer filters."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        # Clear filters from session
        if "customer-filters" in self.request.session:
            del self.request.session["customer-filters"]

        messages.success(self.request, _("Customer filters have been reset."))

        # Redirect back to where we came from
        customer_id = self.request.GET.get("customer_id")
        if customer_id:
            return reverse("lfs_manage_customer", kwargs={"customer_id": customer_id})
        else:
            return reverse("lfs_manage_customers")


class SetCustomerOrderingView(PermissionRequiredMixin, RedirectView):
    """Sets customer ordering."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
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

        # Redirect back to where we came from
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

        # Save only start to session (service uses half-open interval and handles missing end)
        customer_filters = self.request.session.get("customer-filters", {})
        filter_service = CustomerFilterService()
        customer_filters["start"] = filter_service.format_iso_date(start_date)
        # We intentionally do not set end for presets
        if "end" in customer_filters:
            del customer_filters["end"]
        self.request.session["customer-filters"] = customer_filters

        messages.success(self.request, _("Filter applied: %(filter_name)s") % {"filter_name": filter_name})

        if customer_id:
            return reverse("lfs_manage_customer", kwargs={"customer_id": customer_id})
        else:
            return reverse("lfs_manage_customers")
