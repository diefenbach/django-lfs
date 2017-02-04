import json

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.core.utils import LazyEncoder
from lfs.customer_tax.models import CustomerTax
from lfs.manage.customer_tax.forms import CustomerTaxForm


@permission_required("core.manage_shop")
def manage_customer_taxes(request):
    """Dispatches to the first customer_tax or to the add customer_tax form.
    """
    try:
        customer_tax = CustomerTax.objects.all()[0]
        url = reverse("lfs_manage_customer_tax", kwargs={"id": customer_tax.id})
    except IndexError:
        url = reverse("lfs_manage_no_customer_taxes")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
def manage_customer_tax(request, id, template_name="manage/customer_tax/customer_tax.html"):
    """Displays the main form to manage customer taxes.
    """
    customer_tax = get_object_or_404(CustomerTax, pk=id)
    return render(request, template_name, {
        "customer_tax": customer_tax,
        "data": data(request, customer_tax),
        "criteria": criteria(request, customer_tax),
        "navigation": navigation(request, customer_tax),
    })


# Parts
def data(request, customer_tax, form=None, template_name="manage/customer_tax/data.html"):
    """
    Renders the data tab of customer taxes.
    """
    if form is None:
        form = CustomerTaxForm(instance=customer_tax)

    return render_to_string(template_name, request=request, context={
        "customer_tax": customer_tax,
        "form": form,
    })


def criteria(request, customer_tax, template_name="manage/customer_tax/criteria.html"):
    """Returns the criteria of the passed customer tax.
    """
    criteria = []
    position = 0
    for criterion in customer_tax.get_criteria():
        position += 10
        criterion_html = criterion.render(request, position)
        criteria.append(criterion_html)

    return render_to_string(template_name, request=request, context={
        "customer_tax": customer_tax,
        "criteria": criteria,
    })


def navigation(request, customer_tax, template_name="manage/customer_tax/navigation.html"):
    """
    Renders the navigation of customer taxes.
    """
    return render_to_string(template_name, request=request, context={
        "customer_taxes": CustomerTax.objects.all(),
        "current_id": customer_tax.id,
    })


@permission_required("core.manage_shop")
def no_customer_taxes(request, template_name="manage/customer_tax/no_customer_taxes.html"):
    """Display no taxes available.
    """
    return render(request, template_name, {})


# Actions
@permission_required("core.manage_shop")
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

    return render(request, template_name, {
        "form": form,
        "customer_taxes": CustomerTax.objects.all(),
        "next": (request.POST if request.method == 'POST' else request.GET).get("next", request.META.get("HTTP_REFERER")),
    })


@permission_required("core.manage_shop")
@require_POST
def delete_customer_tax(request, id):
    """
    Deletes customer tax with passed id.
    """
    customer_tax = get_object_or_404(CustomerTax, pk=id)
    customer_tax.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_customer_taxes"),
        msg=_(u"Customer tax has been deleted."),
    )


@permission_required("core.manage_shop")
def save_criteria(request, id):
    """
    Saves the criteria for the customer tax with given id. The criteria are
    passed via request body.
    """
    customer_tax = get_object_or_404(CustomerTax, pk=id)
    customer_tax.save_criteria(request)

    html = [["#criteria", criteria(request, customer_tax)]]

    result = json.dumps({
        "html": html,
        "message": _(u"Criteria have been changed."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
@require_POST
def save_data(request, id):
    """
    Saves the data for the customer tax with given id.
    """
    customer_tax = get_object_or_404(CustomerTax, pk=id)
    form = CustomerTaxForm(instance=customer_tax, data=request.POST, files=request.FILES)
    if form.is_valid():
        form.save()
        form = None

    html = [
        ["#data", data(request, customer_tax, form=form)],
        ["#navigation", navigation(request, customer_tax)],
    ]

    result = json.dumps({
        "html": html,
        "message": _(u"Data have been saved."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')
