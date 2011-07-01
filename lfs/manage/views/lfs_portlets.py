# django imports
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# portlets imports
import portlets.utils
from portlets.models import PortletAssignment
from portlets.models import PortletBlocking
from portlets.models import PortletRegistration
from portlets.models import Slot

# lfs imports
import lfs.core.utils
from lfs.core.utils import LazyEncoder


@permission_required("core.manage_shop", login_url="/login/")
def portlets_inline(request, obj, template_name="manage/portlets/portlets_inline.html"):
    """Displays the assigned portlets for given object.
    """
    ct = ContentType.objects.get_for_model(obj)

    parent_for_portlets = obj.get_parent_for_portlets()
    if parent_for_portlets:
        parent_slots = portlets.utils.get_slots(parent_for_portlets)
    else:
        parent_slots = None

    return render_to_string(template_name, RequestContext(request, {
        "slots": portlets.utils.get_slots(obj),
        "parent_slots": parent_slots,
        "parent_for_portlets": parent_for_portlets,
        "portlet_types": PortletRegistration.objects.filter(active=True),
        "object": obj,
        "object_type_id": ct.id,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def update_portlets(request, object_type_id, object_id):
    """Update portlets blocking.
    """
    # Get content type to which the portlet should be added
    object_ct = ContentType.objects.get(pk=object_type_id)
    object = object_ct.get_object_for_this_type(pk=object_id)

    blocked_slots = request.POST.getlist("block_slot")

    for slot in Slot.objects.all():
        if str(slot.id) in blocked_slots:
            try:
                PortletBlocking.objects.create(
                    slot_id=slot.id, content_type_id=object_type_id, content_id=object_id)
            except IntegrityError:
                pass

        else:
            try:
                pb = PortletBlocking.objects.get(
                    slot=slot, content_type=object_type_id, content_id=object_id)
                pb.delete()
            except PortletBlocking.DoesNotExist:
                pass

        html = portlets_inline(request, object)

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Portlet has been updated.")},
        cls=LazyEncoder
    )
    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def add_portlet(request, object_type_id, object_id, template_name="manage/portlets/portlet_add.html"):
    """Form and logic to add a new portlet to the object with given type and id.
    """
    # Get content type to which the portlet should be added
    object_ct = ContentType.objects.get(pk=object_type_id)
    object = object_ct.get_object_for_this_type(pk=object_id)

    # Get the portlet type
    portlet_type = request.REQUEST.get("portlet_type", "")

    if request.method == "POST":
        try:
            ct = ContentType.objects.filter(model=portlet_type.lower())[0]
            mc = ct.model_class()
            form = mc().form(prefix="portlet", data=request.POST)
            portlet = form.save()

            slot_id = request.POST.get("slot")
            position = request.POST.get("position")
            PortletAssignment.objects.create(
                slot_id=slot_id, content=object, portlet=portlet, position=position)

            html = [["#portlets", portlets_inline(request, object)]]

            result = simplejson.dumps({
                "html": html,
                "close-dialog": True,
                "message": _(u"Portlet has been added.")},
                cls=LazyEncoder
            )
            return HttpResponse(result)

        except ContentType.DoesNotExist:
            pass
    else:
        try:
            portlet_ct = ContentType.objects.filter(model=portlet_type.lower())[0]
            mc = portlet_ct.model_class()
            form = mc().form(prefix="portlet")
            return render_to_response(template_name, RequestContext(request, {
                "form": form,
                "object_id": object_id,
                "object_type_id": object_ct.id,
                "portlet_type": portlet_type,
                "slots": Slot.objects.all(),
            }))
        except ContentType.DoesNotExist:
            pass


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def delete_portlet(request, portletassignment_id):
    """Deletes a portlet for given portlet assignment.
    """
    try:
        pa = PortletAssignment.objects.get(pk=portletassignment_id)
    except PortletAssignment.DoesNotExist:
        pass
    else:
        pa.delete()
        return lfs.core.utils.set_message_cookie(
            request.META.get("HTTP_REFERER"),
            msg=_(u"Portlet has been deleted.")
        )


@permission_required("core.manage_shop", login_url="/login/")
def edit_portlet(request, portletassignment_id, template_name="manage/portlets/portlet_edit.html"):
    """Form and logic to edit the portlet of the given portlet assignment.
    """
    try:
        pa = PortletAssignment.objects.get(pk=portletassignment_id)
    except PortletAssignment.DoesNotExist:
        return ""

    if request.method == "POST":
        form = pa.portlet.form(prefix="portlet", data=request.POST)
        portlet = form.save()

        # Save the rest
        pa.slot_id = request.POST.get("slot")
        pa.position = request.POST.get("position")
        pa.save()

        html = [["#portlets", portlets_inline(request, pa.content)]]

        result = simplejson.dumps({
            "html": html,
            "close-dialog": True,
            "message": _(u"Portlet has been saved.")},
            cls=LazyEncoder
        )
        return HttpResponse(result)
    else:
        slots = []
        for slot in Slot.objects.all():
            slots.append({
                "id": slot.id,
                "name": slot.name,
                "selected": slot.id == pa.slot.id,
            })

        form = pa.portlet.form(prefix="portlet")
        return render_to_response(template_name, RequestContext(request, {
            "form": form,
            "portletassigment_id": pa.id,
            "slots": slots,
            "position": pa.position,
        }))
