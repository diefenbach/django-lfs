# python imports
import json

# django imports
from django.db.models import Q
from django.contrib.auth.decorators import permission_required
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.cart.utils
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.cart.models import Cart
from lfs.core.utils import LazyEncoder
from lfs.customer.models import Customer
from lfs.manage.utils import get_current_page
from lfs.order.models import Order


# Views
@permission_required("core.manage_shop")
def customer(request, customer_id, template_name="manage/customer/customer.html"):
    """Base view to display the customer with passed customer id.
    """
    return render(request, template_name, {
        "customer_inline": customer_inline(request, customer_id),
        "selectable_customers_inline": selectable_customers_inline(request, customer_id),
        "customer_filters_inline": customer_filters_inline(request, customer_id)
    })


@permission_required("core.manage_shop")
def customers(request, template_name="manage/customer/customers.html"):
    """Base view to display the customers overview.
    """
    return render(request, template_name, {
        "customers_inline": customers_inline(request),
        "customers_filters_inline": customers_filters_inline(request),
    })


# Parts
def customer_filters_inline(request, customer_id, template_name="manage/customer/customer_filters_inline.html"):
    """Renders the filters section of the customer view.
    """
    customer_filters = request.session.get("customer-filters", {})
    customer = lfs_get_object_or_404(Customer, pk=customer_id)

    return render_to_string(template_name, request=request, context={
        "customer": customer,
        "name": customer_filters.get("name", ""),
    })


def customers_filters_inline(request, template_name="manage/customer/customers_filters_inline.html"):
    """Renders the filters section of the customers overview view.
    """
    customer_filters = request.session.get("customer-filters", {})
    ordering = request.session.get("customer-ordering", "id")

    temp = _get_filtered_customers(request, customer_filters)

    paginator = Paginator(temp, 30)

    page = (request.POST if request.method == 'POST' else request.GET).get("page", 1)
    page = paginator.page(page)

    customers = []
    for customer in page.object_list:
        query = Q()
        if customer.session:
            query |= Q(session=customer.session)
        if customer.user:
            query |= Q(user=customer.user)

        try:
            cart = Cart.objects.get(query)
            cart_price = cart.get_price_gross(request, total=True)
        except Cart.DoesNotExist:
            cart_price = None

        orders = Order.objects.filter(query)
        customers.append({
            "customer": customer,
            "orders": len(orders),
            "cart_price": cart_price,
        })

    return render_to_string(template_name, request=request, context={
        "customers": customers,
        "page": page,
        "paginator": paginator,
        "start": customer_filters.get("start", ""),
        "end": customer_filters.get("end", ""),
        "ordering": ordering,
    })


@permission_required("core.manage_shop")
def customer_inline(request, customer_id, template_name="manage/customer/customer_inline.html"):
    """Displays customer with provided customer id.
    """
    customer = lfs_get_object_or_404(Customer, pk=customer_id)

    query = Q()
    if customer.session:
        query |= Q(session=customer.session)
    if customer.user:
        query |= Q(user=customer.user)
    orders = Order.objects.filter(query)

    try:
        cart = Cart.objects.get(query)
    except Cart.DoesNotExist:
        cart = None
        cart_price = None
    else:
        # Shipping
        selected_shipping_method = lfs.shipping.utils.get_selected_shipping_method(request)
        shipping_costs = lfs.shipping.utils.get_shipping_costs(request, selected_shipping_method)

        # Payment
        selected_payment_method = lfs.payment.utils.get_selected_payment_method(request)
        payment_costs = lfs.payment.utils.get_payment_costs(request, selected_payment_method)

        cart_price = cart.get_price_gross(request) + shipping_costs["price_gross"] + payment_costs["price"]

    if customer.selected_shipping_address:
        shipping_address = customer.selected_shipping_address.as_html(request, "shipping")
    else:
        shipping_address = None

    if customer.selected_invoice_address:
        invoice_address = customer.selected_invoice_address.as_html(request, "invoice")
    else:
        invoice_address = None

    return render_to_string(template_name, request=request, context={
        "customer": customer,
        "orders": orders,
        "cart": cart,
        "cart_price": cart_price,
        "shipping_address": shipping_address,
        "invoice_address": invoice_address,
    })


@permission_required("core.manage_shop")
def customers_inline(request, template_name="manage/customer/customers_inline.html"):
    """Displays carts overview.
    """
    customer_filters = request.session.get("customer-filters", {})
    ordering = request.session.get("customer-ordering", "id")

    temp = _get_filtered_customers(request, customer_filters)

    paginator = Paginator(temp, 30)

    page = (request.POST if request.method == 'POST' else request.GET).get("page", 1)
    page = paginator.page(page)

    customers = []
    for customer in page.object_list:
        if not customer.user_id and not customer.session:
            continue

        query = Q()
        if customer.session:
            query |= Q(session=customer.session)
        if customer.user:
            query |= Q(user=customer.user)

        try:
            cart = Cart.objects.get(query)
            cart_price = cart.get_price_gross(request, total=True)
        except Cart.DoesNotExist:
            cart_price = None

        orders = Order.objects.filter(query)
        customers.append({
            "customer": customer,
            "orders": len(orders),
            "cart_price": cart_price,
        })

    return render_to_string(template_name, request=request, context={
        "customers": customers,
        "page": page,
        "paginator": paginator,
        "start": customer_filters.get("start", ""),
        "end": customer_filters.get("end", ""),
        "ordering": ordering,
    })


