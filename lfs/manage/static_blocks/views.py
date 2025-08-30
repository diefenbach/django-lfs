from typing import Dict, List, Tuple, Any, Optional

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, FormView, CreateView, DeleteView, RedirectView, TemplateView

import lfs.core.utils

from lfs.catalog.models import StaticBlock, File
from lfs.manage.static_blocks.forms import FileUploadForm


from django.views.generic.base import RedirectView


class ManageStaticBlocksView(PermissionRequiredMixin, RedirectView):
    """Dispatches to the first static block or to the add static block form."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        try:
            sb = StaticBlock.objects.all().order_by("name")[0]
            return reverse("lfs_manage_static_block", kwargs={"id": sb.id})
        except IndexError:
            return reverse("lfs_manage_no_static_blocks")


class NoStaticBlocksView(PermissionRequiredMixin, TemplateView):
    """Displays that no static blocks exist."""

    permission_required = "core.manage_shop"
    template_name = "manage/static_block/no_static_blocks.html"


class StaticBlockTabMixin:
    """Mixin for tab navigation in StaticBlock views."""

    template_name = "manage/static_block/static_block.html"
    tab_name: Optional[str] = None

    def get_static_block(self) -> StaticBlock:
        """Gets the StaticBlock object."""
        return get_object_or_404(StaticBlock, pk=self.kwargs["id"])

    def get_static_blocks_queryset(self):
        """Returns filtered StaticBlocks based on search parameter."""
        queryset = StaticBlock.objects.all().order_by("name")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with tab navigation and StaticBlock."""
        ctx = super().get_context_data(**kwargs)
        static_block = getattr(self, "object", None) or self.get_static_block()

        ctx.update(
            {
                "current_static_block": static_block,
                "static_blocks": self.get_static_blocks_queryset(),
                "search_query": self.request.GET.get("q", ""),
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(static_block),
                "current_id": static_block.pk,
            }
        )
        return ctx

    def _get_tabs(self, static_block: StaticBlock) -> List[Tuple[str, str]]:
        """Creates tab navigation URLs with search parameter."""
        search_query = self.request.GET.get("q", "").strip()

        data_url = reverse("lfs_manage_static_block", args=[static_block.pk])
        files_url = reverse("lfs_manage_static_block_files", args=[static_block.pk])

        # Add search parameter if present
        if search_query:
            from urllib.parse import urlencode

            query_params = urlencode({"q": search_query})
            data_url += "?" + query_params
            files_url += "?" + query_params

        return [
            ("data", data_url),
            ("files", files_url),
        ]


class StaticBlockDataView(PermissionRequiredMixin, StaticBlockTabMixin, UpdateView):
    """View for data tab of a StaticBlock."""

    model = StaticBlock
    fields = ["name", "html"]
    tab_name = "data"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the data tab after successful save."""
        return reverse("lfs_manage_static_block", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        response = super().form_valid(form)
        messages.success(self.request, _("Static block has been saved."))
        return response

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context for data tab."""
        ctx = super().get_context_data(**kwargs)
        return ctx


