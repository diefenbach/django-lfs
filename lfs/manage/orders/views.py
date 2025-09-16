from typing import Dict, Any
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
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
from lfs.mail import utils as mail_utils
from lfs.order.models import Order
from lfs.manage.mixins import DirectDeleteMixin
from lfs.manage.orders.services import OrderFilterService, OrderDataService
from lfs.manage.orders.forms import OrderFilterForm


class OrderListView(PermissionRequiredMixin, TemplateView):
    """Shows a table view of all orders with filtering and pagination."""

    permission_required = "core.manage_shop"
    template_name = "manage/orders/order_list.html"

    def get_context_data(self, **kwargs):
        """Extends context with orders and filter form."""
        ctx = super().get_context_data(**kwargs)

        # Initialize services
        filter_service = OrderFilterService()
        data_service = OrderDataService()

        # Get filters from session
        order_filters = self.request.session.get("order-filters", {})

        # Filter orders
        queryset = Order.objects.all().order_by("-created")
        filtered_orders = filter_service.filter_orders(queryset, order_filters)

        # Paginate orders
        paginator = Paginator(filtered_orders, 50)
        page_number = self.request.GET.get("page", 1)
        orders_page = paginator.get_page(page_number)

        # Enrich orders with data
        orders_with_data = data_service.get_orders_with_data(orders_page)

        # Build states context for template compatibility
        states = []
        state_id = order_filters.get("state")
        for state in lfs.order.settings.ORDER_STATES:
            states.append({"id": state[0], "name": state[1], "selected": state_id == str(state[0])})

        # Prepare filter form
        filter_form_initial = self._get_filter_form_initial(order_filters, filter_service)
        filter_form = OrderFilterForm(initial=filter_form_initial)

        ctx.update(
            {
                "page": orders_page,
                "orders_with_data": orders_with_data,
                "states": states,
                "state_id": state_id,
                "start": order_filters.get("start", ""),
                "end": order_filters.get("end", ""),
                "name": order_filters.get("name", ""),
                "order_filters": order_filters,
                "filter_form": filter_form,
            }
        )
        return ctx

    def _get_filter_form_initial(self, order_filters, filter_service):
        """Get initial data for filter form."""
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


class OrderDataView(PermissionRequiredMixin, TemplateView):
    """View for data tab of an Order."""

    template_name = "manage/orders/order.html"
    tab_name = "data"
    permission_required = "core.manage_shop"

    def get_order(self) -> Order:
        """Gets the Order object."""
        return lfs_get_object_or_404(Order, pk=self.kwargs["order_id"])

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context for data tab."""
        ctx = super().get_context_data(**kwargs)

        # Initialize services
        filter_service = OrderFilterService()
        data_service = OrderDataService()

        # Get current order
        order = self.get_order()

        # Get filters from session
        order_filters = self.request.session.get("order-filters", {})

        # Get paginated orders for sidebar
        queryset = Order.objects.all().order_by("-created")
        filtered_orders = filter_service.filter_orders(queryset, order_filters)
        paginator = Paginator(filtered_orders, 8)
        page_number = self.request.GET.get("page", 1)
        orders_page = paginator.get_page(page_number)

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

        # Get enriched order data (summary + customer) via service
        order_data = data_service.get_order_with_data(order)

        # Prepare filter form
        filter_form_initial = self._get_filter_form_initial(order_filters, filter_service)
        filter_form = OrderFilterForm(initial=filter_form_initial)

        ctx.update(
            {
                "current_order": order,
                "orders_page": orders_page,
                "active_tab": self.tab_name,
                "states": states,
                "start": order_filters.get("start", ""),
                "end": order_filters.get("end", ""),
                "name": order_filters.get("name", ""),
                "order_filters": order_filters,
                "filter_form": filter_form,
                "order_total": order_data["total"] if order_data else 0,
                "order_products": ", ".join(order_data["products"]) if order_data else "",
                "customer_name": order_data["customer_name"] if order_data else "",
                "order_items": order.items.all(),
            }
        )
        return ctx

    def _get_filter_form_initial(self, order_filters, filter_service):
        """Get initial data for filter form."""
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


class ApplyOrderFiltersView(PermissionRequiredMixin, FormView):
    """Handles filter form submissions and redirects back to order view."""

    permission_required = "core.manage_shop"
    form_class = None

    def get_success_url(self) -> str:
        """Redirects back to the order view or order list."""
        order_id = self.kwargs.get("order_id") or self.request.POST.get("order-id")
        if order_id:
            return reverse("lfs_manage_order", kwargs={"order_id": order_id})
        return reverse("lfs_manage_orders")

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
            return reverse("lfs_manage_orders")


class ApplyPredefinedOrderFilterView(PermissionRequiredMixin, RedirectView):
    """Applies predefined date filters (today, week, month) to order view."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        order_id = self.request.GET.get("order_id") or self.kwargs.get("order_id")
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
            return (
                reverse("lfs_manage_order", kwargs={"order_id": order_id}) if order_id else reverse("lfs_manage_orders")
            )

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
            return reverse("lfs_manage_orders")


class OrderDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of an order."""

    template_name = "manage/orders/delete_order.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = get_object_or_404(Order, pk=self.kwargs["order_id"])
        return context


class OrderDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes order with passed id."""

    model = Order
    pk_url_kwarg = "order_id"
    permission_required = "core.manage_shop"
    success_message = _("Order has been deleted.")

    def get_success_url(self):
        return reverse("lfs_manage_orders")


@permission_required("core.manage_shop")
def send_order(request, order_id):
    """Sends order with passed order id to the customer of this order."""
    order = lfs_get_object_or_404(Order, pk=order_id)
    mail_utils.send_order_received_mail(request, order)
    messages.success(request, _("Order has been sent."))
    return HttpResponseRedirect(reverse("lfs_manage_order", kwargs={"order_id": order.id}))


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

        messages.success(request, _("Order state has been changed"))

    return HttpResponseRedirect(reverse("lfs_manage_order", kwargs={"order_id": order_id}))
