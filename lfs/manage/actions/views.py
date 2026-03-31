from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.views.generic import RedirectView
from django.views.generic import View


from lfs.core.models import Action
from lfs.core.models import ActionGroup
from lfs.manage.mixins import DirectDeleteMixin


class ManageActionsView(PermissionRequiredMixin, RedirectView):
    """Dispatches to the first action or to the form to add a action (if there
    is no action yet).
    """

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        try:
            action = Action.objects.all()[0]
            return reverse("lfs_manage_action", kwargs={"pk": action.id})
        except IndexError:
            return reverse("lfs_manage_no_actions")


class ActionUpdateView(PermissionRequiredMixin, UpdateView):
    model = Action
    fields = ("active", "title", "link")
    template_name = "manage/actions/action.html"
    permission_required = "core.manage_shop"
    context_object_name = "action"

    def get_success_url(self):
        search_query = self.request.POST.get("q", "")
        url = reverse_lazy("lfs_manage_action", kwargs={"pk": self.object.id})
        if search_query:
            url = f"{url}?q={search_query}"
        return url

    def get_action_groups_queryset(self):
        """Liefert gefilterte ActionGroups mit Actions basierend auf Suchparameter."""
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            # Get all groups
            groups = ActionGroup.objects.all()

            # Filter actions based on title
            filtered_actions = Action.objects.filter(title__icontains=search_query)

            # Add filtered actions to each group
            for group in groups:
                group.filtered_actions = filtered_actions.filter(group=group).order_by("position")
        else:
            # All groups with all actions
            groups = ActionGroup.objects.all()
            for group in groups:
                group.filtered_actions = group.actions.all()

        return groups

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = self.get_action_groups_queryset()
        context["search_query"] = self.request.GET.get("q", "")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        _update_positions()

        messages.success(self.request, _("Action has been saved."))

        return response


class NoActionsView(PermissionRequiredMixin, TemplateView):
    """Displays a view when there are no actions."""

    template_name = "manage/actions/no_actions.html"
    permission_required = "core.manage_shop"


class ActionCreateView(PermissionRequiredMixin, CreateView):
    model = Action
    fields = ("active", "title", "link", "group")
    template_name = "manage/actions/add_action.html"
    permission_required = "core.manage_shop"

    def get_success_url(self):
        search_query = self.request.POST.get("q", "")
        url = reverse_lazy("lfs_manage_action", kwargs={"pk": self.object.id})
        if search_query:
            url = f"{url}?q={search_query}"
        return url

    def get_form_kwargs(self):
        # Add prefix to form fields to avoid conflicts with existing fields, as this view is used within a modal
        kwargs = super().get_form_kwargs()
        kwargs["prefix"] = "create"
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = ActionGroup.objects.all()
        context["came_from"] = self.request.POST.get("came_from", reverse("lfs_manage_actions"))
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        _update_positions()

        messages.success(self.request, _("Action has been added."))

        return response


class ActionDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of an action."""

    template_name = "manage/actions/delete_action.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = get_object_or_404(Action, pk=self.kwargs["pk"])
        return context


class ActionDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes the action with passed id."""

    model = Action
    permission_required = "core.manage_shop"
    success_message = _("Action has been deleted.")

    def get_success_url(self):
        """Return the URL to redirect to after successful deletion."""
        # Find next action to redirect to
        first_action = Action.objects.exclude(pk=self.object.pk).first()
        if first_action:
            return reverse("lfs_manage_action", kwargs={"pk": first_action.id})
        else:
            return reverse("lfs_manage_no_actions")


class SortActionsView(PermissionRequiredMixin, View):
    """Sorts actions after drag 'n drop."""

    permission_required = "core.manage_shop"
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        item_id = int(request.POST.get("item_id", ""))
        to_list = int(request.POST.get("to_list", ""))
        new_index = int(request.POST.get("new_index", ""))

        # action which has been dragged and dropped
        dnd_action = Action.objects.get(pk=item_id)

        # Update the group if it changed
        if dnd_action.group_id != to_list:
            dnd_action.group_id = to_list
            dnd_action.save()

        # Get all actions in the target group ordered by position
        actions_in_group = list(Action.objects.filter(group_id=to_list).exclude(pk=item_id).order_by("position"))

        if new_index < len(actions_in_group):
            new_position = actions_in_group[new_index].position
            for action in actions_in_group[new_index:]:
                action.position += 10
                action.save()
        else:
            new_position = (actions_in_group[-1].position + 10) if actions_in_group else 10

        # Set the new position for the sorted action
        dnd_action.position = new_position
        dnd_action.save()

        # Update all positions to ensure consistency
        _update_positions()

        return HttpResponse()


def _update_positions():
    """Updates the positions of all actions."""
    for group in ActionGroup.objects.all():
        for i, action in enumerate(group.actions.all()):
            action.position = (i + 1) * 10
            action.save()
