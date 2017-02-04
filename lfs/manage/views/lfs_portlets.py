import json

# django imports
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# portlets imports
import portlets.utils
from portlets.models import PortletAssignment
from portlets.models import PortletBlocking
from portlets.models import PortletRegistration
from portlets.models import Slot

# lfs imports
from lfs.core.utils import LazyEncoder


@permission_required("core.manage_shop")
def portlets_inline(request, obj, template_name="manage/portlets/portlets_inline.html"):
    """Displays the assigned portlets for given object.
    """
    ct = ContentType.objects.get_for_model(obj)

    parent_for_portlets = obj.get_parent_for_portlets()
    if parent_for_portlets:
        parent_slots = portlets.utils.get_slots(parent_for_portlets)

    else:
        parent_slots = None

    return render_to_string(template_name, request=request, context={
        "slots": portlets.utils.get_slots(obj),
        "parent_slots": parent_slots,
        "parent_for_portlets": parent_for_portlets,
        "portlet_types": PortletRegistration.objects.filter(active=True),
        "object": obj,
        "object_type_id": ct.id,
    })


@permission_required("core.manage_shop")
def update_portlets(request, object_type_id, object_id):
    """Update portlets blocking.
    """
    # Get content type to which the portlet should be added
    object_ct = ContentType.objects.get(pk=object_type_id)
    obj = object_ct.get_object_for_this_type(pk=object_id)

    blocked_slots = request.POST.getlist("block_slot")

    # Delete all slots that were NOT checked
    PortletBlocking.objects.filter(content_type_id=object_type_id,
                                   content_id=object_id).exclude(slot_id__in=blocked_slots).delete()

    for slot in Slot.objects.filter(id__in=blocked_slots):
        PortletBlocking.objects.get_or_create(slot=slot,
                                              content_type_id=object_type_id,
                                              content_id=object_id)

    result = json.dumps({
        "html": [["#portlets", portlets_inline(request, obj)]],
        "message": _(u"Portlet has been updated.")},
        cls=LazyEncoder
    )
    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def add_portlet(request, object_type_id, object_id, template_name="manage/portlets/portlet_add.html"):
    """Form and logic to add a new portlet to the object with given type and id.
    """
    # Get content type to which the portlet should be added
    object_ct = ContentType.objects.get(pk=object_type_id)
    obj = object_ct.get_object_for_this_type(pk=object_id)

    # Get the portlet type
    portlet_type = (request.POST if request.method == 'POST' else request.GET).get("portlet_type", "")

    if request.method == "POST":
        try:
            ct = ContentType.objects.filter(model=portlet_type.lower())[0]
            mc = ct.model_class()
            form = mc().form(prefix="portlet", data=request.POST)

            if form.is_valid():
                portlet = form.save()

                slot_id = request.POST.get("slot")
                pa = PortletAssignment.objects.create(
                    slot_id=slot_id, content=obj, portlet=portlet, position=1000)

                update_portlet_positions(pa)

                html = [["#portlets", portlets_inline(request, obj)]]

                result = json.dumps({
                    "html": html,
                    "close-dialog": True,
                    "message": _(u"Portlet has been added.")},
                    cls=LazyEncoder
                )
            else:
                html = [["#portlet-form-inline", render_to_string('manage/lfs_form.html', request=request, context={'form': form})]]

                result = json.dumps({
                    "html": html,
                    "close-dialog": False,
                    "message": _(u"Please correct errors and try again.")},
                    cls=LazyEncoder
                )
            return HttpResponse(result, content_type='application/json')

        except ContentType.DoesNotExist:
            pass
    else:
        try:
            portlet_ct = ContentType.objects.filter(model=portlet_type.lower())[0]
            mc = portlet_ct.model_class()
            form = mc().form(prefix="portlet")
            result = render_to_string(template_name, request=request, context={
                "form": form,
                "object_id": object_id,
                "object_type_id": object_ct.id,
                "portlet_type": portlet_type,
                "slots": Slot.objects.all(),
            })

            return HttpResponse(json.dumps({'html': result}),
                                content_type='application/json')

        except ContentType.DoesNotExist:
            pass


@permission_required("core.manage_shop")
@require_POST
def delete_portlet(request, portletassignment_id):
    """Deletes a portlet for given portlet assignment.
    """
    try:
        pa = PortletAssignment.objects.get(pk=portletassignment_id)
    except PortletAssignment.DoesNotExist:
        pass
    else:
        pa.delete()
        update_portlet_positions(pa)
        result = json.dumps({
            "html": [["#portlets", portlets_inline(request, pa.content)]],
            "close-dialog": True,
            "message": _(u"Portlet has been deleted.")},
            cls=LazyEncoder
        )
        return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def edit_portlet(request, portletassignment_id, template_name="manage/portlets/portlet_edit.html"):
    """Form and logic to edit the portlet of the given portlet assignment.
    """
    try:
        pa = PortletAssignment.objects.get(pk=portletassignment_id)
    except PortletAssignment.DoesNotExist:
        return ""

    if request.method == "POST":
        form = pa.portlet.form(prefix="portlet", data=request.POST)
        if form.is_valid():
            form.save()

            # Save the rest
            pa.slot_id = request.POST.get("slot")
            pa.save()

            html = [["#portlets", portlets_inline(request, pa.content)]]

            result = json.dumps({
                "html": html,
                "close-dialog": True,
                "message": _(u"Portlet has been saved.")},
                cls=LazyEncoder
            )
        else:
            html = [["#portlet-form-inline", render_to_string('manage/lfs_form.html', request=request, context={'form': form})]]

            result = json.dumps({
                "html": html,
                "close-dialog": False,
                "message": _(u"Please correct errors and try again.")},
                cls=LazyEncoder
            )
        return HttpResponse(result, content_type='application/json')
    else:
        slots = []
        for slot in Slot.objects.all():
            slots.append({
                "id": slot.id,
                "name": slot.name,
                "selected": slot.id == pa.slot.id,
            })

        form = pa.portlet.form(prefix="portlet")
        return render(request, template_name, {
            "form": form,
            "portletassigment_id": pa.id,
            "slots": slots,
        })


@permission_required("core.manage_shop")
def move_portlet(request, portletassignment_id):
    """
    Moves a portlet up/down within a slot.

    **Parameters:**

        portletassignment_id
            The portlet assignment (hence the portlet) which should be moved.

    **Query String:**

        direction
            The direction to which the portlet should be moved. One of 0 (up)
            or 1 (down).
    """
    try:
        pa = PortletAssignment.objects.get(pk=portletassignment_id)
    except PortletAssignment.DoesNotExist:
        return ""

    direction = request.GET.get("direction", "0")
    if direction == "1":
        pa.position += 15
    else:
        pa.position -= 15
        if pa.position < 0:
            pa.position = 10
    pa.save()

    update_portlet_positions(pa)

    result = json.dumps({
        "html": [["#portlets", portlets_inline(request, pa.content)]]},
        cls=LazyEncoder
    )

    return HttpResponse(result, content_type='application/json')


def update_portlet_positions(pa):
    """Updates the portlet positions for a content object and a slot.

    **Parameters:**

        pa
            PortletAssignment which contains the slot and the content object
            in question.

    **Permission:**

        None (as this is not called from outside)
    """
    for i, pa in enumerate(PortletAssignment.objects.filter(content_type=pa.content_type, content_id=pa.content_id, slot=pa.slot)):
        pa.position = (i + 1) * 10
        pa.save()
