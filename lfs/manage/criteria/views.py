# django imports
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views import View

# lfs imports
from lfs.core.utils import import_symbol
from lfs.settings import lfs_setting


class AddCriterionView(PermissionRequiredMixin, View):
    """
    Adds a new criterion form.
    """

    permission_required = "core.manage_shop"

    def get(self, request: HttpRequest) -> HttpResponse:
        """Return the form of the first criterion in LFS_CRITERIA, for a new criterion row."""
        default_criterion = lfs_setting("LFS_CRITERIA")[0]
        default_criterion = import_symbol(default_criterion[0])
        result = default_criterion().render(request, 10)

        return HttpResponse(result)


class ChangeCriterionFormView(PermissionRequiredMixin, View):
    """
    Changes the changed criterion form to the given type (via request body)
    form.

    This is called via an AJAX request. The result is injected into the right
    DOM node.
    """

    permission_required = "core.manage_shop"

    def post(self, request):
        type = request.POST.get("type", "price")
        criterion = import_symbol(type)

        # create dummy criterion
        result = criterion(pk=1).render(request, 10)
        return HttpResponse(result)


class DeleteCriterionView(PermissionRequiredMixin, View):
    """
    Handles HTMX delete requests for criteria.
    Returns empty response to remove the criterion row from the UI.
    The actual criterion deletion is handled when the parent form is saved.
    """

    permission_required = "core.manage_shop"

    def delete(self, request):
        return HttpResponse("")


# Keep function aliases for backwards compatibility
add_criterion = AddCriterionView.as_view()
change_criterion_form = ChangeCriterionFormView.as_view()
delete_criterion = DeleteCriterionView.as_view()