@permission_required("core.manage_shop")
def selectable_customers_inline(request, customer_id, template_name="manage/customer/selectable_customers_inline.html"):
    """Display selectable customers.
    """
    AMOUNT = 30
    customer = lfs_get_object_or_404(Customer, pk=customer_id)
    customer_filters = request.session.get("customer-filters", {})
    customers = _get_filtered_customers(request, customer_filters)

    page = get_current_page(request, customers, customer, AMOUNT)
    paginator = Paginator(customers, AMOUNT)

    try:
        page = paginator.page(page)
    except EmptyPage:
        page = paginator.page(1)

    return render_to_string(template_name, request=request, context={
        "paginator": paginator,
        "page": page,
        "customer_id": int(customer_id),
    })


# Actions
@permission_required("core.manage_shop")
def set_selectable_customers_page(request):
    """Sets the page of the selectable customers sections.
    """
    customer_id = request.GET.get("customer_id")

    result = selectable_customers_inline(request, customer_id)

    result = json.dumps({
        "html": (("#selectable-customers-inline", result),),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def set_customers_page(request):
    """Sets the page of the selectable customers sections.
    """
    result = json.dumps({
        "html": (
            ("#customers-inline", customers_inline(request)),
            ("#customers-filters-inline", customers_filters_inline(request)),
        ),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def set_ordering(request, ordering):
    """Sets customer ordering given by passed request.
    """
    req = request.POST if request.method == 'POST' else request.GET
    if ordering == "lastname":
        ordering = "addresses__lastname"
    elif ordering == "firstname":
        ordering = "addresses__firstname"
    elif ordering == "email":
        ordering = "user__email"

    if ordering == request.session.get("customer-ordering"):
        if request.session.get("customer-ordering-order") == "":
            request.session["customer-ordering-order"] = "-"
        else:
            request.session["customer-ordering-order"] = ""
    else:
        request.session["customer-ordering-order"] = ""

    request.session["customer-ordering"] = ordering
    if req.get("came-from") == "customer":
        customer_id = req.get("customer-id")
        html = (
            ("#selectable-customers-inline", selectable_customers_inline(request, customer_id)),
            ("#customer-inline", customer_inline(request, customer_id=customer_id)),
        )
    else:
        html = (("#customers-inline", customers_inline(request)),)

    result = json.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def set_customer_filters(request):
    """Sets customer filters given by passed request.
    """
    req = request.POST if request.method == 'POST' else request.GET
    customer_filters = request.session.get("customer-filters", {})

    if request.POST.get("name", "") != "":
        customer_filters["name"] = request.POST.get("name")
    else:
        if customer_filters.get("name"):
            del customer_filters["name"]

    request.session["customer-filters"] = customer_filters

    if req.get("came-from") == "customer":
        customer_id = req.get("customer-id")
        html = (
            ("#selectable-customers-inline", selectable_customers_inline(request, customer_id)),
            ("#customer-inline", customer_inline(request, customer_id=customer_id)),
        )
    else:
        html = (("#customers-inline", customers_inline(request)),)

    msg = _(u"Customer filters have been set")

    result = json.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def reset_customer_filters(request):
    """Resets all customer filters.
    """
    req = request.POST if request.method == 'POST' else request.GET
    if "customer-filters" in request.session:
        del request.session["customer-filters"]

    if req.get("came-from") == "customer":
        customer_id = req.get("customer-id")
        html = (
            ("#selectable-customers-inline", selectable_customers_inline(request, customer_id)),
            ("#customer-inline", customer_inline(request, customer_id=customer_id)),
            ("#customer-filters-inline", customer_filters_inline(request, customer_id)),
        )
    else:
        html = (("#customers-inline", customers_inline(request)),)

    msg = _(u"Customer filters has been reset")

    result = json.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


# Private Methods
def _get_filtered_customers(request, customer_filters):
    """
    """
    customer_ordering = request.session.get("customer-ordering", "id")
    customer_ordering_order = request.session.get("customer-ordering-order", "")

    customers = Customer.objects.all()

    # Filter
    name = customer_filters.get("name", "")
    if name != "":
        f = Q(addresses__lastname__icontains=name)
        f |= Q(addresses__firstname__icontains=name)
        customers = customers.filter(f)

    # Ordering
    customers = customers.distinct().order_by("%s%s" % (customer_ordering_order, customer_ordering))

    return customers
