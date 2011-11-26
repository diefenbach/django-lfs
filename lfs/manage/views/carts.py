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


@permission_required("core.manage_shop", login_url="/login/")
def carts_view(request, template_name="manage/cart/carts.html"):
    """Base view to display carts overview.
    """
    return render_to_response(template_name, RequestContext(request, {
        "carts_inline": carts_inline(request, as_string=True),
    }))


def carts_inline(request, as_string=False, template_name="manage/cart/carts_inline.html"):
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

    result = render_to_string(template_name, RequestContext(request, {
        "carts": carts,
        "page": page,
        "paginator": paginator,
        "start": cart_filters.get("start", ""),
        "end": cart_filters.get("end", ""),
    }))

    if as_string:
        return result
    else:
        html = (("#carts-inline", result),)

        result = simplejson.dumps({
            "html": html,
        }, cls=LazyEncoder)

        return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def cart_view(request, cart_id, template_name="manage/cart/cart.html"):
    """Displays cart with provided cart id.
    """
    return render_to_response(template_name, RequestContext(request, {
        "cart_inline": cart_inline(request, cart_id, as_string=True),
        "selectable_carts_inline": selectable_carts_inline(request, cart_id, as_string=True),
    }))


def cart_inline(request, cart_id, as_string=False, template_name="manage/cart/cart_inline.html"):
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
    result = render_to_string(template_name, RequestContext(request, {
        "cart": cart,
        "customer": customer,
        "total": total,
        "start": cart_filters.get("start", ""),
        "end": cart_filters.get("end", ""),
    }))

    if as_string:
        return result
    else:
        html = (("#cart-inline", result),)

        result = simplejson.dumps({
            "html": html,
        }, cls=LazyEncoder)

        return HttpResponse(result)


def selectable_carts_inline(request, cart_id=0, as_string=False,
    template_name="manage/cart/selectable_carts_inline.html"):
    """Display selectable carts.
    """
    cart_filters = request.session.get("cart-filters", {})
    carts = _get_filtered_carts(cart_filters)

    paginator = Paginator(carts, 30)

    try:
        page = int(request.REQUEST.get("page", 1))
    except TypeError:
        page = 1
    page = paginator.page(page)

    result = render_to_string(template_name, RequestContext(request, {
        "paginator": paginator,
        "page": page,
        "cart_id": int(cart_id),
    }))

    if as_string:
        return result
    else:
        result = simplejson.dumps({
            "html": (("#selectable-carts-inline", result),),
        }, cls=LazyEncoder)

        return HttpResponse(result)


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
            ("#selectable-carts-inline", selectable_carts_inline(request, as_string=True)),
            ("#cart-inline", cart_inline(request, cart_id=cart_id, as_string=True)),
        )
    else:
        html = (("#carts-inline", carts_inline(request, as_string=True)),)

    msg = _(u"Cart filters has been set.")

    result = simplejson.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


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
            ("#selectable-carts-inline", selectable_carts_inline(request, as_string=True)),
            ("#cart-inline", cart_inline(request, cart_id=cart_id, as_string=True)),
        )
    else:
        html = (("#carts-inline", carts_inline(request, as_string=True)),)

    msg = _(u"Cart filters has been set")

    result = simplejson.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


def reset_cart_filters(request):
    """Resets all cart filters.
    """
    if "cart-filters" in request.session:
        del request.session["cart-filters"]

    if request.REQUEST.get("came-from") == "cart":
        cart_id = request.REQUEST.get("cart-id")
        html = (
            ("#selectable-carts-inline", selectable_carts_inline(request, as_string=True)),
            ("#cart-inline", cart_inline(request, cart_id=cart_id, as_string=True)),
        )
    else:
        html = (("#carts-inline", carts_inline(request, as_string=True)),)

    msg = _(u"Cart filters has been reset")

    result = simplejson.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


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
