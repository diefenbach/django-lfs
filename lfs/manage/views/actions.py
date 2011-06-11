# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.core.models import Action
from lfs.core.models import ActionGroup


class ActionForm(ModelForm):
    """Form to edit an action.
    """
    class Meta:
        model = Action
        exclude = ("parent", "place")


class ActionAddForm(ActionForm):
    """Form to add a action
    """
    class Meta:
        model = Action
        fields = ("title", "group")


@permission_required("core.manage_shop", login_url="/login/")
def manage_actions(request):
    """Dispatches to the first action or to the form to add a action (if there is no
    action yet).
    """
    try:
        action = Action.objects.all()[0]
        url = reverse("lfs_manage_action", kwargs={"id": action.id})
    except IndexError:
        url = reverse("lfs_add_action")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop", login_url="/login/")
def manage_action(request, id, template_name="manage/shop/action.html"):
    """Provides a form to edit the action with the passed id.
    """
    action = get_object_or_404(Action, pk=id)
    if request.method == "POST":
        form = ActionForm(instance=action, data=request.POST, files=request.FILES)
        if form.is_valid():
            new_action = form.save()
            _update_positions()

            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_action", kwargs={"id": action.id}),
                msg=_(u"Action has been saved."),
            )
    else:
        form = ActionForm(instance=action)

    return render_to_response(template_name, RequestContext(request, {
        "action": action,
        "groups": ActionGroup.objects.all(),
        "form": form,
        "current_id": int(id),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def add_action(request, template_name="manage/shop/add_action.html"):
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

    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "groups": ActionGroup.objects.all(),
    }))


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def delete_action(request, id):
    """Deletes the action with passed id.
    """
    action = get_object_or_404(Action, pk=id)
    action.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_actions"),
        msg=_(u"Action has been deleted."),
    )


def _update_positions():
    """Updates the positions of all actions.
    """
    for group in ActionGroup.objects.all():
        for i, action in enumerate(group.actions.all()):
            action.position = (i + 1) * 10
            action.save()
