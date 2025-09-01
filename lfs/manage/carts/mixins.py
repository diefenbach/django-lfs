from django.core.paginator import Paginator

from lfs.manage.carts.services import CartFilterService, CartDataService
from lfs.manage.carts.forms import CartFilterForm


class CartFilterMixin:
    """Mixin for handling cart filtering logic."""

    def get_cart_filters(self):
        """Get cart filters from session."""
        return self.request.session.get("cart-filters", {})

    def get_filtered_carts_queryset(self):
        """Get filtered carts based on session filters."""
        queryset = self.model.objects.all().order_by("-modification_date")
        cart_filters = self.get_cart_filters()

        filter_service = CartFilterService()
        return filter_service.filter_carts(queryset, cart_filters)

    def get_filter_form_initial(self):
        """Get initial data for filter form."""
        cart_filters = self.get_cart_filters()

        filter_service = CartFilterService()
        start = None
        end = None

        if cart_filters.get("start"):
            start = filter_service.parse_iso_date(cart_filters["start"])

        if cart_filters.get("end"):
            end = filter_service.parse_iso_date(cart_filters["end"])

        return {
            "start": start,
            "end": end,
        }


class CartPaginationMixin:
    """Mixin for handling cart pagination."""

    def get_paginated_carts(self, page_size=15):
        """Get paginated carts."""
        queryset = self.get_filtered_carts_queryset()
        paginator = Paginator(queryset, page_size)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)


class CartDataMixin:
    """Mixin for handling cart data calculations."""

    def get_cart_summary(self, cart):
        """Get summary data for a single cart."""
        data_service = CartDataService()
        return data_service.get_cart_summary(cart, self.request)

    def get_carts_with_data(self, carts):
        """Get list of carts with calculated data."""
        data_service = CartDataService()
        return data_service.get_carts_with_data(carts, self.request)

    def get_cart_with_data(self, cart):
        """Get a single cart enriched with calculated data and customer."""
        data_service = CartDataService()
        result = data_service.get_carts_with_data([cart], self.request)
        return result[0] if result else None


class CartContextMixin:
    """Mixin for providing common cart context data."""

    def get_cart_context_data(self, **kwargs):
        """Get common context data for cart views."""
        cart_filters = self.get_cart_filters()
        filter_form = CartFilterForm(initial=self.get_filter_form_initial())

        return {
            "cart_filters": cart_filters,
            "filter_form": filter_form,
        }
