import json

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
from lfs.catalog.models import Category, Product
import lfs.core.utils
import lfs.criteria.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder
from lfs.discounts.models import Discount
from lfs.manage.discounts.forms import DiscountForm
from lfs.manufacturer.models import Manufacturer


@permission_required("core.manage_shop")
def manage_discounts(request):
    """Dispatches to the first discount or to the add discount method
    form if there is no discount yet.
    """
    try:
        discount = Discount.objects.all()[0]
    except IndexError:
        url = reverse("lfs_manage_no_discounts")
    else:
        url = reverse("lfs_manage_discount", kwargs={"id": discount.id})

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
def manage_discount(request, id, template_name="manage/discounts/discount.html"):
    """The main view to manage the discount with given id.

    This view collects the various parts of the discount form (data, criteria,
    and displays them.
    """
    try:
        discount = Discount.objects.get(pk=id)
    except Discount.DoesNotExist:
        return HttpResponseRedirect(reverse("lfs_manage_discounts"))

    return render(request, template_name, {
        "discount": discount,
        "navigation": navigation(request),
        "data": discount_data(request, id),
        "products": products_tab(request, id),
        "criteria": discount_criteria(request, id),
    })


@permission_required("core.manage_shop")
def no_discounts(request, template_name="manage/discounts/no_discounts.html"):
    """Displays no discounts view
    """
    return render(request, template_name, {})


# Parts of the manage discount view.
@permission_required("core.manage_shop")
def navigation(request, template_name="manage/discounts/navigation.html"):
    """Returns the navigation for the discount view.
    """
    try:
        current_id = int(request.path.split("/")[-1])
    except ValueError:
        current_id = ""

    return render_to_string(template_name, request=request, context={
        "current_id": current_id,
        "discounts": Discount.objects.all(),
    })


@permission_required("core.manage_shop")
def discount_data(request, id, template_name="manage/discounts/data.html"):
    """Returns the discount data as html.

    This view is used as a part within the manage discount view.
    """
    discount = Discount.objects.get(pk=id)

    return render_to_string(template_name, request=request, context={
        "form": DiscountForm(instance=discount),
        "discount": discount,
    })


@permission_required("core.manage_shop")
def discount_criteria(request, id, template_name="manage/discounts/criteria.html"):
    """Returns the criteria of the discount with passed id as HTML.

    This view is used as a part within the manage discount view.
    """
    discount = Discount.objects.get(pk=id)

    criteria = []
    position = 0
    for criterion_object in discount.get_criteria():
        position += 10
        criterion_html = criterion_object.get_content_object().render(request, position)
        criteria.append(criterion_html)

    return render_to_string(template_name, request=request, context={
        "discount": discount,
        "criteria": criteria,
    })


# Actions
@permission_required("core.manage_shop")
def add_discount(request, template_name="manage/discounts/add_discount.html"):
    """Provides an add form and saves a new discount method.
    """
    if request.method == "POST":
        form = DiscountForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_discount = form.save()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_discount", kwargs={"id": new_discount.id}),
                msg=_(u"Discount method has been added."),
            )
    else:
        form = DiscountForm()

    return render(request, template_name, {
        "navigation": navigation(request),
        "form": form,
        "came_from": (request.POST if request.method == 'POST' else request.GET).get("came_from", reverse("lfs_manage_discounts")),
    })


