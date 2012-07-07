# django imports
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
import lfs.criteria.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder
from lfs.discounts.models import Discount
from lfs.manage.discounts.forms import DiscountForm


@permission_required("core.manage_shop")
def manage_discounts(request):
    """Dispatches to the first discount or to the add discount method
    form if there is no discount yet.
    """
    try:
        discount = Discount.objects.all()[0]
    except IndexError:
        url = reverse("lfs_manage_no_discounts")
    else:
        url = reverse("lfs_manage_discount", kwargs={"id": discount.id})

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
def manage_discount(request, id, template_name="manage/discounts/discount.html"):
    """The main view to manage the discount with given id.

    This view collects the various parts of the discount form (data, criteria,
    and displays them.
    """
    try:
        discount = Discount.objects.get(pk=id)
    except Discount.DoesNotExist:
        return HttpResponseRedirect(reverse("lfs_manage_discounts"))

    return render_to_response(template_name, RequestContext(request, {
        "discount": discount,
        "navigation": navigation(request),
        "data": discount_data(request, id),
        "criteria": discount_criteria(request, id),
    }))


@permission_required("core.manage_shop")
def no_discounts(request, template_name="manage/discounts/no_discounts.html"):
    """Displays no discounts view
    """
    return render_to_response(template_name, RequestContext(request, {}))


# Parts of the manage discount view.
@permission_required("core.manage_shop")
def navigation(request, template_name="manage/discounts/navigation.html"):
    """Returns the navigation for the discount view.
    """
    try:
        current_id = int(request.path.split("/")[-1])
    except ValueError:
        current_id = ""

    return render_to_string(template_name, RequestContext(request, {
        "current_id": current_id,
        "discounts": Discount.objects.all(),
    }))


@permission_required("core.manage_shop")
def discount_data(request, id, template_name="manage/discounts/data.html"):
    """Returns the discount data as html.

    This view is used as a part within the manage discount view.
    """
    discount = Discount.objects.get(pk=id)

    return render_to_string(template_name, RequestContext(request, {
        "form": DiscountForm(instance=discount),
        "discount": discount,
    }))


@permission_required("core.manage_shop")
def discount_criteria(request, id, template_name="manage/discounts/criteria.html"):
    """Returns the criteria of the discount with passed id as HTML.

    This view is used as a part within the manage discount view.
    """
    discount = Discount.objects.get(pk=id)

    criteria = []
    position = 0
    for criterion_object in discount.get_criteria():
        position += 10
        criterion_html = criterion_object.get_content_object().render(request, position)
        criteria.append(criterion_html)

    return render_to_string(template_name, RequestContext(request, {
        "discount": discount,
        "criteria": criteria,
    }))


# Actions
@permission_required("core.manage_shop")
def add_discount(request, template_name="manage/discounts/add_discount.html"):
    """Provides an add form and saves a new discount method.
    """
    if request.method == "POST":
        form = DiscountForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_discount = form.save()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_discount", kwargs={"id": new_discount.id}),
                msg=_(u"Discount method has been added."),
            )
    else:
        form = DiscountForm()

    return render_to_response(template_name, RequestContext(request, {
        "navigation": navigation(request),
        "form": form,
        "came_from": request.REQUEST.get("came_from", reverse("lfs_manage_discounts")),
    }))


@permission_required("core.manage_shop")
def save_discount_criteria(request, id):
    """Saves the criteria for the discount with given id. The criteria
    are passed via request body.
    """
    discount = lfs_get_object_or_404(Discount, pk=id)
    discount.save_criteria(request)

    html = [["#criteria", discount_criteria(request, id)]]

    result = simplejson.dumps({
        "html": html,
        "message": _("Modifications have been changed."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop")
def save_discount_data(request, id):
    """Saves discount data (via request body) to the discount with passed
    id.

    This is called via an AJAX request and returns JSON encoded data.
    """
    discount = Discount.objects.get(pk=id)
    discount_form = DiscountForm(instance=discount, data=request.POST)

    if discount_form.is_valid():
        discount_form.save()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_discount", kwargs={"id": id}),
        msg=_(u"Discount data has been saved."),
    )


@permission_required("core.manage_shop")
@require_POST
def delete_discount(request, id):
    """Deletes discount with passed id.
    """
    try:
        discount = Discount.objects.get(pk=id)
    except ObjectDoesNotExist:
        pass
    else:
        discount.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_discounts"),
        msg=_(u"Discount has been deleted."),
    )
