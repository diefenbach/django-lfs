from django.core.paginator import Paginator
from lfs.customer.models import Customer
from .services import CustomerFilterService, CustomerDataService
from .forms import CustomerFilterForm


class CustomerFilterMixin:
    """Mixin for handling customer filtering logic."""

    def get_customer_filters(self):
        """Get customer filters from session."""
        if not hasattr(self.request, "session") or self.request.session is None:
            return {}

        try:
            filters = self.request.session.get("customer-filters", {})
            # Handle case where session data is corrupted (not a dict)
            if not isinstance(filters, dict):
                return {}
            return filters
        except (AttributeError, TypeError):
            return {}

    def get_filtered_customers_queryset(self):
        """Get filtered customers based on session filters."""
        queryset = Customer.objects.all()
        customer_filters = self.get_customer_filters()

        # Get ordering from session
        ordering = self.request.session.get("customer-ordering", "id")
        ordering_order = self.request.session.get("customer-ordering-order", "")

        filter_service = CustomerFilterService()
        queryset = filter_service.filter_customers(queryset, customer_filters)

        # Apply ordering
        ordering_str = filter_service.get_ordering(ordering, ordering_order)
        return queryset.distinct().order_by(ordering_str)

    def get_filter_form_initial(self):
        """Get initial data for filter form."""
        customer_filters = self.get_customer_filters()

        filter_service = CustomerFilterService()
        name = ""
        start = ""
        end = ""

        if customer_filters.get("start"):
            parsed_date = filter_service.parse_iso_date(customer_filters["start"])
            start = filter_service.format_iso_date(parsed_date) if parsed_date else ""

        if customer_filters.get("end"):
            parsed_date = filter_service.parse_iso_date(customer_filters["end"])
            end = filter_service.format_iso_date(parsed_date) if parsed_date else ""

        if customer_filters.get("name"):
            name = customer_filters["name"]

        return {
            "name": name,
            "start": start,
            "end": end,
        }

    def get_filter_service(self):
        """Get CustomerFilterService instance."""
        return CustomerFilterService()


class CustomerPaginationMixin:
    """Mixin for handling customer pagination."""

    def get_paginated_customers(self, page_size=30):
        """Get paginated customers."""
        queryset = self.get_filtered_customers_queryset()
        paginator = Paginator(queryset, page_size)

        # Handle edge cases for page number
        page_number = self.request.GET.get("page", 1)
        try:
            page_number = int(page_number)
            if page_number < 1:
                page_number = 1
        except (ValueError, TypeError):
            page_number = 1

        return paginator.get_page(page_number)


class CustomerDataMixin:
    """Mixin for handling customer data calculations."""

    def get_customers_with_data(self, customers):
        """Get list of customers with calculated data."""
        data_service = CustomerDataService()
        return data_service.get_customers_with_data(customers, self.request)

    def get_customer_with_data(self, customer):
        """Get a single customer enriched with calculated data."""
        data_service = CustomerDataService()
        return data_service.get_customer_with_data(customer, self.request)


class CustomerContextMixin:
    """Mixin for providing common customer context data."""

    def get_customer_context_data(self, **kwargs):
        """Get common context data for customer views."""
        customer_filters = self.get_customer_filters()
        filter_form = CustomerFilterForm(initial=self.get_filter_form_initial())

        ordering = self.request.session.get("customer-ordering", "id")
        if ordering is None:
            ordering = "id"

        return {
            "customer_filters": customer_filters,
            "filter_form": filter_form,
            "ordering": ordering,
        }
