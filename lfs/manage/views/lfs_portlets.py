import json

# django imports
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
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
    """Displays the assigned portlets for given object."""
    ct = ContentType.objects.get_for_model(obj)

    parent_for_portlets = obj.get_parent_for_portlets()
    if parent_for_portlets:
        parent_slots = portlets.utils.get_slots(parent_for_portlets)

    else:
        parent_slots = None

    return render_to_string(
        template_name,
        request=request,
        context={
            "slots": portlets.utils.get_slots(obj),
            "parent_slots": parent_slots,
            "parent_for_portlets": parent_for_portlets,
            "portlet_types": PortletRegistration.objects.filter(active=True),
            "object": obj,
            "object_type_id": ct.id,
        },
    )


@permission_required("core.manage_shop")
def update_portlets(request, object_type_id, object_id):
    """Update portlets blocking."""
    # Get content type to which the portlet should be added
    object_ct = ContentType.objects.get(pk=object_type_id)
    obj = object_ct.get_object_for_this_type(pk=object_id)

    blocked_slots = request.POST.getlist("block_slot")

    # Delete all slots that were NOT checked
    PortletBlocking.objects.filter(content_type_id=object_type_id, content_id=object_id).exclude(
        slot_id__in=blocked_slots
    ).delete()

    for slot in Slot.objects.filter(id__in=blocked_slots):
        PortletBlocking.objects.get_or_create(slot=slot, content_type_id=object_type_id, content_id=object_id)

    # Check if this is an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        result = json.dumps(
            {"html": [["#portlets", portlets_inline(request, obj)]], "message": _("Portlet has been updated.")},
            cls=LazyEncoder,
        )
        return HttpResponse(result, content_type="application/json")
    else:
        # Regular form submission - redirect back to the portlets page
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.urls import reverse

        messages.success(request, _("Portlet has been updated."))

        # Determine the correct redirect URL based on object type
        if hasattr(obj, "id") and obj.id == 1:  # Root page
            return redirect(reverse("lfs_manage_page_portlets", kwargs={"id": obj.id}))
        else:
            return redirect(reverse("lfs_manage_page_portlets", kwargs={"id": obj.id}))


@permission_required("core.manage_shop")
def add_portlet(request, object_type_id, object_id, template_name="manage/portlets/portlet_add.html"):
    """Form and logic to add a new portlet to the object with given type and id."""
    # Get content type to which the portlet should be added
    object_ct = ContentType.objects.get(pk=object_type_id)
    obj = object_ct.get_object_for_this_type(pk=object_id)

    # Get the portlet type
    portlet_type = (request.POST if request.method == "POST" else request.GET).get("portlet_type", "")

    # Check if portlet_type is empty
    if not portlet_type:
        return HttpResponse("<div class='alert alert-warning'>Please select a portlet type.</div>")

    if request.method == "POST":
        try:
            ct_queryset = ContentType.objects.filter(model=portlet_type.lower())
            if not ct_queryset.exists():
                raise ContentType.DoesNotExist()

            ct = ct_queryset[0]
            mc = ct.model_class()
            form = mc().form(prefix="portlet", data=request.POST)

            if form.is_valid():
                portlet = form.save()

                slot_id = request.POST.get("slot")
                pa = PortletAssignment.objects.create(slot_id=slot_id, content=obj, portlet=portlet, position=1000)

                update_portlet_positions(pa)

                from django.contrib import messages
                from django.shortcuts import redirect
                from django.urls import reverse

                messages.success(request, _("Portlet has been added."))
                return redirect(reverse("lfs_manage_page_portlets", kwargs={"id": obj.id}))
            else:
                # Form has errors, re-render the form
                try:
                    portlet_registration = PortletRegistration.objects.get(type=portlet_type)
                    portlet_type_name = portlet_registration.name
                except PortletRegistration.DoesNotExist:
                    portlet_type_name = portlet_type

                return render(
                    request,
                    template_name,
                    {
                        "form": form,
                        "object_id": object_id,
                        "object_type_id": object_ct.id,
                        "portlet_type": portlet_type,
                        "portlet_type_name": portlet_type_name,
                        "slots": Slot.objects.all(),
                    },
                )

        except ContentType.DoesNotExist:
            # Handle invalid portlet type
            return HttpResponse("<div class='alert alert-danger'>Invalid portlet type.</div>")
    else:
        try:
            portlet_ct_queryset = ContentType.objects.filter(model=portlet_type.lower())
            if not portlet_ct_queryset.exists():
                raise ContentType.DoesNotExist()

            portlet_ct = portlet_ct_queryset[0]
            mc = portlet_ct.model_class()
            form = mc().form(prefix="portlet")

            # Get portlet type name for modal title
            try:
                portlet_registration = PortletRegistration.objects.get(type=portlet_type)
                portlet_type_name = portlet_registration.name
            except PortletRegistration.DoesNotExist:
                portlet_type_name = portlet_type

            return render(
                request,
                template_name,
                {
                    "form": form,
                    "object_id": object_id,
                    "object_type_id": object_ct.id,
                    "portlet_type": portlet_type,
                    "portlet_type_name": portlet_type_name,
                    "slots": Slot.objects.all(),
                },
            )

        except ContentType.DoesNotExist:
            # Handle invalid portlet type
            return HttpResponse("<div class='alert alert-danger'>Invalid portlet type.</div>")


