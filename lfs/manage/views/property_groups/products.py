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

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.models import PropertyGroup
from lfs.catalog.models import ProductPropertyValue
from lfs.core.utils import LazyEncoder
from lfs.core.signals import product_removed_property_group


@permission_required("core.manage_shop", login_url="/login/")
def products(request, product_group_id, template_name="manage/properties/pg_products.html"):
    """Renders the products tab of the property groups management views.
    """
    property_group = PropertyGroup.objects.get(pk=product_group_id)
    inline = products_inline(request, product_group_id, as_string=True)

    return render_to_string(template_name, RequestContext(request, {
        "property_group": property_group,
        "products_inline": inline,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def products_inline(request, product_group_id, as_string=False,
    template_name="manage/properties/pg_products_inline.html"):
    """Renders the products tab of the property groups management views.
    """
    property_group = PropertyGroup.objects.get(pk=product_group_id)
    group_products = property_group.products.all()
    group_product_ids = [p.id for p in group_products]

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
        page = r.get("page", s.get("property_group_page", 1))
        filter_ = r.get("filter", s.get("filter"))
        category_filter = r.get("products_category_filter",
                          s.get("products_category_filter"))
    else:
        page = r.get("page", 1)
        filter_ = r.get("filter")
        category_filter = r.get("products_category_filter")

    # The current filters are saved in any case for later use.
    s["property_group_page"] = page
    s["filter"] = filter_
    s["products_category_filter"] = category_filter

    filters = Q()
    if filter_:
        filters &= Q(name__icontains=filter_)
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

    products = Product.objects.filter(filters)
    paginator = Paginator(products.exclude(pk__in=group_product_ids), 25)

    try:
        page = paginator.page(page)
    except EmptyPage:
        page = 0

    result = render_to_string(template_name, RequestContext(request, {
        "property_group": property_group,
        "group_products": group_products,
        "page": page,
        "paginator": paginator,
        "filter": filter_
    }))

    if as_string:
        return result
    else:
        return HttpResponse(
            simplejson.dumps({
                "html": [["#products-inline", result]],
            }))


@permission_required("core.manage_shop", login_url="/login/")
def assign_products(request, group_id):
    """Assign products to given property group with given property_group_id.
    """
    property_group = lfs_get_object_or_404(PropertyGroup, pk=group_id)

    for temp_id in request.POST.keys():
        if temp_id.startswith("product"):
            temp_id = temp_id.split("-")[1]
            product = Product.objects.get(pk=temp_id)
            property_group.products.add(product)

    html = [["#products-inline", products_inline(request, group_id, as_string=True)]]
    result = simplejson.dumps({
        "html": html,
        "message": _(u"Products have been assigned.")
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def remove_products(request, group_id):
    """Remove products from given property group with given property_group_id.
    """
    property_group = lfs_get_object_or_404(PropertyGroup, pk=group_id)

    for temp_id in request.POST.keys():
        if temp_id.startswith("product"):
            temp_id = temp_id.split("-")[1]
            product = Product.objects.get(pk=temp_id)
            property_group.products.remove(product)

            # Notify removing
            product_removed_property_group.send([property_group, product])

    html = [["#products-inline", products_inline(request, group_id, as_string=True)]]
    result = simplejson.dumps({
        "html": html,
        "message": _(u"Products have been removed.")
    }, cls=LazyEncoder)

    return HttpResponse(result)
