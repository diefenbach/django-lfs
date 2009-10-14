# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson

# lfs imports
import lfs.voucher.utils
from lfs.core.utils import LazyEncoder
from lfs.core.utils import render_to_ajax_response
from lfs.tax.models import Tax
from lfs.voucher.forms import VoucherGroupForm
from lfs.voucher.models import Voucher
from lfs.voucher.models import VoucherGroup

# Parts
def voucher_group(request, id, template_name="manage/voucher/voucher_group.html"):
    """Main view to display a voucher group.
    """
    voucher_group = VoucherGroup.objects.get(pk=id)

    return render_to_response(template_name, RequestContext(request, {
        "voucher_group"  : voucher_group,
        "data_tab" : data_tab(request, voucher_group),
        "vouchers_tab" : vouchers_tab(request, voucher_group),
        "navigation" : navigation(request, voucher_group),
    }))

def navigation(request, voucher_group, template_name="manage/voucher/navigation.html"):
    """Displays the navigation.
    """
    return render_to_string(template_name, RequestContext(request, {
        "voucher_group" : voucher_group,
        "voucher_groups" : VoucherGroup.objects.all(),
    }))

def data_tab(request, voucher_group, template_name="manage/voucher/data.html"):
    """Displays the data tab of the passed voucher group.
    """
    if request.method == "POST":
        form = VoucherGroupForm(instance=voucher_group, data=request.POST)
        if form.is_valid():
            form = VoucherGroupForm(instance=voucher_group)
    else:
        form = VoucherGroupForm(instance=voucher_group)

    return render_to_string(template_name, RequestContext(request, {
        "voucher_group" : voucher_group,
        "form" : form,
    }))

def vouchers_tab(request, voucher_group, template_name="manage/voucher/vouchers.html"):
    """Displays the vouchers tab
    """
    vouchers = voucher_group.vouchers.all()
    taxes = Tax.objects.all()
    
    return render_to_string(template_name, RequestContext(request, {
        "voucher_group" : voucher_group,
        "vouchers" : vouchers,
        "taxes" : taxes,
    }))

# Actions
def manage_vouchers(request):
    """Redirects to the first voucher group or to the add voucher form.
    """
    try:
        voucher_group = VoucherGroup.objects.all()[0]
    except IndexError:
        url = reverse("lfs_manage_add_voucher_group")
    else:
        url = reverse("lfs_manage_voucher_group", kwargs={ "id" : voucher_group.id })

    return HttpResponseRedirect(url)

def add_vouchers(request, group_id):
    """
    """
    voucher_group = VoucherGroup.objects.get(pk=group_id)

    try:
        amount = int(request.POST.get("amount", 0))
    except TypeError:
        amount = 0

    for i in range(0, amount):
        while 1:
            try:
                Voucher.objects.create(
                    number = lfs.voucher.utils.create_voucher_number(),
                    group = voucher_group,
                    creator = request.user,
                    kind_of = request.POST.get("kind_of", 0),
                    value = request.POST.get("value", 0.0),
                    expiration_date = request.POST.get("expiration_date"),
                    tax_id = request.POST.get("tax_id")
                )
                break
            except IntegrityError:
                pass

    return render_to_ajax_response(
        (("#vouchers", vouchers_tab(request, voucher_group)), ),
        _(u"Vouchers have been created."))

def delete_vouchers(request, group_id):
    """Deletes checked vouchers.
    """
    voucher_group = VoucherGroup.objects.get(pk=group_id)
    vouchers = Voucher.objects.filter(pk__in=request.POST.getlist("voucher-ids"))

    for voucher in vouchers:
        voucher.delete()

    return render_to_ajax_response(
        (("#vouchers", vouchers_tab(request, voucher_group)), ),
        _(u"Vouchers have been deleted."))

def add_voucher_group(request, template_name="manage/voucher/add_voucher_group.html"):
    """Adds a voucher group
    """
    if request.method == "POST":
        form = VoucherGroupForm(data=request.POST)
        if form.is_valid():
            voucher_group = form.save(commit=False)
            voucher_group.creator = request.user
            voucher_group.save()
            url = reverse("lfs_manage_voucher_group", kwargs={"id" : voucher_group.id })
            return HttpResponseRedirect(url)
    else:
        form = VoucherGroupForm()

    return render_to_response(template_name, RequestContext(request, {
        "form" : form,
        "voucher_groups" : VoucherGroup.objects.all(),
    }))

def save_voucher_group_data(request, id):
    """Saves the data of the voucher group with passed id.
    """
    voucher_group = VoucherGroup.objects.get(pk=id)
    form = VoucherGroupForm(instance=voucher_group, data=request.POST)
    if form.is_valid():
        voucher_group = form.save()

    _update_positions()
    voucher_group = VoucherGroup.objects.get(pk=voucher_group.id)

    return render_to_ajax_response(
        (("#data_tab", data_tab(request, voucher_group)),
        ("#navigation", navigation(request, voucher_group)),),
        _(u"Voucher data has been save."))

def _update_positions():
    for i, voucher_group in enumerate(VoucherGroup.objects.all()):
        voucher_group.position = (i+1)*10
        voucher_group.save()