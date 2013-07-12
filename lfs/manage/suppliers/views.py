# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache

# lfs imports
from lfs.core.utils import LazyEncoder
from lfs.supplier.models import Supplier
from lfs.manage.suppliers.forms import SupplierDataForm, SupplierAddForm

import logging

logger = logging.getLogger(__file__)


@permission_required("core.manage_shop")
def manage_supplier(request, supplier_id, template_name="manage/suppliers/supplier.html"):
    """The main view to display suppliers.
    """
    supplier = Supplier.objects.get(pk=supplier_id)

    return render_to_response(template_name, RequestContext(request, {
        "supplier": supplier,
        "supplier_id": supplier_id,
        "selectable_suppliers_inline": selectable_suppliers_inline(request, supplier_id),
        "supplier_data_inline": supplier_data_inline(request, supplier_id),
    }))


@permission_required("core.manage_shop")
def no_suppliers(request, template_name="manage/suppliers/no_suppliers.html"):
    """Displays that there are no suppliers.
    """
    return render_to_response(template_name, RequestContext(request, {}))


# Parts
def supplier_data_inline(request, supplier_id,
                         template_name="manage/suppliers/supplier_data_inline.html"):
    """Displays the data form of the current supplier.
    """
    supplier = Supplier.objects.get(pk=supplier_id)
    if request.method == "POST":
        form = SupplierDataForm(instance=supplier, data=request.POST)
    else:
        form = SupplierDataForm(instance=supplier)
    return render_to_string(template_name, RequestContext(request, {
        "supplier": supplier,
        "form": form,
    }))


def selectable_suppliers_inline(request, supplier_id,
                                template_name="manage/suppliers/selectable_suppliers_inline.html"):
    """Displays all selectable suppliers.
    """
    return render_to_string(template_name, RequestContext(request, {
        "suppliers": Supplier.objects.all(),
        "supplier_id": int(supplier_id),
    }))


@permission_required("core.manage_shop")
def add_supplier(request, template_name="manage/suppliers/add_supplier.html"):
    """Form and logic to add a supplier.
    """
    if request.method == "POST":
        form = SupplierAddForm(data=request.POST)
        if form.is_valid():
            new_supplier = form.save()
            return HttpResponseRedirect(
                reverse("lfs_manage_supplier", kwargs={"supplier_id": new_supplier.id}))

    else:
        form = SupplierAddForm()

    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "selectable_suppliers_inline": selectable_suppliers_inline(request, 0),
        "came_from": request.REQUEST.get("came_from", reverse("lfs_supplier_dispatcher")),
    }))


# Actions
@permission_required("core.manage_shop")
def supplier_dispatcher(request):
    """Dispatches to the first supplier or to the add form.
    """
    try:
        supplier = Supplier.objects.all()[0]
    except IndexError:
        return HttpResponseRedirect(reverse("lfs_manage_no_suppliers"))
    else:
        return HttpResponseRedirect(
            reverse("lfs_manage_supplier", kwargs={"supplier_id": supplier.id}))


@permission_required("core.manage_shop")
@require_POST
def delete_supplier(request, supplier_id):
    """Deletes Supplier with passed supplier id.
    """
    try:
        supplier = Supplier.objects.get(pk=supplier_id)
    except Supplier.DoesNotExist:
        pass
    else:
        supplier.delete()

    return HttpResponseRedirect(reverse("lfs_supplier_dispatcher"))


@permission_required("core.manage_shop")
def update_data(request, supplier_id):
    """Updates data of supplier with given supplier id.
    """
    supplier = Supplier.objects.get(pk=supplier_id)
    form = SupplierDataForm(instance=supplier, data=request.POST,
                            files=request.FILES)

    if form.is_valid():
        supplier = form.save()
        msg = _(u"Supplier data has been saved.")
    else:
        msg = _(u"Please correct the indicated errors.")

    html = (
        ("#data", supplier_data_inline(request, supplier.pk)),
        ("#selectable-suppliers", selectable_suppliers_inline(request, supplier_id)),
    )

    result = simplejson.dumps({
                                  "html": html,
                                  "message": msg
                              }, cls=LazyEncoder)

    return HttpResponse(result)


@never_cache
@permission_required("core.manage_shop")
def suppliers_ajax(request):
    """ Returns list of suppliers for autocomplete
    """
    term = request.GET.get('term', '')
    suppliers = Supplier.objects.filter(name__istartswith=term)[:10]

    out = []
    for sup in suppliers:
        out.append({'label': sup.name,
                    'value': sup.pk})

    result = simplejson.dumps(out, cls=LazyEncoder)
    return HttpResponse(result)
