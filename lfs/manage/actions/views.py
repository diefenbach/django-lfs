from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, DeleteView, CreateView

from lfs.core.models import Action
from lfs.core.models import ActionGroup


@permission_required("core.manage_shop")
def manage_actions(request):
    """Dispatches to the first action or to the form to add a action (if there
    is no action yet).
    """
    try:
        action = Action.objects.all()[0]
        url = reverse("lfs_manage_action", kwargs={"pk": action.id})
    except IndexError:
        url = reverse("lfs_no_actions")

    return HttpResponseRedirect(url)


class ActionUpdateView(PermissionRequiredMixin, UpdateView):
    model = Action
    fields = ("active", "title", "link", "group")
    template_name = "manage/actions/action.html"
    permission_required = "core.manage_shop"
    context_object_name = "action"
    permission_required = "core.manage_shop"

    def get_success_url(self):
        return reverse_lazy("lfs_manage_action", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = ActionGroup.objects.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        _update_positions()
        return response


class NoActionsView(PermissionRequiredMixin, TemplateView):
    """Displays a view when there are no actions."""

    template_name = "manage/actions/no_actions.html"
    permission_required = "core.manage_shop"


class ActionCreateView(PermissionRequiredMixin, CreateView):
    model = Action
    fields = ("title", "link", "group")
    template_name = "manage/actions/add_action.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = ActionGroup.objects.all()
        context["came_from"] = self.request.POST.get("came_from", reverse("lfs_manage_actions"))
        return context

    def form_valid(self, form):
        action = form.save()
        _update_positions()
        
        if self.request.headers.get('HX-Request') == 'true':
            response = HttpResponse()
            response["HX-Redirect"] = reverse("lfs_manage_action", kwargs={"pk": action.id})
            return response
        
        messages.success(self.request, _("Action has been added."))
        return HttpResponseRedirect(reverse("lfs_manage_action", kwargs={"pk": action.id}))


class ActionDeleteView(PermissionRequiredMixin, DeleteView):
    """Deletes the action with passed id."""

    model = Action
    permission_required = "core.manage_shop"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        first_action = Action.objects.exclude(pk=self.object.pk).first()
        if first_action:
            return HttpResponseRedirect(reverse("lfs_manage_action", kwargs={"pk": first_action.id}))
        else:
            response = HttpResponse()
            response["HX-Redirect"] = reverse("lfs_no_actions")
            return response


@permission_required("core.manage_shop")
@require_POST
def sort_actions(request):
    """Sorts actions after drag 'n drop."""
    item_id = int(request.POST.get("item_id", ""))
    to_list = int(request.POST.get("to_list", ""))
    new_index = int(request.POST.get("new_index", ""))

    action = Action.objects.get(pk=item_id)
    action.group_id = to_list
    action.position = new_index * 10 + 5
    action.save()

    _update_positions()

    return HttpResponse()


def _update_positions():
    """Updates the positions of all actions."""
    for group in ActionGroup.objects.all():
        for i, action in enumerate(group.actions.all()):
            action.position = (i + 1) * 10
            action.save()
