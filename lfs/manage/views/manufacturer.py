# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
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
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.core.utils import LazyEncoder
from lfs.manufacturer.models import Manufacturer
from lfs.manufacturer.models import Manufacturer


class ManufacturerDataForm(ModelForm):
    """Form to manage selection data.
    """
    class Meta:
        model = Manufacturer


def manage_manufacturer(request, manufacturer_id, template_name="manage/manufacturer/manufacturer.html"):
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

    data_form = ManufacturerDataForm(instance=manufacturer)
    return render_to_response(template_name, RequestContext(request, {
        "categories": categories,
        "manufacturer_id": manufacturer_id,
        "selectable_manufacturers_inline": selectable_manufacturers_inline(request, manufacturer_id),
        "manufacturer_data_inline": manufacturer_data_inline(request, manufacturer_id, data_form),
    }))


# Parts
def manufacturer_data_inline(request, manufacturer_id, form,
    template_name="manage/manufacturer/manufacturer_data_inline.html"):
    """Displays the data form of the current manufacturer.
    """
    return render_to_string(template_name, RequestContext(request, {
        "manufacturer_id": manufacturer_id,
        "form": form,
    }))


def selectable_manufacturers_inline(request, manufacturer_id,
    template_name="manage/manufacturer/selectable_manufacturers_inline.html"):
    """Displays all selectable manufacturers.
    """
    return render_to_string(template_name, RequestContext(request, {
        "manufacturers": Manufacturer.objects.all(),
        "manufacturer_id": int(manufacturer_id),
    }))


def manufacturer_inline(request, manufacturer_id, category_id,
    template_name="manage/manufacturer/manufacturer_inline.html"):
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

    result = render_to_string(template_name, RequestContext(request, {
        "categories": categories,
        "products": products,
        "manufacturer_id": manufacturer_id,
    }))

    html = (("#sub-categories-%s" % category_id, result),)

    return HttpResponse(
        simplejson.dumps({"html": html}))


def add_manufacturer(request, template_name="manage/manufacturer/add_manufacturer.html"):
    """Form and logic to add a manufacturer.
    """
    if request.method == "POST":
        form = ManufacturerDataForm(data=request.POST)
        if form.is_valid():
            new_manufacturer = form.save()
            return HttpResponseRedirect(
                reverse("lfs_manufacturer", kwargs={"manufacturer_id": new_manufacturer.id}))

    else:
        form = ManufacturerDataForm()

    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "selectable_manufacturers_inline": selectable_manufacturers_inline(request, 0),
        "next": request.REQUEST.get("next", request.META.get("HTTP_REFERER")),
    }))


# Actions
def manufacturer_dispatcher(request):
    """Dispatches to the first manufacturer or to the add form.
    """
    try:
        manufacturer = Manufacturer.objects.all()[0]
    except IndexError:
        return HttpResponseRedirect(reverse("lfs_manufacturer_add_manufacturer"))
    else:
        return HttpResponseRedirect(
            reverse("lfs_manufacturer", kwargs={"manufacturer_id": manufacturer.id}))


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
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
        simplejson.dumps({
            "html": html,
            "checkbox": checkbox
        })
    )


def update_data(request, manufacturer_id):
    """Updates data of manufacturer with given manufacturer id.
    """
    manufacturer = Manufacturer.objects.get(pk=manufacturer_id)
    form = ManufacturerDataForm(instance=manufacturer, data=request.POST)

    if form.is_valid():
        form.save()

    msg = _(u"Manufacturer data has been saved.")

    html = (
        ("#data", manufacturer_data_inline(request, manufacturer_id, form)),
        ("#selectable-manufacturers", selectable_manufacturers_inline(request, manufacturer_id)),
    )

    result = simplejson.dumps({
        "html": html,
        "message": msg
    }, cls=LazyEncoder)

    return HttpResponse(result)


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
