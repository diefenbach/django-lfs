# python imports
from datetime import datetime

# django imports
from django.contrib.auth.decorators import permission_required
from django.forms import ModelForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import RequestContext

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop
from lfs.criteria.models import CartPriceCriterion
from lfs.criteria.models import UserCriterion
from lfs.payment.models import PaymentMethod
from lfs.shipping.models import ShippingMethod


class CartPriceCriterionForm(ModelForm):
    """
    """
    class Meta:
        model = CartPriceCriterion


class UserCriterionForm(ModelForm):
    """
    """
    class Meta:
        model = UserCriterion


@permission_required("core.manage_shop", login_url="/login/")
def add_criterion(request, template_name="manage/criteria/price_criterion.html"):
    """Adds a new criterion form. By default it adds the form for the price
    criterion.

    This is called via an AJAX request. The result is injected into the right
    DOM node.

    The amount of already existing criteria is passed via request body. This is
    used to calculate the new id for the to added form fields.
    """
    # create a (pseudo) unique id for the the new criterion form fields. This
    # are the seconds since Epoch
    now = datetime.now()
    return HttpResponse(render_to_string(template_name, RequestContext(request, {
        "id": "%s%s" % (now.strftime("%s"), now.microsecond),
    })))


@permission_required("core.manage_shop", login_url="/login/")
def change_criterion_form(request):
    """Changes the changed criterion form to the given type (via request body)
    form.

    This is called via an AJAX request. The result is injected into the right
    DOM node.
    """
    shop = lfs_get_object_or_404(Shop, pk=1)
    countries = shop.shipping_countries.all()

    type = request.POST.get("type", "price")
    template_name = "manage/criteria/%s_criterion.html" % type

    # create a (pseudo) unique id for the the new criterion form fields. This
    # are the seconds since Epoch
    now = datetime.now()
    return HttpResponse(render_to_string(template_name, RequestContext(request, {
        "id": "%s%s" % (now.strftime("%s"), now.microsecond),
        "countries": countries,
        "payment_methods": PaymentMethod.objects.filter(active=True),
        "shipping_methods": ShippingMethod.objects.filter(active=True),
    })))