@permission_required("core.manage_shop")
def delete_portlet(request, portletassignment_id, template_name="manage/portlets/delete_portlet.html"):
    """Shows confirmation modal for GET, deletes portlet for POST."""
    try:
        pa = PortletAssignment.objects.get(pk=portletassignment_id)
    except PortletAssignment.DoesNotExist:
        if request.method == "GET":
            return HttpResponse("<div class='alert alert-danger'>Portlet not found.</div>")
        else:
            # POST request - redirect back to portlets page even if portlet not found
            from django.contrib import messages
            from django.shortcuts import redirect
            from django.urls import reverse

            messages.error(request, _("Portlet not found."))
            # We need to get the content object from somewhere, but since portlet doesn't exist,
            # we'll redirect to a general portlets page or the root page
            return redirect(reverse("lfs_manage_page_portlets", kwargs={"id": 1}))

    if request.method == "GET":
        # Show confirmation modal
        if request.headers.get("HX-Request"):
            result = render_to_string(
                template_name,
                request=request,
                context={
                    "portlet": pa.portlet,
                    "portlet_assignment": pa,
                },
            )
            return HttpResponse(result)
        else:
            # Legacy JSON response for non-HTMX requests
            result = render_to_string(
                template_name,
                request=request,
                context={
                    "portlet": pa.portlet,
                    "portlet_assignment": pa,
                },
            )
            return HttpResponse(json.dumps({"html": result}), content_type="application/json")
    else:
        # POST request - actually delete the portlet
        content_obj = pa.content
        pa.delete()
        update_portlet_positions(pa)

        # Always redirect back to the portlets page after deletion
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.urls import reverse

        messages.success(request, _("Portlet has been deleted."))
        return redirect(reverse("lfs_manage_page_portlets", kwargs={"id": content_obj.id}))


@permission_required("core.manage_shop")
def edit_portlet(request, portletassignment_id, template_name="manage/portlets/portlet_edit.html"):
    """Form and logic to edit the portlet of the given portlet assignment."""
    try:
        pa = PortletAssignment.objects.get(pk=portletassignment_id)
    except PortletAssignment.DoesNotExist:
        if request.headers.get("HX-Request"):
            return HttpResponse("<div class='alert alert-danger'>Portlet not found.</div>")
        else:
            return HttpResponse("")

    if request.method == "POST":
        form = pa.portlet.form(prefix="portlet", data=request.POST)
        if form.is_valid():
            form.save()

            # Save the rest
            pa.slot_id = request.POST.get("slot")
            pa.save()

            # Always redirect to the portlets page after successful save
            from django.contrib import messages
            from django.shortcuts import redirect
            from django.urls import reverse

            messages.success(request, _("Portlet has been saved."))
            return redirect(reverse("lfs_manage_page_portlets", kwargs={"id": pa.content.id}))
        else:
            # Form has errors, re-render the form
            slots = []
            for slot in Slot.objects.all():
                slots.append(
                    {
                        "id": slot.id,
                        "name": slot.name,
                        "selected": slot.id == pa.slot.id,
                    }
                )

            return render(
                request,
                template_name,
                {
                    "form": form,
                    "portletassigment_id": pa.id,
                    "slots": slots,
                },
            )
    else:
        # GET request - show the form
        slots = []
        for slot in Slot.objects.all():
            slots.append(
                {
                    "id": slot.id,
                    "name": slot.name,
                    "selected": slot.id == pa.slot.id,
                }
            )

        form = pa.portlet.form(prefix="portlet")

        return render(
            request,
            template_name,
            {
                "form": form,
                "portletassigment_id": pa.id,
                "slots": slots,
            },
        )


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

    result = json.dumps({"html": [["#portlets", portlets_inline(request, pa.content)]]}, cls=LazyEncoder)

    return HttpResponse(result, content_type="application/json")


@permission_required("core.manage_shop")
@require_POST
def sort_portlets(request):
    """Sorts portlets after drag 'n drop."""
    portlet_id = int(request.POST.get("portlet_id", ""))
    to_slot = int(request.POST.get("to_slot", ""))
    new_index = int(request.POST.get("new_index", ""))

    # portlet which has been dragged and dropped
    dnd_portlet = PortletAssignment.objects.get(pk=portlet_id)

    # Update the slot if it changed
    if dnd_portlet.slot_id != to_slot:
        dnd_portlet.slot_id = to_slot
        dnd_portlet.save()

    # Get all portlets in the target slot ordered by position (excluding the dragged one)
    portlets_in_slot = list(
        PortletAssignment.objects.filter(
            content_type=dnd_portlet.content_type, content_id=dnd_portlet.content_id, slot_id=to_slot
        )
        .exclude(pk=portlet_id)
        .order_by("position")
    )

    if new_index == 1:
        new_position = 10
        for portlet in portlets_in_slot:
            portlet.position += 10
            portlet.save()
    elif new_index > len(portlets_in_slot):
        new_position = portlets_in_slot[-1].position + 10
    else:
        new_position = portlets_in_slot[new_index - 1].position
        for portlet in portlets_in_slot[new_index - 1 :]:
            portlet.position += 10
            portlet.save()

    # Set the new position for the sorted portlet
    dnd_portlet.position = new_position
    dnd_portlet.save()

    # Update all positions to ensure consistency
    update_portlet_positions(dnd_portlet)

    return HttpResponse()


def update_portlet_positions(pa):
    """Updates the portlet positions for a content object and a slot.

    **Parameters:**

        pa
            PortletAssignment which contains the slot and the content object
            in question.

    **Permission:**

        None (as this is not called from outside)
    """
    queryset = PortletAssignment.objects.filter(
        content_type=pa.content_type, content_id=pa.content_id, slot=pa.slot
    ).order_by("position")

    for i, portlet in enumerate(queryset):
        portlet.position = (i + 1) * 10
        portlet.save()
