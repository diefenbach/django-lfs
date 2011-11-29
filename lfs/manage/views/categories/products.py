# django imports
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.signals import product_changed
from lfs.core.signals import category_changed
from lfs.core.utils import LazyEncoder
from lfs.catalog.settings import VARIANT
from lfs.catalog.models import Category
from lfs.catalog.models import Product


# Views
@permission_required("core.manage_shop", login_url="/login/")
def manage_products(request, category_id, template_name="manage/category/products.html"):
    """
    """
    category = Category.objects.get(pk=category_id)
    inline = products_inline(request, category_id, True)

    # amount options
    amount_options = []
    for value in (10, 25, 50, 100):
        amount_options.append({
            "value": value,
            "selected": value == request.session.get("category-products-amount")
        })

    return render_to_string(template_name, RequestContext(request, {
        "category": category,
        "products_inline": inline,
        "amount_options": amount_options,
    }))


# Parts
@permission_required("core.manage_shop", login_url="/login/")
def products_inline(request, category_id, as_string=False, template_name="manage/category/products_inline.html"):
    """Displays the products-tab of a category.

    This is called at start from the manage_products view to assemble the
    whole manage category view and is subsequently called via ajax requests to
    update this part independent of others.
    """
    category = Category.objects.get(pk=category_id)

    products = Product.objects.filter(categories=category)
    product_ids = [p.id for p in products]

    if request.REQUEST.get("keep-session"):
        page = request.REQUEST.get("page", request.session.get("page", 1))
        filter_ = request.REQUEST.get("filter", request.session.get("filter", ""))
        category_filter = request.REQUEST.get("category_filter", request.session.get("category_filter", ""))
    else:
        page = 1
        filter_ = ""
        category_filter = ""

    s = request.session
    s["page"] = page
    s["filter"] = filter_
    s["category_filter"] = category_filter

    try:
        s["category-products-amount"] = int(request.REQUEST.get("category-products-amount",
                                      s.get("category-products-amount")))
    except TypeError:
        s["category-products-amount"] = 25

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

    selectable_products = Product.objects.filter(
        filters).exclude(sub_type=VARIANT)

    paginator = Paginator(selectable_products.exclude(pk__in=product_ids), s["category-products-amount"])
    try:
        page = paginator.page(page)
    except:
        page = paginator.page(1)

    result = render_to_string(template_name, RequestContext(request, {
        "category": category,
        "paginator": paginator,
        "page": page,
        "selected_products": selected_products(request, category_id, as_string=True),
    }))

    if as_string:
        return result
    else:
        return HttpResponse(simplejson.dumps({
            "html": [["#products-inline", result]],
        }))


# Actions
@permission_required("core.manage_shop", login_url="/login/")
def products_tab(request, category_id):
    """Returns the products tab for given category id.
    """
    result = manage_products(request, category_id)
    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def selected_products(request, category_id, as_string=False, template_name="manage/category/selected_products.html"):
    """The selected products part of the products-tab of a category.

    This is called at start from the products_inline method to assemble the
    whole manage category view and is later called via ajax requests to update
    this part independent of others.
    """
    category = Category.objects.get(pk=category_id)

    if request.REQUEST.get("keep-session"):
        page_2 = request.REQUEST.get("page_2", request.session.get("page_2", 2))
        filter_2 = request.REQUEST.get("filter_2", request.session.get("filter_2", ""))
        category_filter_2 = request.REQUEST.get("category_filter_2", request.session.get("category_filter_2", ""))
    else:
        page_2 = 1
        filter_2 = ""
        category_filter_2 = ""

    request.session["page_2"] = page_2
    request.session["filter_2"] = filter_2

    try:
        request.session["category-products-amount"] = int(request.REQUEST.get("category-products-amount", request.session.get("category-products-amount")))
    except TypeError:
        request.session["category-products-amount"] = 25

    filters = Q(categories=category)
    if filter_2:
        filters &= (Q(name__icontains=filter_2) | Q(sku__icontains=filter_2))

    products = Product.objects.filter(filters).exclude(sub_type=VARIANT)

    paginator_2 = Paginator(products, request.session["category-products-amount"])
    try:
        page_2 = paginator_2.page(page_2)
    except:
        page_2 = paginator_2.page(1)

    result = render_to_string(template_name, RequestContext(request, {
        "category": category,
        "products": products,
        "paginator_2": paginator_2,
        "page_2": page_2,
        "filter_2": filter_2,
    }))

    if as_string:
        return result
    else:
        return HttpResponse(simplejson.dumps({
            "html": [["#selected-products", result]],
        }))


@permission_required("core.manage_shop", login_url="/login/")
def add_products(request, category_id):
    """Adds products (passed via request body) to category with passed id.
    """
    category = Category.objects.get(pk=category_id)

    for product_id in request.POST.keys():
        if product_id.startswith("page") or product_id.startswith("filter") or \
           product_id.startswith("keep-session") or product_id.startswith("action"):
            continue
        try:
            category.products.add(product_id)
        except IntegrityError:
            continue

        product = Product.objects.get(pk=product_id)
        product_changed.send(product)

    category_changed.send(category)

    html = [["#products-inline", products_inline(request, category_id, as_string=True)]]

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Selected products have been added to category.")
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def remove_products(request, category_id):
    """Removes product (passed via request body) from category with passed id.
    """
    category = Category.objects.get(pk=category_id)

    for product_id in request.POST.keys():

        if product_id.startswith("page") or product_id.startswith("filter") or \
           product_id.startswith("keep-session") or product_id.startswith("action"):
            continue

        product = Product.objects.get(pk=product_id)
        product_changed.send(product)

        category.products.remove(product_id)

    category_changed.send(category)

    html = [["#products-inline", products_inline(request, category_id, as_string=True)]]

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Selected products have been removed from category.")
    }, cls=LazyEncoder)

    return HttpResponse(result)
