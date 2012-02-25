# django imports
from django.contrib.auth.decorators import permission_required
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs.imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.settings import VARIANT
from lfs.core.signals import topseller_changed
from lfs.core.utils import LazyEncoder
from lfs.marketing.models import Topseller


@permission_required("core.manage_shop", login_url="/login/")
def manage_topseller(
    request, template_name="manage/marketing/topseller.html"):
    """
    """
    inline = manage_topseller_inline(request, as_string=True)

    # amount options
    amount_options = []
    for value in (10, 25, 50, 100):
        amount_options.append({
            "value": value,
            "selected": value == request.session.get("topseller-amount")
        })

    return render_to_string(template_name, RequestContext(request, {
        "topseller_inline": inline,
        "amount_options": amount_options,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def manage_topseller_inline(
    request, as_string=False, template_name="manage/marketing/topseller_inline.html"):
    """
    """
    topseller = Topseller.objects.all()
    topseller_ids = [t.product.id for t in topseller]

    r = request.REQUEST
    s = request.session

    # If we get the parameter ``keep-filters`` or ``page`` we take the
    # filters out of the request resp. session. The request takes precedence.
    # The page parameter is given if the user clicks on the next/previous page
    # links. The ``keep-filters`` parameters is given is the users adds/removes
    # products. In this way we keeps the current filters when we needed to. If
    # the whole page is reloaded there is no ``keep-filters`` or ``page`` and
    # all filters are reset as they should.

    if r.get("keep-filters") or r.get("page"):
        page = r.get("page", s.get("topseller_products_page", 1))
        filter_ = r.get("filter", s.get("filter"))
        category_filter = r.get("topseller_category_filter",
                          s.get("topseller_category_filter"))
    else:
        page = r.get("page", 1)
        filter_ = r.get("filter")
        category_filter = r.get("topseller_category_filter")

    # The current filters are saved in any case for later use.
    s["topseller_products_page"] = page
    s["filter"] = filter_
    s["topseller_category_filter"] = category_filter

    try:
        s["topseller-amount"] = int(r.get("topseller-amount",
                                      s.get("topseller-amount")))
    except TypeError:
        s["topseller-amount"] = 25

    filters = Q()
    if filter_:
        filters &= Q(name__icontains=filter_)
        filters |= Q(sku__icontains=filter_)
        filters |= (Q(sub_type=VARIANT) & Q(active_sku=False) & Q(parent__sku__icontains=filter_))
        filters |= (Q(sub_type=VARIANT) & Q(active_name=False) & Q(parent__name__icontains=filter_))

    if category_filter:
        if category_filter == "None":
            filters &= Q(categories=None)
        elif category_filter == "All":
            pass
        else:
            # First we collect all sub categories and using the `in` operator
            category = lfs_get_object_or_404(Category, pk=category_filter)
            categories = [category]
            categories.extend(category.get_all_children())
            filters &= Q(categories__in=categories)

    products = Product.objects.filter(filters).exclude(pk__in=topseller_ids)
    paginator = Paginator(products, s["topseller-amount"])

    total = products.count()
    try:
        page = paginator.page(page)
    except EmptyPage:
        page = 0

    result = render_to_string(template_name, RequestContext(request, {
        "topseller": topseller,
        "total": total,
        "page": page,
        "paginator": paginator,
        "filter": filter_
    }))

    if as_string:
        return result
    else:
        return HttpResponse(
            simplejson.dumps({
                "html": [["#topseller-inline", result]],
            }))


# Actions
@permission_required("core.manage_shop", login_url="/login/")
def add_topseller(request):
    """Adds topseller by given ids (within request body).
    """
    for temp_id in request.POST.keys():

        if temp_id.startswith("product") == False:
            continue

        temp_id = temp_id.split("-")[1]
        Topseller.objects.create(product_id=temp_id)

    _update_positions()
    html = [["#topseller-inline", manage_topseller_inline(request, as_string=True)]]
    result = simplejson.dumps({
        "html": html,
        "message": _(u"Topseller have been added.")
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def update_topseller(request):
    """Saves or removes passed topsellers passed id (within request body).
    """
    if request.POST.get("action") == "remove":
        for temp_id in request.POST.keys():

            if temp_id.startswith("product") == False:
                continue

            temp_id = temp_id.split("-")[1]
            try:
                topseller = Topseller.objects.get(pk=temp_id)
                topseller.delete()
            except (Topseller.DoesNotExist, ValueError):
                pass

            _update_positions()
            topseller_changed.send(topseller)

        html = [["#topseller-inline", manage_topseller_inline(request, as_string=True)]]
        result = simplejson.dumps({
            "html": html,
            "message": _(u"Topseller have been removed.")
        }, cls=LazyEncoder)

    else:
        for temp_id in request.POST.keys():

            if temp_id.startswith("position") == False:
                continue

            temp_id = temp_id.split("-")[1]
            topseller = Topseller.objects.get(pk=temp_id)

            # Update position
            position = request.POST.get("position-%s" % temp_id)
            topseller.position = position
            topseller.save()

        _update_positions()
        html = [["#topseller-inline", manage_topseller_inline(request, as_string=True)]]
        result = simplejson.dumps({
            "html": html,
            "message": _(u"Topseller have been updated.")
        }, cls=LazyEncoder)

    return HttpResponse(result)


def _update_positions():
    for i, topseller in enumerate(Topseller.objects.all()):
        topseller.position = (i + 1)
        topseller.save()
