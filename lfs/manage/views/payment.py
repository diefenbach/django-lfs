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
from lfs.payment.models import PaymentMethod
from lfs.payment.models import PaymentMethodPrice
from lfs.payment import utils as payment_utils


class PaymentMethodAddForm(ModelForm):
    """Form to add a payment method.
    """
    class Meta:
        model = PaymentMethod
        fields = ("name", )


class PaymentMethodForm(ModelForm):
    """Form to edit a payment method.
    """
    def __init__(self, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        self.fields["image"].widget = LFSImageInput()

    class Meta:
        model = PaymentMethod
        exclude = ("deletable", )


# Starting pages. This pages are called directly via a request
@permission_required("core.manage_shop", login_url="/login/")
def manage_payment(request):
    """Dispatches to the first payment method or to the add payment method
    form if there is no payment method.
    """
    try:
        payment_method = PaymentMethod.objects.all()[0]
    except IndexError:
        url = reverse("lfs_add_payment_method")
    else:
        url = reverse("lfs_manage_payment_method",
            kwargs={"payment_method_id": payment_method.id})
    return HttpResponseRedirect(url)


@permission_required("core.manage_shop", login_url="/login/")
def manage_payment_method(request, payment_method_id,
    template_name="manage/payment/manage_payment.html"):
    """The main view to manage the payment method with given id.

    This view collects the various parts of the payment form (data, criteria,
    prices) and displays them.
    """
    payment_method = PaymentMethod.objects.get(pk=payment_method_id)

    return render_to_response(template_name, RequestContext(request, {
        "payment_method": payment_method,
        "payment_methods": payment_methods(request),
        "data": payment_method_data(request, payment_method_id),
        "method_criteria": payment_method_criteria(request, payment_method_id),
        "method_prices": payment_method_prices(request, payment_method_id),
    }))


# Parts of the manage payment view.
@permission_required("core.manage_shop", login_url="/login/")
def payment_methods(request, template_name="manage/payment/payment_methods.html"):
    """Returns all payment methods as html.

    This view is used as a part within the manage payment view.
    """
    try:
        current_id = int(request.path.split("/")[-1])
    except ValueError:
        current_id = ""

    return render_to_string(template_name, RequestContext(request, {
        "current_id": current_id,
        "payment_methods": PaymentMethod.objects.all(),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def payment_method_data(request, payment_id,
    template_name="manage/payment/payment_method_data.html"):
    """Returns the payment data as html.

    This view is used as a part within the manage payment view.
    """
    payment_method = PaymentMethod.objects.get(pk=payment_id)

    return render_to_string(template_name, RequestContext(request, {
        "form": PaymentMethodForm(instance=payment_method),
        "payment_method": payment_method,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def payment_method_criteria(request, payment_method_id,
    template_name="manage/payment/payment_method_criteria.html"):
    """Returns the criteria of the payment method with passed id as HTML.

    This view is used as a part within the manage payment view.
    """
    payment_method = PaymentMethod.objects.get(pk=payment_method_id)

    criteria = []
    position = 0
    for criterion_object in payment_method.criteria_objects.all():
        position += 10
        criterion_html = criterion_object.criterion.as_html(request, position)
        criteria.append(criterion_html)

    return render_to_string(template_name, RequestContext(request, {
        "payment_method": payment_method,
        "criteria": criteria,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def payment_method_prices(request, payment_method_id,
    template_name="manage/payment/payment_method_prices.html"):
    """Returns the payment method prices for the payment method with given id.

    This view is used as a part within the manage payment view.
    """
    payment_method = get_object_or_404(PaymentMethod, pk=payment_method_id)

    return render_to_string(template_name, RequestContext(request, {
        "payment_method": payment_method,
        "prices": payment_method.prices.all(),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def payment_price_criteria(request, payment_price_id, as_string=False, template_name="manage/payment/payment_price_criteria.html"):
    """Returns the criteria of the payment price with passed id.

    This view is used as a part within the manage payment view.
    """
    payment_price = get_object_or_404(PaymentMethodPrice, pk=payment_price_id)

    criteria = []
    position = 0
    for criterion_object in payment_price.criteria_objects.all():
        position += 10
        criterion_html = criterion_object.criterion.as_html(request, position)
        criteria.append(criterion_html)

    dialog = render_to_string(template_name, RequestContext(request, {
        "payment_price": payment_price,
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
def add_payment_method(request,
    template_name="manage/payment/add_payment_method.html"):
    """Provides an add form and saves a new payment method.
    """
    if request.method == "POST":
        form = PaymentMethodAddForm(data=request.POST)
        if form.is_valid():
            new_payment_method = form.save()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_payment_method", kwargs={"payment_method_id": new_payment_method.id}),
                msg=_(u"Payment method has been added."),
            )
    else:
        form = PaymentMethodAddForm()

    return render_to_response(template_name, RequestContext(request, {
        "payment_methods": payment_methods(request),
        "form": form,
        "next": request.REQUEST.get("next", request.META.get("HTTP_REFERER")),
    }))


# Actions
@permission_required("core.manage_shop", login_url="/login/")
def save_payment_method_criteria(request, payment_method_id):
    """Saves the criteria for the payment method with given id. The criteria
    are passed via request body.
    """
    payment_method = lfs_get_object_or_404(PaymentMethod, pk=payment_method_id)

    criteria_utils.save_criteria(request, payment_method)

    html = [["#criteria", payment_method_criteria(request, payment_method_id)]]

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Modifications have been changed."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def save_payment_price_criteria(request, payment_price_id):
    """Saves the criteria for the payment price with given id. The criteria
    are passed via request body.
    """
    payment_price = get_object_or_404(PaymentMethodPrice, pk=payment_price_id)

    criteria_utils.save_criteria(request, payment_price)

    html = [
        ["#price-criteria", payment_price_criteria(request, payment_price_id, as_string=True)],
        ["#prices", payment_method_prices(request, payment_price.payment_method.id)],
    ]

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Modifications have been changed."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def add_payment_price(request, payment_method_id):
    """Adds given payment price (via request body) to payment method with
    give id.

    Returns JSON encoded data.
    """
    try:
        price = float(request.POST.get("price", 0))
    except ValueError:
        price = 0.0

    payment_method = get_object_or_404(PaymentMethod, pk=payment_method_id)
    payment_method.prices.create(price=price)
    _update_price_positions(payment_method)

    html = [["#prices", payment_method_prices(request, payment_method_id)]]

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Price has been added"),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def update_payment_prices(request, payment_method_id):
    """Saves/Deletes payment prices with passed ids (via request body)
    dependent on given action (via request body).
    """
    payment_method = get_object_or_404(PaymentMethod, pk=payment_method_id)

    action = request.POST.get("action")
    if action == "delete":
        message = _(u"Prices have been deleted")
        for key in request.POST.keys():
            if key.startswith("delete-"):
                try:
                    id = key.split("-")[1]
                    price = get_object_or_404(PaymentMethodPrice, pk=id)
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
                    price = get_object_or_404(PaymentMethodPrice, pk=id)
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

    _update_price_positions(payment_method)
    html = [["#prices", payment_method_prices(request, payment_method_id)]]

    result = simplejson.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def save_payment_method_data(request, payment_method_id):
    """Saves payment data (via request body) to the payment method with passed
    id.

    This is called via an AJAX request and returns JSON encoded data.
    """
    payment_method = PaymentMethod.objects.get(pk=payment_method_id)
    payment_form = PaymentMethodForm(instance=payment_method, data=request.POST, files=request.FILES)

    form = render_to_string(
        "manage/payment/payment_method_data.html", RequestContext(request, {
        "form": payment_form,
        "payment_method": payment_method,
    }))

    if payment_form.is_valid():
        payment_form.save()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_payment_method", kwargs={"payment_method_id": payment_method.id}),
        msg=_(u"Payment method has been saved."),
    )


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def delete_payment_method(request, payment_method_id):
    """Deletes payment method with passed payment id.

    All customers, which have selected this payment method are getting the
    default payment method.
    """
    try:
        payment_method = PaymentMethod.objects.get(pk=payment_method_id)
    except ObjectDoesNotExist:
        pass
    else:
        for customer in Customer.objects.filter(selected_payment_method=payment_method_id):
            customer.selected_payment_method = payment_utils.get_default_payment_method(request)
            customer.save()

        payment_method.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_payment"),
        msg=_(u"Payment method has been deleted."),
    )


def _update_price_positions(payment_method):
    for i, price in enumerate(payment_method.prices.all()):
        price.priority = (i + 1) * 10
        price.save()
