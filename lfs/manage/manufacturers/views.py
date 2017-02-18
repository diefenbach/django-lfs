import json

from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache

from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.core.utils import LazyEncoder
from lfs.manage.manufacturers.forms import ManufacturerDataForm, ManufacturerAddForm
from lfs.manufacturer.models import Manufacturer
from lfs.manage.manufacturers.forms import ViewForm
from lfs.manage.seo.views import SEOView

import logging
logger = logging.getLogger(__name__)


@permission_required("core.manage_shop")
def manage_manufacturer(request, manufacturer_id, template_name="manage/manufacturers/manufacturer.html"):
    """The main view to display manufacturers.
    """
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)

    categories = []
    for category in Category.objects.filter(parent=None):

        # Checking state
        checked, klass = _get_category_state(manufacturer, category)

        categories.append({
            "id": category.id,
            "name": category.name,
            "checked": checked,
            "klass": klass,
        })

    render(request, template_name, {
        "categories": categories,
        "manufacturer": manufacturer,
        "manufacturer_id": manufacturer_id,
        "selectable_manufacturers_inline": selectable_manufacturers_inline(request, manufacturer_id),
        "manufacturer_data_inline": manufacturer_data_inline(request, manufacturer_id),
        "seo": SEOView(Manufacturer).render(request, manufacturer),
        "view": manufacturer_view(request, manufacturer_id),
    })


@permission_required("core.manage_shop")
def no_manufacturers(request, template_name="manage/manufacturers/no_manufacturers.html"):
    """Displays that there are no manufacturers.
    """
    return render(request, template_name, {})


# Parts
def manufacturer_data_inline(request, manufacturer_id,
                             template_name="manage/manufacturers/manufacturer_data_inline.html"):
    """Displays the data form of the current manufacturer.
    """
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)
    if request.method == "POST":
        form = ManufacturerDataForm(instance=manufacturer, data=request.POST)
    else:
        form = ManufacturerDataForm(instance=manufacturer)
    return render_to_string(template_name, request=request, context={
        "manufacturer": manufacturer,
        "form": form,
    })


@permission_required("core.manage_shop")
def manufacturer_view(request, manufacturer_id, template_name="manage/manufacturers/view.html"):
    """Displays the view data for the manufacturer with passed manufacturer id.

    This is used as a part of the whole category form.
    """
    manufacturer = lfs_get_object_or_404(Manufacturer, pk=manufacturer_id)

    if request.method == "POST":
        form = ViewForm(instance=manufacturer, data=request.POST)
        if form.is_valid():
            form.save()
            message = _(u"View data has been saved.")
        else:
            message = _(u"Please correct the indicated errors.")
    else:
        form = ViewForm(instance=manufacturer)

    view_html = render_to_string(template_name, request=request, context={
        "manufacturer": manufacturer,
        "form": form,
    })

    if request.is_ajax():
        html = [["#view", view_html]]
        return HttpResponse(json.dumps({
            "html": html,
            "message": message,
        }, cls=LazyEncoder), content_type='application/json')
    else:
        return view_html


def selectable_manufacturers_inline(request, manufacturer_id,
                                    template_name="manage/manufacturers/selectable_manufacturers_inline.html"):
    """Displays all selectable manufacturers.
    """
    return render_to_string(template_name, request=request, context={
        "manufacturers": Manufacturer.objects.all(),
        "manufacturer_id": int(manufacturer_id),
    })


@permission_required("core.manage_shop")
def manufacturer_inline(request, manufacturer_id, category_id,
                        template_name="manage/manufacturers/manufacturer_inline.html"):
    """Returns categories and products for given manufacturer id and category id.
    """
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)
    selected_products = manufacturer.products.all()

    products = []
    for product in Product.objects.filter(sub_type__in=[STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS], categories__in=[category_id], active=True):

        if product.is_standard():
            type = "P"
        else:
            type = "V"

        products.append({
            "id": product.id,
            "name": product.get_name(),
            "checked": product in selected_products,
            "type": type,
        })

    categories = []
    for category in Category.objects.filter(parent=category_id):

        checked, klass = _get_category_state(manufacturer, category)

        categories.append({
            "id": category.id,
            "name": category.name,
            "checked": checked,
            "klass": klass,
        })

    result = render_to_string(template_name, request=request, context={
        "categories": categories,
        "products": products,
        "manufacturer_id": manufacturer_id,
    })

    html = (("#sub-categories-%s" % category_id, result),)

    return HttpResponse(
        json.dumps({"html": html}), content_type='application/json')


