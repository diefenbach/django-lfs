import json

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder
from lfs.customer.models import Customer
from lfs.manage.shipping_methods.forms import ShippingMethodAddForm
from lfs.manage.shipping_methods.forms import ShippingMethodForm
from lfs.shipping.models import ShippingMethod
from lfs.shipping.models import ShippingMethodPrice
from lfs.shipping import utils as shipping_utils


# Starting pages. This pages are called directly via a request
@permission_required("core.manage_shop")
def manage_shipping(request):
    """Dispatches to the first shipping method or to the add shipping method
    form if there is no shipping method.
    """
    try:
        shipping_method = ShippingMethod.objects.all()[0]
    except IndexError:
        url = reverse("lfs_manage_no_shipping_methods")
    else:
        url = reverse("lfs_manage_shipping_method", kwargs={"shipping_method_id": shipping_method.id})
    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
def manage_shipping_method(request, shipping_method_id,
                           template_name="manage/shipping_methods/manage_shipping.html"):
    """The main view to manage the shipping method with given id.

    This view collects the various parts of the shipping form (data, criteria,
    prices) and displays them.
    """
    shipping_method = ShippingMethod.objects.get(pk=shipping_method_id)

    return render(request, template_name, {
        "shipping_method": shipping_method,
        "shipping_methods": shipping_methods(request),
        "data": shipping_method_data(request, shipping_method_id),
        "method_criteria": shipping_method_criteria(request, shipping_method_id),
        "method_prices": shipping_method_prices(request, shipping_method_id),
    })


@permission_required("core.manage_shop")
def no_shipping_methods(request, template_name="manage/shipping_methods/no_shipping_methods.html"):
    """Displays that there are no shipping methods.
    """
    return render(request, template_name, {})


# Parts of the manage shipping view.
@permission_required("core.manage_shop")
def shipping_methods(request, template_name="manage/shipping_methods/shipping_methods.html"):
    """Returns all shipping methods as html.

    This view is used as a part within the manage shipping view.
    """
    try:
        current_id = int(request.path.split("/")[-1])
    except ValueError:
        current_id = ""

    return render_to_string(template_name, request=request, context={
        "current_id": current_id,
        "shipping_methods": ShippingMethod.objects.all(),
    })


@permission_required("core.manage_shop")
def shipping_method_data(request, shipping_id, form=None,
                         template_name="manage/shipping_methods/shipping_method_data.html"):
    """Returns the shipping data as html.

    This view is used as a part within the manage shipping view.
    """
    shipping_method = ShippingMethod.objects.get(pk=shipping_id)
    if form is None:
        form = ShippingMethodForm(instance=shipping_method)

    return render_to_string(template_name, request=request, context={
        "form": form,
        "shipping_method": shipping_method,
    })


@permission_required("core.manage_shop")
def shipping_method_criteria(request, shipping_method_id,
                             template_name="manage/shipping_methods/shipping_method_criteria.html"):
    """Returns the criteria of the shipping method with passed id as HTML.

    This view is used as a part within the manage shipping view.
    """
    shipping_method = ShippingMethod.objects.get(pk=shipping_method_id)

    criteria = []
    position = 0
    for criterion in shipping_method.get_criteria():
        position += 10
        criterion_html = criterion.render(request, position)
        criteria.append(criterion_html)

    return render_to_string(template_name, request=request, context={
        "shipping_method": shipping_method,
        "criteria": criteria,
    })


@permission_required("core.manage_shop")
def shipping_method_prices(request, shipping_method_id,
                           template_name="manage/shipping_methods/shipping_method_prices.html"):
    """Returns the shipping method prices for the shipping method with given id.

    This view is used as a part within the manage shipping view.
    """
    shipping_method = get_object_or_404(ShippingMethod, pk=shipping_method_id)

    return render_to_string(template_name, request=request, context={
        "shipping_method": shipping_method,
        "prices": shipping_method.prices.all(),
    })


@permission_required("core.manage_shop")
def shipping_price_criteria(request, shipping_price_id, as_string=False,
                            template_name="manage/shipping_methods/shipping_price_criteria.html"):
    """Returns the criteria of the shipping price with passed id.

    This view is used as a part within the manage shipping view.
    """
    shipping_price = get_object_or_404(ShippingMethodPrice, pk=shipping_price_id)

    criteria = []
    position = 0
    for criterion in shipping_price.get_criteria():
        position += 10
        criterion_html = criterion.render(request, position)
        criteria.append(criterion_html)

    dialog = render_to_string(template_name, request=request, context={
        "shipping_price": shipping_price,
        "criteria": criteria,
    })

    if as_string:
        return dialog
    else:
        html = [["#dialog", dialog]]

        result = json.dumps({
            "html": html,
            "open-dialog": True,
        }, cls=LazyEncoder)

        return HttpResponse(result, content_type='application/json')


# Actions
@permission_required("core.manage_shop")
def add_shipping_method(request,
                        template_name="manage/shipping_methods/add_shipping_method.html"):
    """Provides an add form and saves a new shipping method.
    """
    if request.method == "POST":
        form = ShippingMethodAddForm(data=request.POST)
        if form.is_valid():
            new_shipping_method = form.save()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_shipping_method", kwargs={"shipping_method_id": new_shipping_method.id}),
                msg=_(u"Shipping method has been added."),
            )
    else:
        form = ShippingMethodAddForm()

    return render(request, template_name, {
        "form": form,
        "came_from": (request.POST if request.method == 'POST' else request.GET).get("came_from",
                                                                                     reverse("lfs_manage_shipping")),
    })


