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
from lfs.core.models import Action
from lfs.core.models import ActionGroup
from lfs.core.utils import LazyEncoder
from lfs.manage.actions.forms import ActionForm
from lfs.manage.actions.forms import ActionAddForm


# Views
@permission_required("core.manage_shop")
def manage_actions(request):
    """Dispatches to the first action or to the form to add a action (if there
    is no action yet).
    """
    try:
        action = Action.objects.all()[0]
        url = reverse("lfs_manage_action", kwargs={"id": action.id})
    except IndexError:
        url = reverse("lfs_no_actions")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
def manage_action(request, id, template_name="manage/actions/action.html"):
    """Displays the manage view for the action with passed id.
    """
    action = get_object_or_404(Action, pk=id)

    return render(request, template_name, {
        "action": action,
        "data": data(request, action),
        "navigation": navigation(request, action),
    })


@permission_required("core.manage_shop")
def no_actions(request, template_name="manage/actions/no_actions.html"):
    """Displays the a view when there are no actions.
    """
    return render(request, template_name, {})


# Parts
def data(request, action, form=None, template_name="manage/actions/data_tab.html"):
    """Provides a form to edit the action with the passed id.
    """
    if form is None:
        form = ActionForm(instance=action)

    return render_to_string(template_name, request=request, context={
        "action": action,
        "groups": ActionGroup.objects.all(),
        "form": form,
        "current_id": action.id,
    })


def navigation(request, action, template_name="manage/actions/navigation.html"):
    """
    """
    return render_to_string(template_name, request=request, context={
        "current_action": action,
        "groups": ActionGroup.objects.all(),
    })


# Actions
@permission_required("core.manage_shop")
@require_POST
def save_action(request, id):
    """Saves the actions with passed id.
    """
    action = get_object_or_404(Action, pk=id)

    form = ActionForm(instance=action, data=request.POST)
    if form.is_valid():
        form.save()
        _update_positions()
        action = get_object_or_404(Action, pk=action.id)
        form = None
        message = _(u"The action has been saved.")
    else:
        message = _(u"Please correct the indicated errors.")

    html = [
        ["#data", data(request, action, form)],
        ["#navigation", navigation(request, action)],
    ]

    result = json.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def add_action(request, template_name="manage/actions/add_action.html"):
    """Provides a form to add a new action.
    """
    if request.method == "POST":
        form = ActionAddForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            action = form.save()
            _update_positions()

            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_action", kwargs={"id": action.id}),
                msg=_(u"Action has been added."),
            )
    else:
        form = ActionAddForm()

    return render(request, template_name, {
        "form": form,
        "groups": ActionGroup.objects.all(),
        "came_from": (request.POST if request.method == 'POST' else request.GET).get("came_from",
                                                                                     reverse("lfs_manage_actions")),
    })


@permission_required("core.manage_shop")
@require_POST
def delete_action(request, id):
    """Deletes the action with passed id.
    """
    action = get_object_or_404(Action, pk=id)
    action.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_actions"),
        msg=_(u"Action has been deleted."),
    )


@permission_required("core.manage_shop")
@require_POST
def sort_actions(request):
    """Sorts actions after drag 'n drop.
    """
    action_list = request.POST.get("objs", "").split('&')
    if len(action_list) > 0:
        pos = 10
        for action_str in action_list:
            action_id = action_str.split('=')[1]
            action_obj = Action.objects.get(pk=action_id)
            action_obj.position = pos
            action_obj.save()
            pos = pos + 10

        result = json.dumps({
            "message": _(u"The actions have been sorted."),
        }, cls=LazyEncoder)

        return HttpResponse(result, content_type='application/json')


def _update_positions():
    """Updates the positions of all actions.
    """
    for group in ActionGroup.objects.all():
        for i, action in enumerate(group.actions.all()):
            action.position = (i + 1) * 10
            action.save()
