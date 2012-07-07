# django imports
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.views.decorators.http import require_POST

# lfs imports
import lfs.voucher.utils
from lfs.core.utils import LazyEncoder
from lfs.core.utils import render_to_ajax_response
from lfs.tax.models import Tax
from lfs.voucher.models import Voucher
from lfs.voucher.models import VoucherGroup
from lfs.voucher.models import VoucherOptions
from lfs.manage.voucher.forms import VoucherForm
from lfs.manage.voucher.forms import VoucherGroupAddForm
from lfs.manage.voucher.forms import VoucherGroupForm
from lfs.manage.voucher.forms import VoucherOptionsForm


# Views
@permission_required("core.manage_shop")
def no_vouchers(request, template_name="manage/voucher/no_vouchers.html"):
    """Displays that no vouchers exist.
    """
    if len(VoucherGroup.objects.all()) == 0:
        return render_to_response(template_name, RequestContext(request, {}))
    else:
        return manage_vouchers(request)


@permission_required("core.manage_shop")
def voucher_group(request, id, template_name="manage/voucher/voucher_group.html"):
    """Main view to display a voucher group.
    """
    try:
        voucher_group = VoucherGroup.objects.get(pk=id)
    except VoucherGroup.DoesNotExist:
        return manage_vouchers(request)

    return render_to_response(template_name, RequestContext(request, {
        "voucher_group": voucher_group,
        "data_tab": data_tab(request, voucher_group),
        "vouchers_tab": vouchers_tab(request, voucher_group),
        "options_tab": options_tab(request),
        "navigation": navigation(request, voucher_group),
    }))


# Parts
def navigation(request, voucher_group, template_name="manage/voucher/navigation.html"):
    """Displays the navigation.
    """
    return render_to_string(template_name, RequestContext(request, {
        "voucher_group": voucher_group,
        "voucher_groups": VoucherGroup.objects.all(),
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
        "voucher_group": voucher_group,
        "form": form,
    }))


def vouchers_tab(request, voucher_group, deleted=False, template_name="manage/voucher/vouchers.html"):
    """Displays the vouchers tab
    """
    vouchers = voucher_group.vouchers.all()
    paginator = Paginator(vouchers, 20)
    page = paginator.page(request.REQUEST.get("page", 1))

    taxes = Tax.objects.all()

    if request.method == "POST" and deleted == False:
        voucher_form = VoucherForm(data=request.POST)
    else:
        voucher_form = VoucherForm()

    return render_to_string(template_name, RequestContext(request, {
        "voucher_group": voucher_group,
        "taxes": taxes,
        "form": voucher_form,
        "vouchers_inline": vouchers_inline(request, voucher_group, vouchers, paginator, page),
    }))


def options_tab(request, template_name="manage/voucher/options.html"):
    """Displays the vouchers options
    """
    try:
        voucher_options = VoucherOptions.objects.all()[0]
    except IndexError:
        voucher_options = VoucherOptions.objects.create()

    form = VoucherOptionsForm(instance=voucher_options)

    return render_to_string(template_name, RequestContext(request, {
        "form": form,
    }))


def vouchers_inline(request, voucher_group, vouchers, paginator, page, template_name="manage/voucher/vouchers_inline.html"):
    """Displays the pages of the vouchers
    """
    return render_to_string(template_name, RequestContext(request, {
        "paginator": paginator,
        "page": page,
        "vouchers": vouchers,
        "voucher_group": voucher_group,
    }))


# Actions
@permission_required("core.manage_shop")
def set_vouchers_page(request):
    """Sets the displayed voucher page.
    """
    group_id = request.REQUEST.get("group")
    voucher_group = VoucherGroup.objects.get(pk=group_id)
    vouchers = voucher_group.vouchers.all()
    paginator = Paginator(vouchers, 20)
    page = paginator.page(request.REQUEST.get("page", 1))

    html = (
        ("#vouchers-inline", vouchers_inline(request, voucher_group, vouchers, paginator, page)),
    )

    return HttpResponse(
        simplejson.dumps({"html": html}, cls=LazyEncoder))


