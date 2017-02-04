import json

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.signals import product_changed
from lfs.core.signals import manufacturer_changed
from lfs.core.utils import LazyEncoder
from lfs.catalog.settings import VARIANT
from lfs.catalog.models import Category
from lfs.catalog.models import Product

# Views
from lfs.manufacturer.models import Manufacturer


@permission_required("core.manage_shop")
def manage_products(request, manufacturer_id, template_name="manage/manufacturers/products.html"):
    """
    """
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)
    inline = products_inline(request, manufacturer_id, True)

    # amount options
    amount_options = []
    for value in (10, 25, 50, 100):
        amount_options.append({
            "value": value,
            "selected": value == request.session.get("manufacturer-products-amount")
        })

    return render_to_string(template_name, request=request, context={
        "manufacturer": manufacturer,
        "products_inline": inline,
        "amount_options": amount_options,
    })


# Parts
@permission_required("core.manage_shop")
def products_inline(request, manufacturer_id, as_string=False, template_name="manage/manufacturers/products_inline.html"):
    """Displays the products-tab of a manufacturer.

    This is called at start from the manage_products view to assemble the
    whole manage manufacturer view and is subsequently called via ajax requests to
    update this part independent of others.
    """
    req = request.POST if request.method == 'POST' else request.GET
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)

    if req.get("keep-session"):
        page = req.get("manufacturer_page", request.session.get("manufacturer_page", 1))
        filter_ = req.get("manufacturer_filter", request.session.get("manufacturer_filter", ""))
        category_filter = req.get("manufacturer_category_filter", request.session.get("manufacturer_category_filter", ""))
    else:
        page = 1
        filter_ = ""
        category_filter = ""

    s = request.session
    s["manufacturer_page"] = page
    s["manufacturer_filter"] = filter_
    s["manufacturer_category_filter"] = category_filter

    try:
        s["manufacturer-products-amount"] = int(req.get("manufacturer-products-amount", s.get("manufacturer-products-amount")))
    except TypeError:
        s["manufacturer-products-amount"] = 25

    filters = Q()
    if filter_:
        filters &= (Q(name__icontains=filter_) | Q(sku__icontains=filter_))
    if category_filter:
        if category_filter == "None":
            filters &= Q(categories=None)
        elif category_filter == "All":
            pass
        else:
            category_temp = lfs_get_object_or_404(Category, pk=category_filter)
            categories_temp = [category_temp]
            categories_temp.extend(category_temp.get_all_children())

            filters &= Q(categories__in=categories_temp)

    selectable_products = Product.objects.filter(filters).exclude(sub_type=VARIANT).exclude(manufacturer=manufacturer).distinct()

    paginator = Paginator(selectable_products, s["manufacturer-products-amount"])
    try:
        page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page = paginator.page(1)

    result = render_to_string(template_name, request=request, context={
        "manufacturer": manufacturer,
        "paginator": paginator,
        "page": page,
        "selected_products": selected_products(request, manufacturer_id, as_string=True),
    })

    if as_string:
        return result
    else:
        return HttpResponse(json.dumps({
            "html": [["#products-inline", result]],
        }), content_type='application/json')


# Actions
@permission_required("core.manage_shop")
def products_tab(request, manufacturer_id):
    """Returns the products tab for given manufacturer id.
    """
    result = manage_products(request, manufacturer_id)
    return HttpResponse(result)


@permission_required("core.manage_shop")
def selected_products(request, manufacturer_id, as_string=False, template_name="manage/manufacturers/selected_products.html"):
    """The selected products part of the products-tab of a manufacturer.

    This is called at start from the products_inline method to assemble the
    whole manage category view and is later called via ajax requests to update
    this part independent of others.
    """
    req = request.POST if request.method == 'POST' else request.GET
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)

    if req.get("keep-session"):
        page_2 = req.get("manufacturer_page_2", request.session.get("manufacturer_page_2", 2))
        filter_2 = req.get("manufacturer_filter_2", request.session.get("manufacturer_filter_2", ""))
    else:
        page_2 = 1
        filter_2 = ""

    request.session["manufacturer_page_2"] = page_2
    request.session["manufacturer_filter_2"] = filter_2

    try:
        request.session["manufacturer-products-amount"] = int(req.get("manufacturer-products-amount", request.session.get("manufacturer-products-amount")))
    except TypeError:
        request.session["manufacturer-products-amount"] = 25

    filters = Q(manufacturer=manufacturer)
    if filter_2:
        filters &= (Q(name__icontains=filter_2) | Q(sku__icontains=filter_2))

    products = Product.objects.filter(filters).exclude(sub_type=VARIANT).distinct()

    paginator_2 = Paginator(products, request.session["manufacturer-products-amount"])
    try:
        page_2 = paginator_2.page(page_2)
    except (EmptyPage, InvalidPage):
        page_2 = paginator_2.page(1)

    result = render_to_string(template_name, request=request, context={
        "manufacturer": manufacturer,
        "products": products,
        "paginator_2": paginator_2,
        "page_2": page_2,
        "filter_2": filter_2,
    })

    if as_string:
        return result
    else:
        return HttpResponse(json.dumps({
            "html": [["#selected-products", result]],
        }), content_type='application/json')


@permission_required("core.manage_shop")
def add_products(request, manufacturer_id):
    """Adds products (passed via request body) to category with passed id.
    """
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)

    for product_id in request.POST.keys():
        if product_id.startswith("manufacturer_page") or product_id.startswith("manufacturer_filter") or \
           product_id.startswith("keep-session") or product_id.startswith("action"):
            continue

        try:
            product = Product.objects.get(pk=product_id)
            product.manufacturer = manufacturer
            product.save()
            product_changed.send(product)
        except Product.DoesNotExist:
            continue
    manufacturer_changed.send(manufacturer)

    html = [["#products-inline", products_inline(request, manufacturer_id, as_string=True)]]

    result = json.dumps({
        "html": html,
        "message": _(u"Selected products have been assigned to manufacturer.")
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def remove_products(request, manufacturer_id):
    """Removes product (passed via request body) from category with passed id.
    """
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)

    for product_id in request.POST.keys():
        if product_id.startswith("manufacturer_page") or product_id.startswith("manufacturer_filter") or \
           product_id.startswith("keep-session") or product_id.startswith("action"):
            continue

        product = Product.objects.get(pk=product_id)
        product.manufacturer = None
        product.save()
        product_changed.send(product)
    manufacturer_changed.send(manufacturer)

    html = [["#products-inline", products_inline(request, manufacturer_id, as_string=True)]]

    result = json.dumps({
        "html": html,
        "message": _(u"Selected products are no longer assigned to manufacturer.")
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')
