from datetime import datetime
from datetime import timedelta
import json

# django imports
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
import lfs.core.signals
import lfs.order.settings
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder
from lfs.mail import utils as mail_utils
from lfs.order.models import Order


# Views
@permission_required("core.manage_shop")
def manage_orders(request, template_name="manage/order/manage_orders.html"):
    """Dispatches to the first order or the order overview.
    """
    try:
        order = Order.objects.all()[0]
    except IndexError:
        return HttpResponseRedirect(reverse("lfs_orders"))
    else:
        return HttpResponseRedirect(
            reverse("lfs_manage_order", kwargs={"order_id": order.id}))


@permission_required("core.manage_shop")
def orders_view(request, template_name="manage/order/orders.html"):
    """Main view to display the order overview view.
    """
    return render(request, template_name, {
        "orders_inline": orders_inline(request),
        "orders_filters_inline": orders_filters_inline(request),
    })


@permission_required("core.manage_shop")
def order_view(request, order_id, template_name="manage/order/order.html"):
    """Displays the management interface for the order with passed order id.
    """
    order_filters = request.session.get("order-filters", {})
    order = lfs_get_object_or_404(Order, pk=order_id)

    states = []
    state_id = order_filters.get("state")
    for state in lfs.order.settings.ORDER_STATES:
        states.append({
            "id": state[0],
            "name": state[1],
            "selected_filter": state_id == str(state[0]),
            "selected_order": order.state == state[0],
        })

    return render(request, template_name, {
        "order_inline": order_inline(request, order_id),
        "order_filters_inline": order_filters_inline(request, order_id),
        "selectable_orders": selectable_orders_inline(request, order_id),
        "current_order": order,
        "states": states,
    })


# Parts
@permission_required("core.manage_shop")
def orders_inline(request, template_name="manage/order/orders_inline.html"):
    """Displays the orders. This is factored out in order to reload it via
    ajax request when the filter is changed..
    """
    order_filters = request.session.get("order-filters", {})
    orders = _get_filtered_orders(order_filters)

    page = (request.POST if request.method == 'POST' else request.GET).get("page", 1)
    paginator = Paginator(orders, 20)
    page = paginator.page(page)

    return render_to_string(template_name, request=request, context={
        "page": page,
    })


def order_inline(request, order_id, template_name="manage/order/order_inline.html"):
    """Displays the details of an order.
    """
    order_filters = request.session.get("order-filters", {})
    order = lfs_get_object_or_404(Order, pk=order_id)

    states = []
    state_id = order_filters.get("state")
    for state in lfs.order.settings.ORDER_STATES:
        states.append({
            "id": state[0],
            "name": state[1],
            "selected_filter": state_id == str(state[0]),
            "selected_order": order.state == state[0],
        })

    return render_to_string(template_name, request=request, context={
        "current_order": order,
        "start": order_filters.get("start", ""),
        "end": order_filters.get("end", ""),
        "name": order_filters.get("name", ""),
        "states": states,
        "invoice_address": order.invoice_address.as_html(request, "invoice"),
        "shipping_address": order.shipping_address.as_html(request, "shipping"),
    })


def order_filters_inline(request, order_id, template_name="manage/order/order_filters_inline.html"):
    """Renders the filters section within the order view.
    """
    order_filters = request.session.get("order-filters", {})
    order = lfs_get_object_or_404(Order, pk=order_id)

    states = []
    state_id = order_filters.get("state")
    for state in lfs.order.settings.ORDER_STATES:
        states.append({
            "id": state[0],
            "name": state[1],
            "selected_filter": state_id == str(state[0]),
            "selected_order": order.state == state[0],
        })

    return render_to_string(template_name, request=request, context={
        "current_order": order,
        "start": order_filters.get("start", ""),
        "end": order_filters.get("end", ""),
        "name": order_filters.get("name", ""),
        "states": states,
        "state_id": state_id
    })


def orders_filters_inline(request, template_name="manage/order/orders_filters_inline.html"):
    """Displays the order filter on top of the order overview view.
    """
    order_filters = request.session.get("order-filters", {})
    orders = _get_filtered_orders(order_filters)

    page = (request.POST if request.method == 'POST' else request.GET).get("page", 1)
    paginator = Paginator(orders, 20)
    page = paginator.page(page)

    states = []
    state_id = order_filters.get("state")
    for state in lfs.order.settings.ORDER_STATES:
        states.append({
            "id": state[0],
            "name": state[1],
            "selected": state_id == str(state[0]),
        })

    result = render_to_string(template_name, request=request, context={
        "paginator": paginator,
        "page": page,
        "state_id": state_id,
        "states": states,
        "start": order_filters.get("start", ""),
        "end": order_filters.get("end", ""),
        "name": order_filters.get("name", ""),
    })

    return result


def selectable_orders_inline(request, order_id, template_name="manage/order/selectable_orders_inline.html"):
    """Displays the selectable orders for the order view. (Used to switch
    quickly from one order to another.)
    """
    order = lfs_get_object_or_404(Order, pk=order_id)

    order_filters = request.session.get("order-filters", {})
    orders = _get_filtered_orders(order_filters)

    paginator = Paginator(orders, 20)

    try:
        page = int((request.POST if request.method == 'POST' else request.GET).get("page", 1))
    except TypeError:
        page = 1
    page = paginator.page(page)

    return render_to_string(template_name, request=request, context={
        "current_order": order,
        "orders": orders,
        "paginator": paginator,
        "page": page,
    })


