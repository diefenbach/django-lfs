from typing import Dict, Any, Optional
from datetime import timedelta, datetime

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, DeleteView, RedirectView, TemplateView

from lfs.cart.models import Cart
from lfs.customer.models import Customer
from lfs.manage.carts.forms import CartFilterForm
from lfs.manage.mixins import DirectDeleteMixin


class ManageCartsView(PermissionRequiredMixin, TemplateView):
    """Shows a table view of all carts with filtering and pagination."""

    permission_required = "core.manage_shop"
    template_name = "manage/cart/cart_list.html"

    def get_carts_queryset(self):
        """Returns filtered Carts based on session filters."""
        queryset = Cart.objects.all().order_by("-modification_date")
        cart_filters = self.request.session.get("cart-filters", {})

        # Apply date filters
        start = cart_filters.get("start", "")
        end = cart_filters.get("end", "")

        # Parse start date using ISO format
        start_date = parse_iso_date(start)
        if start_date:
            start_date = timezone.make_aware(start_date.replace(hour=0, minute=0, second=0))
        else:
            start_date = timezone.datetime(1970, 1, 1)

        # Parse end date using ISO format
        end_date = parse_iso_date(end)
        if end_date:
            end_date = timezone.make_aware(end_date.replace(hour=23, minute=59, second=59))
        else:
            end_date = timezone.now()

        queryset = queryset.filter(modification_date__range=(start_date, end_date))
        return queryset

    def get_paginated_carts(self):
        """Returns paginated carts for the table."""
        carts_queryset = self.get_carts_queryset()
        paginator = Paginator(carts_queryset, 15)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)

    def get_context_data(self, **kwargs):
        """Extends context with carts and filter form."""
        ctx = super().get_context_data(**kwargs)

        carts_page = self.get_paginated_carts()

        cart_filters = self.request.session.get("cart-filters", {})
        if cart_filters.get("start"):
            start = parse_iso_date(cart_filters["start"])
        else:
            start = None

        if cart_filters.get("end"):
            end = parse_iso_date(cart_filters["end"])
        else:
            end = None

        filter_form = CartFilterForm(
            initial={
                "start": start,
                "end": end,
            }
        )

        # Calculate totals for each cart
        carts_with_data = []
        for cart in carts_page:
            total = 0
            item_count = 0
            products = []
            for item in cart.get_items():
                total += item.get_price_gross(self.request)
                item_count += item.amount
                products.append(item.product.get_name())

            # Get customer information
            try:
                if cart.user:
                    customer = Customer.objects.get(user=cart.user)
                else:
                    customer = Customer.objects.get(session=cart.session)
            except Customer.DoesNotExist:
                customer = None

            carts_with_data.append(
                {
                    "cart": cart,
                    "total": total,
                    "item_count": item_count,
                    "products": products,
                    "customer": customer,
                }
            )

        ctx.update(
            {
                "carts_page": carts_page,
                "carts_with_data": carts_with_data,
                "cart_filters": cart_filters,
                "filter_form": filter_form,
            }
        )
        return ctx


class NoCartsView(PermissionRequiredMixin, TemplateView):
    """Displays that no carts exist."""

    permission_required = "core.manage_shop"
    template_name = "manage/cart/no_carts.html"


class CartTabMixin:
    """Mixin for tab navigation in Cart views."""

    template_name = "manage/cart/cart.html"
    tab_name: Optional[str] = None

    def get_cart(self) -> Cart:
        """Gets the Cart object."""
        return get_object_or_404(Cart, pk=self.kwargs["id"])

    def get_carts_queryset(self):
        """Returns filtered Carts based on session filters with pagination."""
        queryset = Cart.objects.all().order_by("-modification_date")
        cart_filters = self.request.session.get("cart-filters", {})

        # Apply date filters
        start = cart_filters.get("start", "")
        end = cart_filters.get("end", "")

        # Parse start date using ISO format
        start_date = parse_iso_date(start)
        if start_date:
            start_date = timezone.make_aware(start_date.replace(hour=0, minute=0, second=0))
        else:
            start_date = timezone.datetime(1970, 1, 1)

        # Parse end date using ISO format
        end_date = parse_iso_date(end)
        if end_date:
            end_date = timezone.make_aware(end_date.replace(hour=23, minute=59, second=59))
        else:
            end_date = timezone.now()

        queryset = queryset.filter(modification_date__range=(start_date, end_date))
        return queryset

    def get_paginated_carts(self):
        """Returns paginated carts for sidebar."""
        carts_queryset = self.get_carts_queryset()
        paginator = Paginator(carts_queryset, 10)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with sidebar navigation and Cart."""
        ctx = super().get_context_data(**kwargs)
        cart = getattr(self, "object", None) or self.get_cart()

        # Get paginated carts for sidebar
        carts_page = self.get_paginated_carts()

        cart_filters = self.request.session.get("cart-filters", {})
        if cart_filters.get("start"):
            start = parse_iso_date(cart_filters["start"])
        else:
            start = None

        if cart_filters.get("end"):
            end = parse_iso_date(cart_filters["end"])
        else:
            end = None

        filter_form = CartFilterForm(
            initial={
                "start": start,
                "end": end,
            }
        )

        ctx.update(
            {
                "cart": cart,
                "carts_page": carts_page,
                "cart_filters": cart_filters,
                "filter_form": filter_form,
                "active_tab": self.tab_name,
            }
        )
        return ctx


class CartDataView(PermissionRequiredMixin, CartTabMixin, TemplateView):
    """View for data tab of a Cart."""

    tab_name = "data"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context for data tab."""
        ctx = super().get_context_data(**kwargs)
        cart = self.get_cart()

        # Calculate cart totals and items
        total = 0
        products = []
        for item in cart.get_items():
            total += item.get_price_gross(self.request)
            products.append(item.product.get_name())

        # Get customer information
        try:
            if cart.user:
                customer = Customer.objects.get(user=cart.user)
            else:
                customer = Customer.objects.get(session=cart.session)
        except Customer.DoesNotExist:
            customer = None

        ctx.update(
            {
                "cart_total": total,
                "cart_products": ", ".join(products),
                "customer": customer,
                "cart_items": cart.get_items(),
            }
        )
        return ctx


