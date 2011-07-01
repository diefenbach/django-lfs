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
from lfs.catalog.models import ProductAccessories
from lfs.catalog.settings import VARIANT
from lfs.core.signals import product_changed
from lfs.core.utils import LazyEncoder


@permission_required("core.manage_shop", login_url="/login/")
def manage_accessories(request, product_id, template_name="manage/product/accessories.html"):
    """
    """
    product = Product.objects.get(pk=product_id)
    inline = manage_accessories_inline(request, product_id, as_string=True)

    # amount options
    amount_options = []
    for value in (10, 25, 50, 100):
        amount_options.append({
            "value": value,
            "selected": value == request.session.get("accessories-amount")
        })

    return render_to_string(template_name, RequestContext(request, {
        "product": product,
        "accessories_inline": inline,
        "amount_options": amount_options,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def manage_accessories_inline(request, product_id, as_string=False, template_name="manage/product/accessories_inline.html"):
    """View which shows all accessories for the product with the passed id.
    """
    product = Product.objects.get(pk=product_id)
    product_accessories = ProductAccessories.objects.filter(product=product_id)
    accessory_ids = [p.accessory.id for p in product_accessories]

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
        page = r.get("page", s.get("accessories_page", 1))
        filter_ = r.get("filter", s.get("filter"))
        category_filter = r.get("accessories_category_filter",
                          s.get("accessories_category_filter"))
    else:
        page = r.get("page", 1)
        filter_ = r.get("filter")
        category_filter = r.get("accessories_category_filter")

    # The current filters are saved in any case for later use.
    s["accessories_page"] = page
    s["filter"] = filter_
    s["accessories_category_filter"] = category_filter

    try:
        s["accessories-amount"] = int(r.get("accessories-amount",
                                      s.get("accessories-amount")))
    except TypeError:
        s["accessories-amount"] = 25

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

    products = Product.objects.filter(filters).exclude(pk=product_id)

    paginator = Paginator(products.exclude(pk__in=accessory_ids), s["accessories-amount"])

    try:
        page = paginator.page(page)
    except EmptyPage:
        page = 0

    result = render_to_string(template_name, RequestContext(request, {
        "product": product,
        "product_accessories": product_accessories,
        "page": page,
        "paginator": paginator,
        "filter": filter_,
    }))

    if as_string:
        return result
    else:
        return HttpResponse(
            simplejson.dumps({
                "html": [["#accessories-inline", result]],
            }))


# Actions
@permission_required("core.manage_shop", login_url="/login/")
def load_tab(request, product_id):
    """
    """
    accessories = manage_accessories(request, product_id)
    return HttpResponse(accessories)


@permission_required("core.manage_shop", login_url="/login/")
def add_accessories(request, product_id):
    """Adds passed accessories to product with passed id.
    """
    parent_product = Product.objects.get(pk=product_id)

    for temp_id in request.POST.keys():

        if temp_id.startswith("product") == False:
            continue

        temp_id = temp_id.split("-")[1]
        accessory = Product.objects.get(pk=temp_id)
        product_accessory = ProductAccessories(product=parent_product, accessory=accessory)
        product_accessory.save()

    _update_positions(parent_product)
    product_changed.send(parent_product)

    html = [["#accessories-inline", manage_accessories_inline(request, product_id, as_string=True)]]

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Accessories have been added.")
    }, cls=LazyEncoder)

    return HttpResponse(result)


# TODO: Rename to "update_accessories"
@permission_required("core.manage_shop", login_url="/login/")
def remove_accessories(request, product_id):
    """Removes passed accessories from product with passed id.
    """
    parent_product = Product.objects.get(pk=product_id)

    if request.POST.get("action") == "remove":
        for temp_id in request.POST.keys():

            if temp_id.startswith("accessory") == False:
                continue

            temp_id = temp_id.split("-")[1]
            accessory = Product.objects.get(pk=temp_id)
            product_accessory = ProductAccessories.objects.filter(product=parent_product, accessory=accessory)

            product_accessory.delete()

        _update_positions(parent_product)
        product_changed.send(parent_product)

        html = [["#accessories-inline", manage_accessories_inline(request, product_id, as_string=True)]]

        result = simplejson.dumps({
            "html": html,
            "message": _(u"Accessories have been removed.")
        }, cls=LazyEncoder)

    else:
        for temp_id in request.POST.keys():

            if temp_id.startswith("quantity") == False:
                continue

            temp_id = temp_id.split("-")[1]
            accessory = Product.objects.get(pk=temp_id)
            product_accessory = ProductAccessories.objects.get(product=parent_product, accessory=accessory)

            # Update quantity
            quantity = request.POST.get("quantity-%s" % temp_id)
            product_accessory.quantity = quantity

            # Update position
            position = request.POST.get("position-%s" % temp_id)
            product_accessory.position = position

            product_accessory.save()

            product_changed.send(product_accessory.product)

        _update_positions(parent_product)

        html = [["#accessories-inline", manage_accessories_inline(request, product_id, as_string=True)]]
        result = simplejson.dumps({
            "html": html,
            "message": _(u"Accessories have been updated.")
        }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def update_accessories(request, product_id):
    """Updates the accessories activity state for product variants.
    """
    product = Product.objects.get(pk=product_id)
    if request.POST.get("active_accessories"):
        product.active_accessories = True
    else:
        product.active_accessories = False
    product.save()

    html = [["#accessories-inline", manage_accessories_inline(request, product_id, as_string=True)]]
    result = simplejson.dumps({
        "html": html,
        "message": _(u"Accessories have been updated.")
    }, cls=LazyEncoder)

    return HttpResponse(result)


def _update_positions(product):
    """Updates positions of product accessories for given product.
    """
    for i, pa in enumerate(ProductAccessories.objects.filter(product=product)):
        pa.position = (i + 1) * 10
        pa.save()