# Actions
@permission_required("core.manage_shop")
def set_order_filters(request):
    """Sets order filters given by passed request.
    """
    req = request.POST if request.method == 'POST' else request.GET
    order_filters = request.session.get("order-filters", {})

    if request.POST.get("name", "") != "":
        order_filters["name"] = request.POST.get("name")
    else:
        if order_filters.get("name"):
            del order_filters["name"]

    if request.POST.get("start", "") != "":
        order_filters["start"] = request.POST.get("start")
    else:
        if order_filters.get("start"):
            del order_filters["start"]

    if request.POST.get("end", "") != "":
        order_filters["end"] = request.POST.get("end")
    else:
        if order_filters.get("end"):
            del order_filters["end"]

    if request.POST.get("state", "") != "":
        order_filters["state"] = request.POST.get("state")
    else:
        if order_filters.get("state"):
            del order_filters["state"]

    request.session["order-filters"] = order_filters

    if req.get("came-from") == "order":
        order_id = req.get("order-id")
        html = (
            ("#selectable-orders", selectable_orders_inline(request, order_id)),
            ("#order-inline", order_inline(request, order_id=order_id)),
            ("#orders-filters-inline", orders_filters_inline(request)),
        )
    else:
        html = (("#orders-inline", orders_inline(request)),
                ("#orders-filters-inline", orders_filters_inline(request)),)

    msg = _(u"Filters has been set")

    result = json.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def set_order_filters_date(request):
    """Sets the date filter by given short cut link
    """
    req = request.POST if request.method == 'POST' else request.GET
    order_filters = request.session.get("order-filters", {})

    start = timezone.now() - timedelta(int(req.get("start")))
    end = timezone.now() - timedelta(int(req.get("end")))

    order_filters["start"] = start.strftime("%Y-%m-%d")
    order_filters["end"] = end.strftime("%Y-%m-%d")
    request.session["order-filters"] = order_filters

    if req.get("came-from") == "order":
        order_id = req.get("order-id")
        html = (
            ("#selectable-orders", selectable_orders_inline(request, order_id)),
            ("#order-inline", order_inline(request, order_id)),
            ("#order-filters-inline", order_filters_inline(request, order_id)),
        )
    else:
        html = (
            ("#orders-inline", orders_inline(request)),
            ("#orders-filters-inline", orders_filters_inline(request)),
        )

    msg = _(u"Filters has been set")

    result = json.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def reset_order_filters(request):
    """resets order filter.
    """
    req = request.POST if request.method == 'POST' else request.GET
    if "order-filters" in request.session:
        del request.session["order-filters"]

    if req.get("came-from") == "order":
        order_id = req.get("order-id")
        html = (
            ("#selectable-orders", selectable_orders_inline(request, order_id)),
            ("#order-inline", order_inline(request, order_id=order_id)),
            ("#order-filters-inline", order_filters_inline(request, order_id=order_id)),
        )
    else:
        html = (
            ("#orders-inline", orders_inline(request)),
            ("#orders-filters-inline", orders_filters_inline(request)),
        )

    msg = _(u"Filters has been reset")

    result = json.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def set_selectable_orders_page(request):
    """Sets the page of selectable orders.
    """
    order_id = request.GET.get("order-id", 1)
    html = (
        ("#selectable-orders", selectable_orders_inline(request, order_id)),
    )

    result = json.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def set_orders_page(request):
    """Sets the page of selectable orders.
    """
    html = (
        ("#orders-inline", orders_inline(request)),
        ("#orders-filters-inline", orders_filters_inline(request)),
    )

    result = json.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
@require_POST
def delete_order(request, order_id):
    """Deletes order with provided order id.
    """
    order = lfs_get_object_or_404(Order, pk=order_id)
    order.delete()

    try:
        order = Order.objects.all()[0]
        url = reverse("lfs_manage_order", kwargs={"order_id": order.id})
    except IndexError:
        url = reverse("lfs_manage_orders")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
def send_order(request, order_id):
    """Sends order with passed order id to the customer of this order.
    """
    order = lfs_get_object_or_404(Order, pk=order_id)
    mail_utils.send_order_received_mail(order)

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_order", kwargs={"order_id": order.id}),
        msg=_(u"Order has been sent."),
    )


@permission_required("core.manage_shop")
@require_POST
def change_order_state(request):
    """Changes the state of an order, given by request post variables.
    """
    order_id = request.POST.get("order-id")
    state_id = request.POST.get("new-state")
    order = get_object_or_404(Order, pk=order_id)

    old_state = order.state

    try:
        order.state = int(state_id)
    except ValueError:
        pass
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

    msg = _(u"State has been changed")

    html = (
        ("#selectable-orders", selectable_orders_inline(request, order_id)),
        ("#order-inline", order_inline(request, order_id)),
    )

    result = json.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


def _get_filtered_orders(order_filters):
    """
    """
    orders = Order.objects.all()

    # name
    name = order_filters.get("name", "")
    if name != "":
        f = Q(customer_lastname__icontains=name)
        f |= Q(customer_firstname__icontains=name)
        orders = orders.filter(f)

    # state
    state_id = order_filters.get("state")
    if state_id is not None:
        orders = orders.filter(state=state_id)

    # start
    start = order_filters.get("start", "")
    s = start
    if start != "":
        s = lfs.core.utils.get_start_day(start)

    if not s:
        s = datetime.min

    # end
    end = order_filters.get("end", "")
    e = end
    if end != "":
        e = lfs.core.utils.get_end_day(end)

    if not e:
        e = datetime.max

    orders = orders.filter(created__range=(s, e))

    return orders
