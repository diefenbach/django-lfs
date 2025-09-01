from django.core.paginator import Paginator

from .services import OrderFilterService, OrderDataService
from .forms import OrderFilterForm


class OrderFilterMixin:
    """Mixin for handling order filtering logic."""

    def get_order_filters(self):
        """Get order filters from session."""
        return self.request.session.get("order-filters", {})

    def get_filtered_orders_queryset(self):
        """Get filtered orders based on session filters."""
        from lfs.order.models import Order

        queryset = Order.objects.all().order_by("-created")
        order_filters = self.get_order_filters()

        filter_service = OrderFilterService()
        return filter_service.filter_orders(queryset, order_filters)

    def get_filter_form_initial(self):
        """Get initial data for filter form."""
        order_filters = self.get_order_filters()

        filter_service = OrderFilterService()
        start = None
        end = None

        if order_filters.get("start"):
            start = filter_service.parse_iso_date(order_filters["start"])

        if order_filters.get("end"):
            end = filter_service.parse_iso_date(order_filters["end"])

        return {
            "name": order_filters.get("name", ""),
            "state": order_filters.get("state", ""),
            "start": start,
            "end": end,
        }


class OrderPaginationMixin:
    """Mixin for handling order pagination."""

    def get_paginated_orders(self, page_size=20):
        """Get paginated orders."""
        queryset = self.get_filtered_orders_queryset()
        paginator = Paginator(queryset, page_size)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)


class OrderDataMixin:
    """Mixin for handling order data calculations."""

    def get_order_summary(self, order):
        """Get summary data for a single order."""
        data_service = OrderDataService()
        return data_service.get_order_summary(order)

    def get_orders_with_data(self, orders):
        """Get list of orders with calculated data."""
        data_service = OrderDataService()
        return data_service.get_orders_with_data(orders)

    def get_order_with_data(self, order):
        """Get a single order enriched with calculated data."""
        data_service = OrderDataService()
        return data_service.get_order_with_data(order)


class OrderContextMixin:
    """Mixin for providing common order context data."""

    def get_order_context_data(self, **kwargs):
        """Get common context data for order views."""
        order_filters = self.get_order_filters()
        filter_form = OrderFilterForm(initial=self.get_filter_form_initial())

        return {
            "order_filters": order_filters,
            "filter_form": filter_form,
        }
