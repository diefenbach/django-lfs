# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.catalog.models import Product
from lfs.customer_tax.models import CustomerTax
from lfs.manage.customer_tax.forms import CustomerTaxForm


@permission_required("core.manage_shop", login_url="/login/")
def manage_customer_taxes(request):
    """Dispatches to the first customer_tax or to the add customer_tax form.
    """
    try:
        customer_tax = CustomerTax.objects.all()[0]
        url = reverse("lfs_manage_customer_tax", kwargs={"id": customer_tax.id})
    except IndexError:
        url = reverse("lfs_manage_no_customer_taxes")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop", login_url="/login/")
def manage_customer_tax(request, id, template_name="manage/customer_tax/customer_tax.html"):
    """Displays the main form to manage customer taxes.
    """
    customer_tax = get_object_or_404(CustomerTax, pk=id)
    if request.method == "POST":
        form = CustomerTaxForm(instance=customer_tax, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_customer_tax", kwargs={"id": customer_tax.id}),
                msg=_(u"Customer tax has been saved."),
            )
    else:
        form = CustomerTaxForm(instance=customer_tax)

    return render_to_response(template_name, RequestContext(request, {
        "customer_tax": customer_tax,
        "customer_taxes": CustomerTax.objects.all(),
        "form": form,
        "current_id": int(id),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def no_customer_taxes(request, template_name="manage/customer_tax/no_customer_taxes.html"):
    """Display no taxes available.
    """
    return render_to_response(template_name, RequestContext(request, {}))


# Actions
@permission_required("core.manage_shop", login_url="/login/")
def add_customer_tax(request, template_name="manage/customer_tax/add_customer_tax.html"):
    """Provides a form to add a new customer tax.
    """
    if request.method == "POST":
        form = CustomerTaxForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            tax = form.save()

            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_customer_tax", kwargs={"id": tax.id}),
                msg=_(u"Customer tax has been added."),
            )
    else:
        form = CustomerTaxForm()

    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "customer_taxes": CustomerTax.objects.all(),
        "next": request.REQUEST.get("next", request.META.get("HTTP_REFERER")),
    }))


@permission_required("core.manage_shop", login_url="/login/")
@require_POST
def delete_customer_tax(request, id):
    """Deletes customer tax with passed id.
    """
    customer_tax = get_object_or_404(CustomerTax, pk=id)
    customer_tax.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_customer_taxes"),
        msg=_(u"Customer tax has been deleted."),
    )
