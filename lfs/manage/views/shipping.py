# django imports
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder
from lfs.core.widgets.image import LFSImageInput
from lfs.criteria import utils as criteria_utils
from lfs.customer.models import Customer
from lfs.shipping.models import ShippingMethod
from lfs.shipping.models import ShippingMethodPrice
from lfs.shipping import utils as shipping_utils


class ShippingMethodAddForm(ModelForm):
    """Form to add a shipping method.
    """
    class Meta:
        model = ShippingMethod
        fields = ["name"]


class ShippingMethodForm(ModelForm):
    """
    """
    def __init__(self, *args, **kwargs):
        super(ShippingMethodForm, self).__init__(*args, **kwargs)
        self.fields["image"].widget = LFSImageInput()

    class Meta:
        model = ShippingMethod


# # Starting pages. This pages are called directly via a request
@permission_required("core.manage_shop", login_url="/login/")
def manage_shipping(request):
    """Dispatches to the first shipping method or to the add shipping method
    form if there is no shipping method.
    """
    try:
        shipping_method = ShippingMethod.objects.all()[0]
    except IndexError:
        url = reverse("lfs.manage.views.add_shipping_method")
    else:
        url = reverse("lfs.manage.views.manage_shipping_method",
            kwargs={"shipping_method_id": shipping_method.id})
    return HttpResponseRedirect(url)


@permission_required("core.manage_shop", login_url="/login/")
def manage_shipping_method(request, shipping_method_id,
    template_name="manage/shipping/manage_shipping.html"):
    """The main view to manage the shipping method with given id.

    This view collects the various parts of the shipping form (data, criteria,
    prices) and displays them.
    """
    shipping_method = ShippingMethod.objects.get(pk=shipping_method_id)

    return render_to_response(template_name, RequestContext(request, {
        "shipping_method": shipping_method,
        "shipping_methods": shipping_methods(request),
        "data": shipping_method_data(request, shipping_method_id),
        "method_criteria": shipping_method_criteria(request, shipping_method_id),
        "method_prices": shipping_method_prices(request, shipping_method_id),
    }))


# Parts of the manage shipping view.
@permission_required("core.manage_shop", login_url="/login/")
def shipping_methods(request, template_name="manage/shipping/shipping_methods.html"):
    """Returns all shipping methods as html.

    This view is used as a part within the manage shipping view.
    """
    try:
        current_id = int(request.path.split("/")[-1])
    except ValueError:
        current_id = ""

    return render_to_string(template_name, RequestContext(request, {
        "current_id": current_id,
        "shipping_methods": ShippingMethod.objects.all(),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def shipping_method_data(request, shipping_id,
    template_name="manage/shipping/shipping_method_data.html"):
    """Returns the shipping data as html.

    This view is used as a part within the manage shipping view.
    """
    shipping_method = ShippingMethod.objects.get(pk=shipping_id)

    return render_to_string(template_name, RequestContext(request, {
        "form": ShippingMethodForm(instance=shipping_method),
        "shipping_method": shipping_method,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def shipping_method_criteria(request, shipping_method_id,
    template_name="manage/shipping/shipping_method_criteria.html"):
    """Returns the criteria of the shipping method with passed id as HTML.

    This view is used as a part within the manage shipping view.
    """
    shipping_method = ShippingMethod.objects.get(pk=shipping_method_id)

    criteria = []
    position = 0
    for criterion_object in shipping_method.criteria_objects.all():
        position += 10
        criterion_html = criterion_object.criterion.as_html(request, position)
        criteria.append(criterion_html)

    return render_to_string(template_name, RequestContext(request, {
        "shipping_method": shipping_method,
        "criteria": criteria,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def shipping_method_prices(request, shipping_method_id,
    template_name="manage/shipping/shipping_method_prices.html"):
    """Returns the shipping method prices for the shipping method with given id.

    This view is used as a part within the manage shipping view.
    """
    shipping_method = get_object_or_404(ShippingMethod, pk=shipping_method_id)

    return render_to_string(template_name, RequestContext(request, {
        "shipping_method": shipping_method,
        "prices": shipping_method.prices.all(),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def shipping_price_criteria(request, shipping_price_id, as_string=False,
    template_name="manage/shipping/shipping_price_criteria.html"):
    """Returns the criteria of the shipping price with passed id.

    This view is used as a part within the manage shipping view.
    """
    shipping_price = get_object_or_404(ShippingMethodPrice, pk=shipping_price_id)

    criteria = []
    position = 0
    for criterion_object in shipping_price.criteria_objects.all():
        position += 10
        criterion_html = criterion_object.criterion.as_html(request, position)
        criteria.append(criterion_html)

    dialog = render_to_string(template_name, RequestContext(request, {
        "shipping_price": shipping_price,
        "criteria": criteria,
    }))

    if as_string:
        return dialog
    else:
        html = [["#dialog", dialog]]

        result = simplejson.dumps({
            "html": html,
            "open-dialog": True,
        }, cls=LazyEncoder)

        return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def add_shipping_method(request,
    template_name="manage/shipping/add_shipping_method.html"):
    """Provides an add form and saves a new shipping method.
    """
    if request.method == "POST":
        form = ShippingMethodAddForm(data=request.POST)
        if form.is_valid():
            new_shipping_method = form.save()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs.manage.views.manage_shipping_method", kwargs={"shipping_method_id": new_shipping_method.id}),
                msg=_(u"Shipping method has been added."),
            )
    else:
        form = ShippingMethodAddForm()

    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "next": request.REQUEST.get("next", request.META.get("HTTP_REFERER")),
    }))


# Actions
@permission_required("core.manage_shop", login_url="/login/")
def save_shipping_method_criteria(request, shipping_method_id):
    """Saves the criteria for the shipping method with given id. The criteria
    are passed via request body.
    """
    shipping_method = lfs_get_object_or_404(ShippingMethod, pk=shipping_method_id)

    criteria_utils.save_criteria(request, shipping_method)

    html = [["#criteria", shipping_method_criteria(request, shipping_method_id)]]

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Modifications have been changed."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def save_shipping_price_criteria(request, shipping_price_id):
    """Saves the criteria for the shipping price with given id. The criteria
    are passed via request body.
    """
    shipping_price = get_object_or_404(ShippingMethodPrice, pk=shipping_price_id)

    criteria_utils.save_criteria(request, shipping_price)

    html = [
        ["#price-criteria", shipping_price_criteria(request, shipping_price_id, as_string=True)],
        ["#prices", shipping_method_prices(request, shipping_price.shipping_method.id)],
    ]

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Modifications have been changed."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
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

    result = simplejson.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
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
    result = simplejson.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def save_shipping_method_data(request, shipping_method_id):
    """Saves shipping data (via request body) to the shipping method with passed
    id.

    This is called via an AJAX request and returns JSON encoded data.
    """
    shipping_method = ShippingMethod.objects.get(pk=shipping_method_id)
    shipping_form = ShippingMethodForm(instance=shipping_method, data=request.POST, files=request.FILES)

    form = render_to_string(
        "manage/shipping/shipping_method_data.html", RequestContext(request, {
        "form": shipping_form,
        "shipping_method": shipping_method,
    }))

    if shipping_form.is_valid():
        shipping_form.save()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_shipping_method", kwargs={"shipping_method_id": shipping_method.id}),
        msg=_(u"Shipping method has been saved."),
    )


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
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


def _update_price_positions(shipping_method):
    for i, price in enumerate(shipping_method.prices.all()):
        price.priority = (i + 1) * 10
        price.save()
