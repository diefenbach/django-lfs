from typing import Dict, Any, Optional
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, DeleteView, RedirectView, TemplateView

from lfs.cart.models import Cart
from lfs.manage.carts.forms import CartFilterForm
from lfs.manage.carts.mixins import CartFilterMixin, CartPaginationMixin, CartDataMixin, CartContextMixin
from lfs.manage.carts.services import CartFilterService
from lfs.manage.mixins import DirectDeleteMixin


class CartListView(
    PermissionRequiredMixin, CartFilterMixin, CartPaginationMixin, CartDataMixin, CartContextMixin, TemplateView
):
    """Shows a table view of all carts with filtering and pagination."""

    permission_required = "core.manage_shop"
    template_name = "manage/cart/cart_list.html"
    model = Cart

    def get_context_data(self, **kwargs):
        """Extends context with carts and filter form."""
        ctx = super().get_context_data(**kwargs)

        carts_page = self.get_paginated_carts()
        carts_with_data = self.get_carts_with_data(carts_page)

        ctx.update(
            {
                "carts_page": carts_page,
                "carts_with_data": carts_with_data,
                **self.get_cart_context_data(),
            }
        )
        return ctx


class NoCartsView(PermissionRequiredMixin, TemplateView):
    """Displays that no carts exist."""

    permission_required = "core.manage_shop"
    template_name = "manage/cart/no_carts.html"


class CartTabMixin(CartFilterMixin, CartPaginationMixin, CartContextMixin):
    """Mixin for tab navigation in Cart views."""

    template_name = "manage/cart/cart.html"
    tab_name: Optional[str] = None
    model = Cart

    def get_cart(self) -> Cart:
        """Gets the Cart object."""
        return get_object_or_404(Cart, pk=self.kwargs["id"])

    def get_paginated_carts(self):
        """Returns paginated carts for sidebar."""
        return super().get_paginated_carts(page_size=10)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with sidebar navigation and Cart."""
        ctx = super().get_context_data(**kwargs)
        cart = getattr(self, "object", None) or self.get_cart()

        # Get paginated carts for sidebar
        carts_page = self.get_paginated_carts()

        ctx.update(
            {
                "cart": cart,
                "carts_page": carts_page,
                "active_tab": self.tab_name,
                **self.get_cart_context_data(),
            }
        )
        return ctx


class CartDataView(PermissionRequiredMixin, CartTabMixin, CartDataMixin, TemplateView):
    """View for data tab of a Cart."""

    tab_name = "data"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context for data tab."""
        ctx = super().get_context_data(**kwargs)
        cart = self.get_cart()

        # Get enriched cart data (summary + customer) via service
        cart_data = self.get_cart_with_data(cart)

        ctx.update(
            {
                "cart_total": cart_data["total"],
                "cart_products": ", ".join(cart_data["products"]),
                "customer": cart_data["customer"],
                "cart_items": cart.get_items(),
            }
        )
        return ctx


class ApplyCartFiltersView(PermissionRequiredMixin, FormView):
    """Handles filter form submissions and redirects back to cart view."""

    permission_required = "core.manage_shop"
    form_class = CartFilterForm
    template_name = "manage/cart/cart_list.html"  # Fallback template for form errors

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

        filter_service = CartFilterService()
        if start:
            cart_filters["start"] = filter_service.format_iso_date(start)
        elif "start" in cart_filters:
            del cart_filters["start"]

        if end:
            cart_filters["end"] = filter_service.format_iso_date(end)
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
            return reverse("lfs_manage_cart", kwargs={"id": cart_id}) if cart_id else reverse("lfs_manage_carts")

        # Save only start to session (service uses half-open interval and handles missing end)
        cart_filters = self.request.session.get("cart-filters", {})
        filter_service = CartFilterService()
        cart_filters["start"] = filter_service.format_iso_date(start_date)
        # We intentionally do not set end for presets
        if "end" in cart_filters:
            del cart_filters["end"]
        self.request.session["cart-filters"] = cart_filters

        messages.success(self.request, _("Filter applied: %(filter_name)s") % {"filter_name": filter_name})

        if cart_id:
            return reverse("lfs_manage_cart", kwargs={"id": cart_id})
        else:
            return reverse("lfs_manage_carts")