@permission_required("core.manage_shop")
def save_discount_criteria(request, id):
    """Saves the criteria for the discount with given id. The criteria
    are passed via request body.
    """
    discount = lfs_get_object_or_404(Discount, pk=id)
    discount.save_criteria(request)

    html = [["#criteria", discount_criteria(request, id)]]

    result = json.dumps({
        "html": html,
        "message": _("Changes have been saved."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def save_discount_data(request, id):
    """Saves discount data (via request body) to the discount with passed
    id.

    This is called via an AJAX request and returns JSON encoded data.
    """
    discount = Discount.objects.get(pk=id)
    discount_form = DiscountForm(instance=discount, data=request.POST)

    if discount_form.is_valid():
        discount_form.save()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_discount", kwargs={"id": id}),
        msg=_(u"Discount data has been saved."),
    )


@permission_required("core.manage_shop")
@require_POST
def delete_discount(request, id):
    """Deletes discount with passed id.
    """
    try:
        discount = Discount.objects.get(pk=id)
    except ObjectDoesNotExist:
        pass
    else:
        discount.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_discounts"),
        msg=_(u"Discount has been deleted."),
    )


@permission_required("core.manage_shop")
def assign_products(request, discount_id):
    """Assign products to given property group with given property_group_id.
    """
    discount = lfs_get_object_or_404(Discount, pk=discount_id)

    for temp_id in request.POST.keys():
        if temp_id.startswith("product"):
            temp_id = temp_id.split("-")[1]
            product = Product.objects.get(pk=temp_id)
            discount.products.add(product)

    html = [["#products-inline", products_inline(request, discount_id, as_string=True)]]
    result = json.dumps({
        "html": html,
        "message": _(u"Products have been assigned.")
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def remove_products(request, discount_id):
    """Remove products from given property group with given property_group_id.
    """
    discount = lfs_get_object_or_404(Discount, pk=discount_id)

    for temp_id in request.POST.keys():
        if temp_id.startswith("product"):
            temp_id = temp_id.split("-")[1]
            product = Product.objects.get(pk=temp_id)
            discount.products.remove(product)

    html = [["#products-inline", products_inline(request, discount_id, as_string=True)]]
    result = json.dumps({
        "html": html,
        "message": _(u"Products have been removed.")
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def products_tab(request, discount_id, template_name="manage/discounts/products.html"):
    """Renders the products tab of the property groups management views.
    """
    discount = Discount.objects.get(pk=discount_id)
    inline = products_inline(request, discount_id, as_string=True)

    return render_to_string(template_name, request=request, context={
        "discount": discount,
        "products_inline": inline,
    })


@permission_required("core.manage_shop")
def products_inline(request, discount_id, as_string=False,
                    template_name="manage/discounts/products_inline.html"):
    """Renders the products tab of the property groups management views.
    """
    discount = Discount.objects.get(pk=discount_id)
    discount_products = discount.products.all().select_related('parent')

    r = request.POST if request.method == 'POST' else request.GET
    s = request.session

    # If we get the parameter ``keep-filters`` or ``page`` we take the
    # filters out of the request resp. session. The request takes precedence.
    # The page parameter is given if the user clicks on the next/previous page
    # links. The ``keep-filters`` parameters is given is the users adds/removes
    # products. In this way we keeps the current filters when we needed to. If
    # the whole page is reloaded there is no ``keep-filters`` or ``page`` and
    # all filters are reset as they should.

    if r.get("keep-filters") or r.get("page"):
        page = r.get("page", s.get("discount_page", 1))
        filter_ = r.get("filter", s.get("filter"))
        category_filter = r.get("products_category_filter",
                                s.get("products_category_filter"))
        manufacturer_filter = r.get("products_manufacturer_filter",
                                    s.get("products_manufacturer_filter"))
    else:
        page = r.get("page", 1)
        filter_ = r.get("filter")
        category_filter = r.get("products_category_filter")
        manufacturer_filter = r.get("products_manufacturer_filter")

    # The current filters are saved in any case for later use.
    s["discount_page"] = page
    s["filter"] = filter_
    s["products_category_filter"] = category_filter
    s["products_manufacturer_filter"] = manufacturer_filter

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

    if manufacturer_filter:
        if manufacturer_filter == "None":
            filters &= Q(manufacturer=None)
        elif manufacturer_filter == "All":
            pass
        else:
            # First we collect all sub categories and using the `in` operator
            manufacturer = lfs_get_object_or_404(Manufacturer, pk=manufacturer_filter)
            filters &= Q(manufacturer=manufacturer)

    products = Product.objects.select_related('parent').filter(filters)
    paginator = Paginator(products.exclude(pk__in=discount_products), 25)

    try:
        page = paginator.page(page)
    except EmptyPage:
        page = 0

    result = render_to_string(template_name, request=request, context={
        "discount": discount,
        "discount_products": discount_products,
        "page": page,
        "paginator": paginator,
        "filter": filter_
    })

    if as_string:
        return result
    else:
        return HttpResponse(
            json.dumps({
                "html": [["#products-inline", result]],
            }), content_type='application/json')
