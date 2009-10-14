# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from lfs.voucher.models import VoucherGroup

def manage_vouchers(request):
    """
    """
    try:
        voucher_group = VoucherGroup.objects.all()[0]
    except IndexError:
        url = reverse("lfs_manage_add_voucher_group")
    else:
        url = reverse("lfs_manage_voucher_group", kwargs={ "id" : voucher_group.id })
    
    return HttpResponseRedirect(url)
    
def add_voucher_group(request, template_name="manage/voucher/add_voucher_group.html"):
    """Adds a voucher group
    """
    if request.method == "POST":
        form = VoucherGroupForm(data=request.POST)
        if form.is_valid():
            voucher = form.save()
    else:
        form = VoucherGroupForm()
    
    return render_to_response(template_name, RequestContext(request, {
        "form" : form,
        "voucher_groups" : VoucherGroup.objects.all(),
    }))

def manage_voucher_group(request, id, template_name="manage/voucher/voucher_group.html"):
    """
    """
    voucher_group = VoucherGroup.objects.get(pk=id)    

    return render_to_response(template_name, RequestContext(request, {
        "form" : VoucherGroupForm(instance=voucher_group),
        "voucher_groups" : VoucherGroup.objects.all(),
    }))