class StaticBlockFilesView(PermissionRequiredMixin, StaticBlockTabMixin, FormView):
    """View for files tab of a StaticBlock."""

    tab_name = "files"
    template_name = "manage/static_block/static_block.html"
    permission_required = "core.manage_shop"
    form_class = FileUploadForm

    def get_static_block(self) -> StaticBlock:
        """Overrides to use id from kwargs."""
        return get_object_or_404(StaticBlock, pk=self.kwargs["id"])

    def get_success_url(self) -> str:
        """Stays on the files tab."""
        return reverse("lfs_manage_static_block_files", kwargs={"id": self.kwargs["id"]})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles file uploads and updates."""
        static_block = self.get_static_block()

        # Handle file uploads
        if "files[]" in request.FILES:
            return self._handle_file_upload(request, static_block)

        # Handle file operations (update/delete)
        if "update" in request.POST:
            return self._handle_file_action(request, static_block, "update")
        elif "delete" in request.POST:
            return self._handle_file_action(request, static_block, "delete")

        return super().post(request, *args, **kwargs)

    def _handle_file_upload(self, request: HttpRequest, static_block: StaticBlock) -> HttpResponse:
        """Handles file upload."""
        for file_content in request.FILES.getlist("files[]"):
            file = File(content=static_block, title=file_content.name)
            file.file.save(file_content.name, file_content, save=True)

        refresh_file_positions(static_block)

        messages.success(self.request, _("Files have been uploaded successfully."))
        return HttpResponseRedirect(self.get_success_url())

    def _handle_file_action(self, request: HttpRequest, static_block: StaticBlock, action: str) -> HttpResponse:
        """Handles file update/delete actions."""
        if action == "delete":
            delete_files_by_keys(request)
            # Only refresh positions after delete (to fill gaps)
            refresh_file_positions(static_block)
        elif action == "update":
            update_files_by_keys(request)
            # Don't refresh positions after update - user set them manually

        # Redirect to files tab instead of returning JSON
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with files."""
        ctx = super().get_context_data(**kwargs)
        static_block = self.get_static_block()
        ctx.update(
            {
                "static_block": static_block,
                "current_static_block": static_block,  # Alias for template compatibility
            }
        )
        return ctx


class AddStaticBlockView(CreateView):
    """Provides a modal form to add a new static block."""

    model = StaticBlock
    fields = ["name"]
    template_name = "manage/static_block/add_static_block.html"

    @method_decorator(permission_required("core.manage_shop"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        static_block = form.save()
        response = HttpResponse()
        response["HX-Redirect"] = reverse("lfs_manage_static_block", kwargs={"id": static_block.id})
        return response

    def get_success_url(self):
        """Return the URL to redirect to after successful form submission."""
        return reverse("lfs_manage_static_block", kwargs={"id": self.object.id})


class StaticBlockDeleteView(PermissionRequiredMixin, DeleteView):
    """Deletes static block with passed id."""

    model = StaticBlock
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Returns URL to redirect after successful deletion."""
        return reverse("lfs_manage_static_blocks")

    def delete(self, request, *args, **kwargs):
        """Override to add success message after deletion."""
        response = super().delete(request, *args, **kwargs)
        return lfs.core.utils.set_message_cookie(
            url=self.get_success_url(),
            msg=_("Static block has been deleted."),
        )


class StaticBlockPreviewView(PermissionRequiredMixin, TemplateView):
    """Displays a preview of a static block"""

    permission_required = "core.manage_shop"
    template_name = "manage/static_block/preview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["static_block"] = get_object_or_404(StaticBlock, pk=self.kwargs["id"])
        return context


def refresh_file_positions(static_block: StaticBlock) -> None:
    """Normalizes file positions of a StaticBlock."""
    for i, file in enumerate(static_block.files.all()):
        file.position = (i + 1) * 10
        file.save()


def delete_files_by_keys(request: HttpRequest) -> None:
    """Deletes files based on delete-* keys in POST request."""
    for key in request.POST.keys():
        if key.startswith("delete-"):
            try:
                file_id = key.split("-")[1]
                # Skip invalid IDs gracefully
                if not file_id.isdigit():
                    continue
                File.objects.get(pk=file_id).delete()
            except (IndexError, File.DoesNotExist, ValueError):
                pass


def update_files_by_keys(request: HttpRequest) -> None:
    """Updates file titles and positions based on POST keys."""
    for key, value in request.POST.items():
        if key.startswith("title-"):
            file_id = key.split("-")[1]
            try:
                # Skip invalid IDs gracefully
                if not file_id.isdigit():
                    continue
                file = File.objects.get(pk=file_id)
                file.title = value
                file.save()
            except (File.DoesNotExist, ValueError):
                pass
        elif key.startswith("position-"):
            try:
                file_id = key.split("-")[1]
                # Skip invalid IDs gracefully
                if not file_id.isdigit():
                    continue
                file = File.objects.get(pk=file_id)
                file.position = value
                file.save()
            except (IndexError, File.DoesNotExist, ValueError):
                pass