class ApplyCartFiltersView(PermissionRequiredMixin, FormView):
    """Handles filter form submissions and redirects back to cart view."""

    permission_required = "core.manage_shop"
    form_class = CartFilterForm

    def get_success_url(self) -> str:
        """Redirects back to the cart view or cart list."""
        cart_id = self.kwargs.get("id")
        if cart_id:
            return reverse("lfs_manage_cart", kwargs={"id": cart_id})
        return reverse("lfs_manage_carts")

    def form_valid(self, form):
        """Saves filter data to session."""
        cart_filters = self.request.session.get("cart-filters", {})

        # Update filters
        start = form.cleaned_data.get("start")
        end = form.cleaned_data.get("end")

        if start:
            cart_filters["start"] = format_iso_date(start)
        elif "start" in cart_filters:
            del cart_filters["start"]

        if end:
            cart_filters["end"] = format_iso_date(end)
        elif "end" in cart_filters:
            del cart_filters["end"]

        self.request.session["cart-filters"] = cart_filters

        messages.success(self.request, _("Cart filters have been updated."))
        return super().form_valid(form)


class CartDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a cart."""

    template_name = "manage/cart/delete_cart.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = get_object_or_404(Cart, pk=self.kwargs["id"])
        return context


class CartDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes cart with passed id."""

    model = Cart
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"
    success_message = _("Cart has been deleted.")

    def get_success_url(self):
        return reverse("lfs_manage_carts")


class ResetCartFiltersView(PermissionRequiredMixin, RedirectView):
    """Resets all cart filters."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        # Clear filters from session
        if "cart-filters" in self.request.session:
            del self.request.session["cart-filters"]

        messages.success(self.request, _("Cart filters have been reset."))

        # Redirect back to where we came from
        cart_id = self.request.GET.get("cart_id")
        if cart_id:
            return reverse("lfs_manage_cart", kwargs={"id": cart_id})
        else:
            return reverse("lfs_manage_carts")


class ApplyPredefinedCartFilterView(PermissionRequiredMixin, RedirectView):
    """Applies predefined date filters (today, week, month) to cart view."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        cart_id = self.kwargs.get("id")
        filter_type = self.kwargs.get("filter_type")

        now = timezone.now()
        start_date = None
        end_date = now

        if filter_type == "today":
            # Full current day: start of today to start of tomorrow
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            filter_name = _("Today")
        elif filter_type == "week":
            # Last 7 days including today
            start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            filter_name = _("Last 7 Days")
        elif filter_type == "month":
            # Last 31 days including today
            start_date = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            filter_name = _("Last 31 Days")
        else:
            messages.error(self.request, _("Invalid filter type."))
            return reverse("lfs_manage_cart", kwargs={"id": cart_id}) if cart_id else reverse("lfs_manage_carts")

        # Save filter to session
        cart_filters = self.request.session.get("cart-filters", {})
        cart_filters["start"] = format_iso_date(start_date)
        cart_filters["end"] = format_iso_date(end_date)
        self.request.session["cart-filters"] = cart_filters

        messages.success(self.request, _("Filter applied: %(filter_name)s") % {"filter_name": filter_name})

        if cart_id:
            return reverse("lfs_manage_cart", kwargs={"id": cart_id})
        else:
            return reverse("lfs_manage_carts")


def parse_iso_date(date_string: str) -> datetime:
    """Parse ISO format date string (YYYY-MM-DD)."""
    if not date_string:
        return None

    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        return None


def format_iso_date(date_obj: datetime) -> str:
    """Format date as ISO format string (YYYY-MM-DD)."""
    if not date_obj:
        return ""

    return date_obj.strftime("%Y-%m-%d")