@permission_required("core.manage_shop")
def save_shipping_method_criteria(request, shipping_method_id):
    """Saves the criteria for the shipping method with given id. The criteria
    are passed via request body.
    """
    shipping_method = lfs_get_object_or_404(ShippingMethod, pk=shipping_method_id)
    shipping_method.save_criteria(request)

    html = [["#criteria", shipping_method_criteria(request, shipping_method_id)]]

    result = json.dumps({
        "html": html,
        "message": _(u"Changes have been saved."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def save_shipping_price_criteria(request, shipping_price_id):
    """Saves the criteria for the shipping price with given id. The criteria
    are passed via request body.
    """
    shipping_price = get_object_or_404(ShippingMethodPrice, pk=shipping_price_id)
    shipping_price.save_criteria(request)

    html = [
        ["#price-criteria", shipping_price_criteria(request, shipping_price_id, as_string=True)],
        ["#prices", shipping_method_prices(request, shipping_price.shipping_method.id)],
    ]

    result = json.dumps({
        "html": html,
        "close-dialog": True,
        "message": _(u"Modifications have been saved."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def add_shipping_price(request, shipping_method_id):
    """Adds given shipping price (via request body) to shipping method with
    give id.

    Returns JSON encoded data.
    """
    try:
        price = float(request.POST.get("price", 0))
    except ValueError:
        price = 0.0

    shipping_method = get_object_or_404(ShippingMethod, pk=shipping_method_id)
    shipping_method.prices.create(price=price)
    _update_price_positions(shipping_method)

    message = _(u"Price has been added")
    html = [["#prices", shipping_method_prices(request, shipping_method_id)]]

    result = json.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def update_shipping_prices(request, shipping_method_id):
    """Saves/Deletes shipping prices with passed ids (via request body)
    dependent on given action (via request body).
    """
    shipping_method = get_object_or_404(ShippingMethod, pk=shipping_method_id)

    action = request.POST.get("action")
    if action == "delete":
        message = _(u"Prices have been deleted")
        for key in request.POST.keys():
            if key.startswith("delete-"):
                try:
                    id = key.split("-")[1]
                    price = get_object_or_404(ShippingMethodPrice, pk=id)
                except (IndexError, ObjectDoesNotExist):
                    continue
                else:
                    price.delete()

    elif action == "update":
        message = _(u"Prices have been updated")
        for key, value in request.POST.items():
            if key.startswith("price-"):
                try:
                    id = key.split("-")[1]
                    price = get_object_or_404(ShippingMethodPrice, pk=id)
                except (IndexError, ObjectDoesNotExist):
                    continue
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        value = 0.0
                    price.price = value
                    price.priority = request.POST.get("priority-%s" % id, 0)
                    price.save()

    _update_price_positions(shipping_method)

    html = [["#prices", shipping_method_prices(request, shipping_method_id)]]
    result = json.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def save_shipping_method_data(request, shipping_method_id):
    """Saves shipping data (via request body) to the shipping method with passed
    id.

    This is called via an AJAX request and returns JSON encoded data.
    """
    shipping_method = ShippingMethod.objects.get(pk=shipping_method_id)
    shipping_form = ShippingMethodForm(instance=shipping_method, data=request.POST, files=request.FILES)

    if shipping_form.is_valid():
        shipping_form.save()
        # Makes an uploaded image appear immediately
        shipping_form = ShippingMethodForm(instance=shipping_method)
        if request.POST.get("delete_image"):
            shipping_method.image.delete()
        message = _(u"Shipping method has been saved.")
    else:
        message = _(u"Please correct the indicated errors.")

    html = [
        ["#data", shipping_method_data(request, shipping_method.id, shipping_form)],
        ["#shipping-methods", shipping_methods(request)],
    ]

    result = json.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
@require_POST
def delete_shipping_method(request, shipping_method_id):
    """Deletes shipping method with passed shipping id.

    All customers, which have selected this shipping method are getting the
    default shipping method.
    """
    try:
        shipping_method = ShippingMethod.objects.get(pk=shipping_method_id)
    except ObjectDoesNotExist:
        pass
    else:
        for customer in Customer.objects.filter(selected_shipping_method=shipping_method_id):
            customer.selected_shipping_method = shipping_utils.get_default_shipping_method(request)
            customer.save()

        shipping_method.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_shipping"),
        msg=_(u"Shipping method has been deleted."),
    )


@permission_required("core.manage_shop")
@require_POST
def sort_shipping_methods(request):
    """Sorts shipping methods after drag 'n drop.
    """
    shipping_methods = request.POST.get("objs", "").split('&')
    assert (isinstance(shipping_methods, list))
    if len(shipping_methods) > 0:
        priority = 10
        for sm_str in shipping_methods:
            sm_id = sm_str.split('=')[1]
            sm_obj = ShippingMethod.objects.get(pk=sm_id)
            sm_obj.priority = priority
            sm_obj.save()
            priority = priority + 10

        result = json.dumps({
            "message": _(u"The shipping methods have been sorted."),
        }, cls=LazyEncoder)

        return HttpResponse(result, content_type='application/json')


def _update_price_positions(shipping_method):
    for i, price in enumerate(shipping_method.prices.all()):
        price.priority = (i + 1) * 10
        price.save()
