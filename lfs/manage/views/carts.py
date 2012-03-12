# python imports
from datetime import datetime
from datetime import timedelta

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.cart.models import Cart
from lfs.core.utils import LazyEncoder
from lfs.customer.models import Customer


# Views
@permission_required("core.manage_shop", login_url="/login/")
def carts_view(request, template_name="manage/cart/carts.html"):
    """Displays the carts overview.
    """
    return render_to_response(template_name, RequestContext(request, {
        "carts_filters_inline": carts_filters_inline(request),
        "carts_inline": carts_inline(request),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def cart_view(request, cart_id, template_name="manage/cart/cart.html"):
    """Displays the cart with the passed cart id.
    """
    return render_to_response(template_name, RequestContext(request, {
        "cart_filters_inline": cart_filters_inline(request, cart_id),
        "selectable_carts_inline": selectable_carts_inline(request, cart_id),
        "cart_inline": cart_inline(request, cart_id),
    }))


# Parts
def cart_filters_inline(request, cart_id, template_name="manage/cart/cart_filters_inline.html"):
    """Renders the filters section of the cart view.
    """
    cart = lfs_get_object_or_404(Cart, pk=cart_id)
    cart_filters = request.session.get("cart-filters", {})

    return render_to_string(template_name, RequestContext(request, {
        "cart": cart,
        "start": cart_filters.get("start", ""),
        "end": cart_filters.get("end", ""),
    }))


def carts_filters_inline(request, template_name="manage/cart/carts_filters_inline.html"):
    """Displays the filters part of the carts overview.
    """
    cart_filters = request.session.get("cart-filters", {})
    temp = _get_filtered_carts(cart_filters)

    paginator = Paginator(temp, 30)

    page = request.REQUEST.get("page", 1)
    page = paginator.page(page)

    return render_to_string(template_name, RequestContext(request, {
        "page": page,
        "paginator": paginator,
        "start": cart_filters.get("start", ""),
        "end": cart_filters.get("end", ""),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def carts_inline(request, template_name="manage/cart/carts_inline.html"):
    """Displays carts overview.
    """
    cart_filters = request.session.get("cart-filters", {})
    temp = _get_filtered_carts(cart_filters)

    paginator = Paginator(temp, 30)

    page = request.REQUEST.get("page", 1)
    page = paginator.page(page)

    carts = []
    for cart in page.object_list:
        products = []
        total = 0
        for item in cart.get_items():
            total += item.get_price_gross(request)
            products.append(item.product.get_name())

        try:
            if cart.user:
                customer = Customer.objects.get(user=cart.user)
            else:
                customer = Customer.objects.get(session=cart.session)
        except Customer.DoesNotExist:
            customer = None

        carts.append({
            "id": cart.id,
            "amount_of_items": cart.get_amount_of_items(),
            "session": cart.session,
            "user": cart.user,
            "total": total,
            "products": ", ".join(products),
            "creation_date": cart.creation_date,
            "modification_date": cart.modification_date,
            "customer": customer,
        })

    return render_to_string(template_name, RequestContext(request, {
        "carts": carts,
        "page": page,
        "paginator": paginator,
        "start": cart_filters.get("start", ""),
        "end": cart_filters.get("end", ""),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def cart_inline(request, cart_id, template_name="manage/cart/cart_inline.html"):
    """Displays cart with provided cart id.
    """
    cart = lfs_get_object_or_404(Cart, pk=cart_id)

    total = 0
    for item in cart.get_items():
        total += item.get_price_gross(request)

    try:
        if cart.user:
            customer = Customer.objects.get(user=cart.user)
        else:
            customer = Customer.objects.get(session=cart.session)
    except Customer.DoesNotExist:
        customer = None

    cart_filters = request.session.get("cart-filters", {})
    return render_to_string(template_name, RequestContext(request, {
        "cart": cart,
        "customer": customer,
        "total": total,
        "start": cart_filters.get("start", ""),
        "end": cart_filters.get("end", ""),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def selectable_carts_inline(request, cart_id, template_name="manage/cart/selectable_carts_inline.html"):
    """Displays selectable carts section within cart view.
    """
    cart_filters = request.session.get("cart-filters", {})
    carts = _get_filtered_carts(cart_filters)

    paginator = Paginator(carts, 30)

    try:
        page = int(request.REQUEST.get("page", 1))
    except TypeError:
        page = 1
    page = paginator.page(page)

    return render_to_string(template_name, RequestContext(request, {
        "paginator": paginator,
        "page": page,
        "cart_id": int(cart_id),
    }))


# Actions
@permission_required("core.manage_shop", login_url="/login/")
def set_carts_page(request):
    """Sets the page of the displayed carts.
    """
    result = simplejson.dumps({
        "html": (
            ("#carts-inline", carts_inline(request)),
            ("#carts-filters-inline", carts_filters_inline(request)),
        ),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def set_cart_page(request):
    """Sets the page of the selectable carts within cart view.
    """
    cart_id = request.GET.get("cart-id")

    result = simplejson.dumps({
        "html": (
            ("#cart-inline", cart_inline(request, cart_id)),
            ("#cart-filters-inline", cart_filters_inline(request, cart_id)),
            ("#selectable-carts-inline", selectable_carts_inline(request, cart_id)),
        ),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def set_cart_filters(request):
    """Sets cart filters given by passed request.
    """
    cart_filters = request.session.get("cart-filters", {})

    if request.POST.get("start", "") != "":
        cart_filters["start"] = request.POST.get("start")
    else:
        if cart_filters.get("start"):
            del cart_filters["start"]

    if request.POST.get("end", "") != "":
        cart_filters["end"] = request.POST.get("end")
    else:
        if cart_filters.get("end"):
            del cart_filters["end"]

    request.session["cart-filters"] = cart_filters

    if request.REQUEST.get("came-from") == "cart":
        cart_id = request.REQUEST.get("cart-id")
        html = (
            ("#selectable-carts-inline", selectable_carts_inline(request, cart_id)),
            ("#cart-filters-inline", cart_filters_inline(request, cart_id)),
            ("#cart-inline", cart_inline(request, cart_id)),
        )
    else:
        html = (
            ("#carts-filters-inline", carts_filters_inline(request)),
            ("#carts-inline", carts_inline(request)),
        )

    msg = _(u"Cart filters has been set.")

    result = simplejson.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def set_cart_filters_date(request):
    """Sets the date filter by given short cut link
    """
    cart_filters = request.session.get("cart-filters", {})

    start = datetime.now() - timedelta(int(request.REQUEST.get("start")))
    end = datetime.now() - timedelta(int(request.REQUEST.get("end")))

    cart_filters["start"] = start.strftime("%Y-%m-%d")
    cart_filters["end"] = end.strftime("%Y-%m-%d")
    request.session["cart-filters"] = cart_filters

    if request.REQUEST.get("came-from") == "cart":
        cart_id = request.REQUEST.get("cart-id")
        html = (
            ("#selectable-carts-inline", selectable_carts_inline(request, cart_id)),
            ("#cart-filters-inline", cart_filters_inline(request, cart_id)),
            ("#cart-inline", cart_inline(request, cart_id)),
        )
    else:
        html = (
            ("#carts-filters-inline", carts_filters_inline(request)),
            ("#carts-inline", carts_inline(request)),
        )

    msg = _(u"Cart filters has been set")

    result = simplejson.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def reset_cart_filters(request):
    """Resets all cart filters.
    """
    if "cart-filters" in request.session:
        del request.session["cart-filters"]

    if request.REQUEST.get("came-from") == "cart":
        cart_id = request.REQUEST.get("cart-id")
        html = (
            ("#selectable-carts-inline", selectable_carts_inline(request, cart_id)),
            ("#cart-inline", cart_inline(request, cart_id)),
        )
    else:
        html = (("#carts-inline", carts_inline(request)),)

    msg = _(u"Cart filters has been reset")

    result = simplejson.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


# Private methods
def _get_filtered_carts(cart_filters):
    """
    """
    carts = Cart.objects.all().order_by("-modification_date")

    # start
    start = cart_filters.get("start", "")
    if start != "":
        s = lfs.core.utils.get_start_day(start)
    else:
        s = datetime.min

    # end
    end = cart_filters.get("end", "")
    if end != "":
        e = lfs.core.utils.get_end_day(end)
    else:
        e = datetime.max

    carts = carts.filter(modification_date__range=(s, e))

    return carts
