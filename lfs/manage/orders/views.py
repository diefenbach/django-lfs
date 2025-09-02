from typing import Dict, Any, Optional
from datetime import timedelta
import json

from django.conf import settings
from django.core.cache import cache
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, FormView, RedirectView, DeleteView

import lfs.core.utils
import lfs.core.signals
import lfs.order.settings
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder
from lfs.mail import utils as mail_utils
from lfs.order.models import Order
from lfs.manage.mixins import DirectDeleteMixin
from lfs.manage.orders.mixins import OrderFilterMixin, OrderPaginationMixin, OrderDataMixin, OrderContextMixin
from lfs.manage.orders.services import OrderFilterService


class OrderListView(
    PermissionRequiredMixin, OrderFilterMixin, OrderPaginationMixin, OrderDataMixin, OrderContextMixin, TemplateView
):
    """Shows a table view of all orders with filtering and pagination."""

    permission_required = "core.manage_shop"
    template_name = "manage/order/orders.html"

    def get_context_data(self, **kwargs):
        """Extends context with orders and filter form."""
        ctx = super().get_context_data(**kwargs)

        orders_page = self.get_paginated_orders()
        orders_with_data = self.get_orders_with_data(orders_page)
        order_filters = self.get_order_filters()

        # Build states context for template compatibility
        states = []
        state_id = order_filters.get("state")
        for state in lfs.order.settings.ORDER_STATES:
            states.append({"id": state[0], "name": state[1], "selected": state_id == str(state[0])})

        ctx.update(
            {
                "page": orders_page,
                "orders_with_data": orders_with_data,
                "states": states,
                "state_id": state_id,
                "start": order_filters.get("start", ""),
                "end": order_filters.get("end", ""),
                "name": order_filters.get("name", ""),
                **self.get_order_context_data(),
            }
        )
        return ctx


class OrderTabMixin(OrderFilterMixin, OrderPaginationMixin, OrderContextMixin):
    """Mixin for tab navigation in Order views."""

    template_name = "manage/order/order.html"
    tab_name: Optional[str] = None

    def get_order(self) -> Order:
        """Gets the Order object."""
        return lfs_get_object_or_404(Order, pk=self.kwargs["order_id"])

    def get_paginated_orders(self, page_size=10):
        """Returns paginated orders for sidebar."""
        return super().get_paginated_orders(page_size=page_size)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with sidebar navigation and Order."""
        ctx = super().get_context_data(**kwargs)
        order = getattr(self, "object", None) or self.get_order()

        # Get paginated orders for sidebar
        orders_page = self.get_paginated_orders()
        order_filters = self.get_order_filters()

        # Build states context for template compatibility
        states = []
        state_id = order_filters.get("state")
        for state in lfs.order.settings.ORDER_STATES:
            states.append(
                {
                    "id": state[0],
                    "name": state[1],
                    "selected_filter": state_id == str(state[0]),
                    "selected_order": order.state == state[0],
                }
            )

        ctx.update(
            {
                "current_order": order,
                "orders_page": orders_page,
                "active_tab": self.tab_name,
                "states": states,
                "start": order_filters.get("start", ""),
                "end": order_filters.get("end", ""),
                "name": order_filters.get("name", ""),
                **self.get_order_context_data(),
            }
        )
        return ctx


class OrderDataView(PermissionRequiredMixin, OrderTabMixin, OrderDataMixin, TemplateView):
    """View for data tab of an Order."""

    tab_name = "data"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context for data tab."""
        ctx = super().get_context_data(**kwargs)
        order = self.get_order()

        # Get enriched order data (summary + customer) via service
        order_data = self.get_order_with_data(order)

        ctx.update(
            {
                "order_total": order_data["total"],
                "order_products": ", ".join(order_data["products"]),
                "customer_name": order_data["customer_name"],
                "order_items": order.items.all(),
            }
        )
        return ctx


class ApplyOrderFiltersView(PermissionRequiredMixin, FormView):
    """Handles filter form submissions and redirects back to order view."""

    permission_required = "core.manage_shop"
    form_class = None

    def get_success_url(self) -> str:
        """Redirects back to the order view or order list."""
        order_id = self.kwargs.get("order_id") or self.request.POST.get("order-id")
        if order_id:
            return reverse("lfs_manage_order", kwargs={"order_id": order_id})
        return reverse("lfs_orders")

    def post(self, request, *args, **kwargs):
        """Saves filter data to session."""
        order_filters = request.session.get("order-filters", {})

        # Update filters
        name = request.POST.get("name", "").strip()
        state = request.POST.get("state", "").strip()
        start = request.POST.get("start", "").strip()
        end = request.POST.get("end", "").strip()

        filter_service = OrderFilterService()

        if name:
            order_filters["name"] = name
        elif "name" in order_filters:
            del order_filters["name"]

        if state:
            order_filters["state"] = state
        elif "state" in order_filters:
            del order_filters["state"]

        if start:
            order_filters["start"] = filter_service.format_iso_date(start)
        elif "start" in order_filters:
            del order_filters["start"]

        if end:
            order_filters["end"] = filter_service.format_iso_date(end)
        elif "end" in order_filters:
            del order_filters["end"]

        request.session["order-filters"] = order_filters

        messages.success(request, _("Order filters have been updated."))
        return HttpResponseRedirect(self.get_success_url())


