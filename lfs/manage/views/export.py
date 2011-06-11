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
from lfs.export.models import Export
from lfs.export.models import CategoryOption
from lfs.export.settings import CATEGORY_VARIANTS_CHOICES
from lfs.export.settings import CATEGORY_VARIANTS_NONE


class ExportDataForm(ModelForm):
    """Form to manage selection data.
    """
    class Meta:
        model = Export
        exclude = ("products", )


def manage_export(request, export_id, template_name="manage/export/export.html"):
    """The main view to display exports.
    """
    export = Export.objects.get(pk=export_id)

    categories = []
    for category in Category.objects.filter(parent=None):

        # Options
        options = []

        try:
            category_option = CategoryOption.objects.get(export=export, category=category)
        except CategoryOption.DoesNotExist:
            variants_option = None
        else:
            variants_option = category_option.variants_option

        for option in CATEGORY_VARIANTS_CHOICES:
            options.append({
                "name": option[1],
                "value": option[0],
                "selected": option[0] == variants_option,
            })

        # Checking state
        checked, klass = _get_category_state(export, category)

        categories.append({
            "id": category.id,
            "name": category.name,
            "checked": checked,
            "klass": klass,
            "options": options,
        })

    data_form = ExportDataForm(instance=export)
    return render_to_response(template_name, RequestContext(request, {
        "categories": categories,
        "export_id": export_id,
        "slug": export.slug,
        "selectable_exports_inline": selectable_exports_inline(request, export_id),
        "export_data_inline": export_data_inline(request, export_id, data_form),
    }))


# Parts
def export_data_inline(request, export_id, form,
    template_name="manage/export/export_data_inline.html"):
    """Displays the data form of the current export.
    """
    return render_to_string(template_name, RequestContext(request, {
        "export_id": export_id,
        "form": form,
    }))


def selectable_exports_inline(request, export_id,
    template_name="manage/export/selectable_exports_inline.html"):
    """Displays all selectable exports.
    """
    return render_to_string(template_name, RequestContext(request, {
        "exports": Export.objects.all(),
        "export_id": int(export_id),
    }))


def export_inline(request, export_id, category_id,
    template_name="manage/export/export_inline.html"):
    """Returns categories and products for given export id and category id.
    """
    export = Export.objects.get(pk=export_id)
    selected_products = export.products.all()

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

        # Options
        options = []

        try:
            category_option = CategoryOption.objects.get(export=export, category=category)
        except CategoryOption.DoesNotExist:
            variants_option = None
        else:
            variants_option = category_option.variants_option

        for option in CATEGORY_VARIANTS_CHOICES:
            options.append({
                "name": option[1],
                "value": option[0],
                "selected": option[0] == variants_option,
            })

        checked, klass = _get_category_state(export, category)

        categories.append({
            "id": category.id,
            "name": category.name,
            "checked": checked,
            "klass": klass,
            "options": options,
        })

    result = render_to_string(template_name, RequestContext(request, {
        "categories": categories,
        "products": products,
        "export_id": export_id,
    }))

    html = (("#sub-categories-%s" % category_id, result),)

    return HttpResponse(
        simplejson.dumps({"html": html}))


def add_export(request, template_name="manage/export/add_export.html"):
    """Form and logic to add a export.
    """
    if request.method == "POST":
        form = ExportDataForm(data=request.POST)
        if form.is_valid():
            new_export = form.save()
            return HttpResponseRedirect(
                reverse("lfs_export", kwargs={"export_id": new_export.id}))

    else:
        form = ExportDataForm()

    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "selectable_exports_inline": selectable_exports_inline(request, 0),
    }))


# Actions
def export_dispatcher(request):
    """Dispatches to the first export or to the add form.
    """
    try:
        export = Export.objects.all()[0]
    except IndexError:
        return HttpResponseRedirect(reverse("lfs_export_add_export"))
    else:
        return HttpResponseRedirect(
            reverse("lfs_export", kwargs={"export_id": export.id}))


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def delete_export(request, export_id):
    """Deletes export with passed export id.
    """
    try:
        export = Export.objects.get(pk=export_id)
    except Export.DoesNotExist:
        pass
    else:
        export.delete()

    return HttpResponseRedirect(reverse("lfs_export_dispatcher"))


def edit_category(request, export_id, category_id):
    """Adds/Removes products of given category to given export.
    """
    export = Export.objects.get(pk=export_id)
    category = Category.objects.get(pk=category_id)

    if request.POST.get("action") == "add":
        for product in category.get_all_products():
            export.products.add(product)
    else:
        for product in category.get_all_products():
            export.products.remove(product)

    return HttpResponse("")


def edit_product(request, export_id, product_id):
    """Adds/Removes given product to given export.
    """
    export = Export.objects.get(pk=export_id)
    product = Product.objects.get(pk=product_id)

    if request.POST.get("action") == "add":
        export.products.add(product)
    else:
        export.products.remove(product)

    return HttpResponse("")


def export(request, slug):
    """Exports the export with passed export id.
    """
    export = get_object_or_404(Export, slug=slug)
    module = lfs.core.utils.import_module(export.script.module)
    return getattr(module, export.script.method)(request, export)


def category_state(request, export_id, category_id):
    """Sets the state (klass and checking) for given category for given
    export.
    """
    export = Export.objects.get(pk=export_id)
    category = Category.objects.get(pk=category_id)
    checked, klass = _get_category_state(export, category)

    if klass == "half":
        result = "(1/2)"
    else:
        result = ""

    html = ("#category-state-%s" % category_id, result)
    checkbox = ("#export-category-input-%s" % category_id, checked)

    return HttpResponse(
        simplejson.dumps({
            "html": html,
            "checkbox": checkbox
        })
    )


def update_category_variants_option(request, export_id, category_id):
    """Stores / deletes options for the variants handling of category with
    given id.
    """
    try:
        variants_option = int(request.POST.get("variants_option"))
    except ValueError:
        variants_option = 0

    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return HttpResponse("")

    try:
        export = Export.objects.get(pk=export_id)
    except Export.DoesNotExist:
        return HttpResponse("")

    try:
        category_option = CategoryOption.objects.get(export=export, category=category)
    except CategoryOption.DoesNotExist:
        category_option = None

    if variants_option == CATEGORY_VARIANTS_NONE:
        if category_option:
            category_option.delete()
    else:
        if category_option is None:
            CategoryOption.objects.create(
                export=export, category=category, variants_option=variants_option)
        else:
            category_option.variants_option = variants_option
            category_option.save()

    return HttpResponse("")


def update_data(request, export_id):
    """Updates data of export with given export id.
    """
    export = Export.objects.get(pk=export_id)
    form = ExportDataForm(instance=export, data=request.POST)

    if form.is_valid():
        form.save()

    msg = _(u"Export data has been saved.")

    html = (
        ("#data", export_data_inline(request, export_id, form)),
        ("#selectable-exports-inline", selectable_exports_inline(request, export_id)),
    )

    result = simplejson.dumps({
        "html": html,
        "message": msg
    }, cls=LazyEncoder)

    return HttpResponse(result)


def _get_category_state(export, category):
    """Calculates the state for given category for given export.
    """
    selected_products = export.products.all()

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