@permission_required("core.manage_shop")
def manage_vouchers(request):
    """Redirects to the first voucher group or to no voucher groups view.
    """
    try:
        voucher_group = VoucherGroup.objects.all()[0]
    except IndexError:
        url = reverse("lfs_no_vouchers")
    else:
        url = reverse("lfs_manage_voucher_group", kwargs={"id": voucher_group.id})

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
def add_vouchers(request, group_id):
    """
    """
    voucher_group = VoucherGroup.objects.get(pk=group_id)
    form = VoucherForm(data=request.POST)

    if form.is_valid():
        try:
            amount = int(request.POST.get("amount", 0))
        except TypeError:
            amount = 0

        # TODO: Fix the possibility of an infinte loop.
        for i in range(0, amount):
            while 1:
                try:
                    Voucher.objects.create(
                        number=lfs.voucher.utils.create_voucher_number(),
                        group=voucher_group,
                        creator=request.user,
                        kind_of=request.POST.get("kind_of", 0),
                        value=request.POST.get("value", 0.0),
                        start_date=request.POST.get("start_date"),
                        end_date=request.POST.get("end_date"),
                        effective_from=request.POST.get("effective_from"),
                        tax_id=request.POST.get("tax"),
                        limit=request.POST.get("limit")
                    )
                except IntegrityError:
                    pass
                else:
                    break
        msg = _(u"Vouchers have been created.")
    else:
        msg = ""

    return render_to_ajax_response(
        (("#vouchers", vouchers_tab(request, voucher_group)), ),
        msg)


@permission_required("core.manage_shop")
@require_POST
def delete_vouchers(request, group_id):
    """Deletes checked vouchers.
    """
    voucher_group = VoucherGroup.objects.get(pk=group_id)
    vouchers = Voucher.objects.filter(pk__in=request.POST.getlist("voucher-ids"))

    for voucher in vouchers:
        voucher.delete()

    return render_to_ajax_response(
        (("#vouchers", vouchers_tab(request, voucher_group, deleted=True)), ),
        _(u"Vouchers have been deleted."))


@permission_required("core.manage_shop")
def add_voucher_group(request, template_name="manage/voucher/add_voucher_group.html"):
    """Adds a voucher group
    """
    if request.method == "POST":
        form = VoucherGroupAddForm(data=request.POST)
        if form.is_valid():
            voucher_group = form.save(commit=False)
            voucher_group.creator = request.user
            voucher_group.save()
            url = reverse("lfs_manage_voucher_group", kwargs={"id": voucher_group.id})
            return HttpResponseRedirect(url)
    else:
        form = VoucherGroupAddForm()

    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "voucher_groups": VoucherGroup.objects.all(),
        "came_from": request.REQUEST.get("came_from", reverse("lfs_manage_vouchers")),
    }))


@permission_required("core.manage_shop")
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
        _(u"Voucher data has been saved."))


@permission_required("core.manage_shop")
@require_POST
def delete_voucher_group(request, id):
    """Deletes voucher group with given id and all assigned vouchers.
    """
    try:
        voucher_group = VoucherGroup.objects.get(pk=id)
    except VoucherGroup.DoesNotExist:
        return HttpResponseRedirect(reverse("lfs_manage_vouchers"))
    else:
        voucher_group.delete()
        return lfs.core.utils.set_message_cookie(
            url=reverse("lfs_manage_vouchers"),
            msg=_(u"Voucher group and assigned vouchers have been deleted."),
        )


@permission_required("core.manage_shop")
def save_voucher_options(request):
    """Saves voucher options.
    """
    try:
        voucher_options = VoucherOptions.objects.all()[0]
    except IndexError:
        voucher_options = VoucherOptions.objects.create()

    form = VoucherOptionsForm(instance=voucher_options, data=request.POST)
    if form.is_valid():
        form.save()

    return render_to_ajax_response(
        (("#options_tab", options_tab(request)),),
        _(u"Voucher options has been saved.")
    )


def _update_positions():
    for i, voucher_group in enumerate(VoucherGroup.objects.all()):
        voucher_group.position = (i + 1) * 10
        voucher_group.save()