class ResetOrderFiltersView(PermissionRequiredMixin, RedirectView):
    """Resets all order filters."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        # Clear filters from session
        if "order-filters" in self.request.session:
            del self.request.session["order-filters"]

        messages.success(self.request, _("Order filters have been reset."))

        # Redirect back to where we came from
        order_id = self.request.GET.get("order_id") or self.kwargs.get("order_id")
        if order_id:
            return reverse("lfs_manage_order", kwargs={"order_id": order_id})
        else:
            return reverse("lfs_orders")


class ApplyPredefinedOrderFilterView(PermissionRequiredMixin, RedirectView):
    """Applies predefined date filters (today, week, month) to order view."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        order_id = self.kwargs.get("order_id")
        filter_type = self.kwargs.get("filter_type")

        now = timezone.now()
        start_date = None

        if filter_type == "today":
            # Start of today
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            filter_name = _("Today")
        elif filter_type == "week":
            # Last 7 days including today
            start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
            filter_name = _("Last 7 Days")
        elif filter_type == "month":
            # Start of current month
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            filter_name = _("This Month")
        else:
            messages.error(self.request, _("Invalid filter type."))
            return reverse("lfs_manage_order", kwargs={"order_id": order_id}) if order_id else reverse("lfs_orders")

        # Save only start to session (service uses half-open interval and handles missing end)
        order_filters = self.request.session.get("order-filters", {})
        filter_service = OrderFilterService()
        order_filters["start"] = filter_service.format_iso_date(start_date)
        # We intentionally do not set end for presets
        if "end" in order_filters:
            del order_filters["end"]
        self.request.session["order-filters"] = order_filters

        messages.success(self.request, _("Filter applied: %(filter_name)s") % {"filter_name": filter_name})

        if order_id:
            return reverse("lfs_manage_order", kwargs={"order_id": order_id})
        else:
            return reverse("lfs_orders")


class OrderDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes order with passed id."""

    model = Order
    pk_url_kwarg = "order_id"
    permission_required = "core.manage_shop"
    success_message = _("Order has been deleted.")

    def get_success_url(self):
        return reverse("lfs_orders")


# Legacy function-based views for backward compatibility
@permission_required("core.manage_shop")
def manage_orders(request, template_name="manage/order/manage_orders.html"):
    """Dispatches to the first order or the order overview."""
    try:
        order = Order.objects.all()[0]
    except IndexError:
        return HttpResponseRedirect(reverse("lfs_orders"))
    else:
        return HttpResponseRedirect(reverse("lfs_manage_order", kwargs={"order_id": order.id}))


@permission_required("core.manage_shop")
def orders_view(request, template_name="manage/order/orders.html"):
    # Delegate to class-based list view for clean cut
    return OrderListView.as_view()(request)


@permission_required("core.manage_shop")
def order_view(request, order_id, template_name="manage/order/order.html"):
    # Delegate to class-based order data view
    return OrderDataView.as_view()(request, order_id=order_id)


# Legacy inline parts removed by clean cut
@permission_required("core.manage_shop")
def set_selectable_orders_page(request):
    # Deprecated endpoint; return no-op JSON for safety until all references removed
    result = json.dumps({"html": ()}, cls=LazyEncoder)
    return HttpResponse(result, content_type="application/json")


@permission_required("core.manage_shop")
def set_orders_page(request):
    result = json.dumps({"html": ()}, cls=LazyEncoder)
    return HttpResponse(result, content_type="application/json")


@permission_required("core.manage_shop")
def send_order(request, order_id):
    """Sends order with passed order id to the customer of this order."""
    order = lfs_get_object_or_404(Order, pk=order_id)
    mail_utils.send_order_received_mail(request, order)

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_order", kwargs={"order_id": order.id}),
        msg=_("Order has been sent."),
    )


@permission_required("core.manage_shop")
@require_POST
def change_order_state(request):
    """Changes the state of an order, given by request post variables."""
    order_id = request.POST.get("order-id")
    state_id = request.POST.get("new-state")
    order = get_object_or_404(Order, pk=order_id)

    old_state = order.state

    try:
        order.state = int(state_id)
    except ValueError:
        messages.error(request, _("Invalid state selected."))
    else:
        order.state_modified = timezone.now()
        order.save()

        if order.state == lfs.order.settings.SENT:
            lfs.core.signals.order_sent.send(sender=order, request=request)
        if order.state == lfs.order.settings.PAID:
            lfs.core.signals.order_paid.send(sender=order, request=request)

        lfs.core.signals.order_state_changed.send(sender=order, order=order, request=request, old_state=old_state)

        cache_key = "%s-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, Order.__name__.lower(), order.pk)
        cache.delete(cache_key)

        messages.success(request, _("Order state has been changed to %(state)s") % {"state": order.get_state_display()})

    return HttpResponseRedirect(reverse("lfs_manage_order", kwargs={"order_id": order_id}))


# Legacy function removed - _get_filtered_orders is now handled by OrderFilterService