@permission_required("core.manage_shop")
def add_manufacturer(request, template_name="manage/manufacturers/add_manufacturer.html"):
    """Form and logic to add a manufacturer.
    """
    if request.method == "POST":
        form = ManufacturerAddForm(data=request.POST)
        if form.is_valid():
            new_manufacturer = form.save()
            return HttpResponseRedirect(
                reverse("lfs_manage_manufacturer", kwargs={"manufacturer_id": new_manufacturer.id}))

    else:
        form = ManufacturerAddForm()

    return render(request, template_name, {
        "form": form,
        "selectable_manufacturers_inline": selectable_manufacturers_inline(request, 0),
        "came_from": (request.POST if request.method == 'POST' else request.GET).get("came_from",
                                                                                     reverse("lfs_manufacturer_dispatcher")),
    })


# Actions
@permission_required("core.manage_shop")
def manufacturer_dispatcher(request):
    """Dispatches to the first manufacturer or to the add form.
    """
    try:
        manufacturer = Manufacturer.objects.all()[0]
    except IndexError:
        return HttpResponseRedirect(reverse("lfs_manage_no_manufacturers"))
    else:
        return HttpResponseRedirect(
            reverse("lfs_manage_manufacturer", kwargs={"manufacturer_id": manufacturer.id}))


@permission_required("core.manage_shop")
@require_POST
def delete_manufacturer(request, manufacturer_id):
    """Deletes Manufacturer with passed manufacturer id.
    """
    try:
        manufacturer = Manufacturer.objects.get(pk=manufacturer_id)
    except Manufacturer.DoesNotExist:
        pass
    else:
        manufacturer.delete()

    return HttpResponseRedirect(reverse("lfs_manufacturer_dispatcher"))


@permission_required("core.manage_shop")
def edit_category(request, manufacturer_id, category_id):
    """Adds/Removes products of given category to given manufacturer.
    """
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)
    category = Category.objects.get(pk=category_id)

    if request.POST.get("action") == "add":
        for product in category.get_all_products():
            product.manufacturer = manufacturer
            product.save()
    else:
        for product in category.get_all_products():
            product.manufacturer = None
            product.save()

    return HttpResponse("")


@permission_required("core.manage_shop")
def edit_product(request, manufacturer_id, product_id):
    """Adds/Removes given product to given manufacturer.
    """
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)
    product = Product.objects.get(pk=product_id)

    if request.POST.get("action") == "add":
        product.manufacturer = manufacturer
        product.save()
    else:
        product.manufacturer = None
        product.save()

    return HttpResponse("")


@permission_required("core.manage_shop")
def category_state(request, manufacturer_id, category_id):
    """Sets the state (klass and checking) for given category for given
    manufacturer.
    """
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)
    category = Category.objects.get(pk=category_id)
    checked, klass = _get_category_state(manufacturer, category)

    if klass == "half":
        result = "(1/2)"
    else:
        result = ""

    html = ("#category-state-%s" % category_id, result)
    checkbox = ("#manufacturer-category-input-%s" % category_id, checked)

    return HttpResponse(
        json.dumps({
            "html": html,
            "checkbox": checkbox
        }, content_type='application/json')
    )


@permission_required("core.manage_shop")
def update_data(request, manufacturer_id):
    """Updates data of manufacturer with given manufacturer id.
    """
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)
    form = ManufacturerDataForm(instance=manufacturer, data=request.POST,
                                files=request.FILES)

    if form.is_valid():
        manufacturer = form.save()
        msg = _(u"Manufacturer data has been saved.")
    else:
        msg = _(u"Please correct the indicated errors.")

    # Delete image
    if request.POST.get("delete_image"):
        try:
            manufacturer.image.delete()
        except OSError as e:
            logger.error('Error while trying to delete manufacturer image: %s' % e)

    html = (
        ("#data", manufacturer_data_inline(request, manufacturer.pk)),
        ("#selectable-manufacturers", selectable_manufacturers_inline(request, manufacturer_id)),
    )

    result = json.dumps({
        "html": html,
        "message": msg
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


def _get_category_state(manufacturer, category):
    """Calculates the state for given category for given manufacturer.
    """
    selected_products = manufacturer.products.all()

    found = False
    not_found = False

    for product in category.get_all_products():
        if product in selected_products:
            found = True
        else:
            not_found = True

    if found and not_found:
        checked = True
        klass = "half"
    elif found:
        checked = True
        klass = "full"
    else:
        checked = False
        klass = ""

    return (checked, klass)


@never_cache
@permission_required("core.manage_shop")
def manufacturers_ajax(request):
    """ Returns list of manufacturers for autocomplete
    """
    term = request.GET.get('term', '')
    manufacturers = Manufacturer.objects.filter(name__istartswith=term)[:10]

    out = []
    for man in manufacturers:
        out.append({'label': man.name,
                    'value': man.pk})

    result = json.dumps(out, cls=LazyEncoder)
    return HttpResponse(result, content_type='application/json')
