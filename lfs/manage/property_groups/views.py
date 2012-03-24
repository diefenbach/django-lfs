# django imports
from django.contrib.auth.decorators import permission_required
from django.db import IntegrityError
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category
from lfs.catalog.models import GroupsPropertiesRelation
from lfs.catalog.models import Product
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyGroup
from lfs.core.utils import LazyEncoder
from lfs.core.signals import product_removed_property_group
from lfs.manage.property_groups.forms import PropertyGroupForm


@permission_required("core.manage_shop", login_url="/login/")
def manage_property_groups(request):
    """The main view to manage properties.
    """
    try:
        property = PropertyGroup.objects.all()[0]
        url = reverse("lfs_manage_property_group", kwargs={"id": property.id})
    except IndexError:
        url = reverse("lfs_manage_no_property_groups")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop", login_url="/login/")
def manage_property_group(request, id, template_name="manage/property_groups/property_group.html"):
    """Edits property group with given id.
    """
    property_group = get_object_or_404(PropertyGroup, pk=id)
    if request.method == "POST":
        form = PropertyGroupForm(instance=property_group, data=request.POST)
        if form.is_valid():
            form.save()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_property_group", kwargs={"id": property_group.id}),
                msg=_(u"Property group has been saved."),
            )
    else:
        form = PropertyGroupForm(instance=property_group)

    return render_to_response(template_name, RequestContext(request, {
        "property_group": property_group,
        "property_groups": PropertyGroup.objects.all(),
        "properties": properties_inline(request, id),
        "products": products_tab(request, id),
        "form": form,
        "current_id": int(id),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def no_property_groups(request, template_name="manage/property_groups/no_property_groups.html"):
    """Displays that there are no property groups.
    """
    return render_to_response(template_name, RequestContext(request, {}))


@permission_required("core.manage_shop", login_url="/login/")
def properties_inline(request, id, template_name="manage/property_groups/properties_inline.html"):
    """
    """
    property_group = get_object_or_404(PropertyGroup, pk=id)

    gps = GroupsPropertiesRelation.objects.filter(group=id)

    # Calculate assignable properties
    assigned_property_ids = [p.property.id for p in gps]
    assignable_properties = Property.objects.exclude(
        pk__in=assigned_property_ids).exclude(local=True)

    return render_to_string(template_name, RequestContext(request, {
        "property_group": property_group,
        "properties": assignable_properties,
        "gps": gps,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def add_property_group(request, template_name="manage/property_groups/add_property_group.html"):
    """Adds a new property group
    """
    if request.method == "POST":
        form = PropertyGroupForm(data=request.POST)
        if form.is_valid():
            property_group = form.save()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_property_group", kwargs={"id": property_group.id}),
                msg=_(u"Property group has been added."),
            )
    else:
        form = PropertyGroupForm()

    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "property_groups": PropertyGroup.objects.all(),
        "came_from": request.REQUEST.get("came_from", reverse("lfs_manage_property_groups")),
    }))


@permission_required("core.manage_shop", login_url="/login/")
@require_POST
def delete_property_group(request, id):
    """Deletes the property group with passed id.
    """
    property_group = get_object_or_404(PropertyGroup, pk=id)
    property_group.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_property_groups"),
        msg=_(u"Property group has been deleted."),
    )


@permission_required("core.manage_shop", login_url="/login/")
def assign_properties(request, group_id):
    """Assignes given properties (via request body) to passed group id.
    """
    for property_id in request.POST.getlist("property-id"):
        try:
            GroupsPropertiesRelation.objects.create(group_id=group_id, property_id=property_id)
        except IntegrityError:
            pass

    _udpate_positions(group_id)

    html = [["#properties", properties_inline(request, group_id)]]
    result = simplejson.dumps({
        "html": html,
        "message": _(u"Properties have been assigned.")
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def update_properties(request, group_id):
    """Update or Removes given properties (via request body) from passed group id.
    """
    if request.POST.get("action") == "remove":
        for property_id in request.POST.getlist("property-id"):
            try:
                gp = GroupsPropertiesRelation.objects.get(group=group_id, property=property_id)
            except GroupsPropertiesRelation.DoesNotExist:
                pass
            else:
                gp.delete()

        message = _(u"Properties have been removed.")

    else:
        message = _(u"There are no properties to update.")
        for gp in GroupsPropertiesRelation.objects.filter(group=group_id):
            position = request.POST.get("position-%s" % gp.property.id, 999)
            gp.position = int(position)
            gp.save()
            message = _(u"Properties have been updated.")

    _udpate_positions(group_id)

    html = [["#properties", properties_inline(request, group_id)]]
    result = simplejson.dumps({
        "html": html,
        "message": message
    }, cls=LazyEncoder)

    return HttpResponse(result)


# Product tab
@permission_required("core.manage_shop", login_url="/login/")
def products_tab(request, product_group_id, template_name="manage/property_groups/products.html"):
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
    template_name="manage/property_groups/products_inline.html"):
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


def _udpate_positions(group_id):
    """
    """
    for i, gp in enumerate(GroupsPropertiesRelation.objects.filter(group=group_id)):
        gp.position = (i + 1) * 10
        gp.save()
