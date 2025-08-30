from typing import Dict, List, Tuple, Any, Optional

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, FormView, CreateView, DeleteView, RedirectView, TemplateView

from lfs.catalog.models import StaticBlock, File
from lfs.manage.static_blocks.forms import FileUploadForm


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
                "static_block": static_block,
                "static_blocks": self.get_static_blocks_queryset(),
                "search_query": self.request.GET.get("q", ""),
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(static_block),
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
        # Handle file operations (upload/update/delete)
        if "files[]" in request.FILES:
            return self._handle_file_upload(request)
        elif "update" in request.POST:
            return self._handle_file_update(request)
        elif "delete" in request.POST:
            return self._handle_file_delete(request)

        return super().post(request, *args, **kwargs)

    def _handle_file_upload(self, request: HttpRequest) -> HttpResponse:
        """Handles file upload."""
        static_block = self.get_static_block()
        for file_content in request.FILES.getlist("files[]"):
            file = File(content=static_block, title=file_content.name)
            file.file.save(file_content.name, file_content, save=True)

        self._refresh_file_positions()

        messages.success(self.request, _("Files have been uploaded successfully."))
        return HttpResponseRedirect(self.get_success_url())

    def _handle_file_update(self, request: HttpRequest) -> HttpResponse:
        """Handles file update actions."""
        self._update_files_by_keys(request)
        messages.success(self.request, _("Files have been updated successfully."))
        return HttpResponseRedirect(self.get_success_url())

    def _handle_file_delete(self, request: HttpRequest) -> HttpResponse:
        """Handles file delete actions."""
        self._delete_files_by_keys(request)
        self._refresh_file_positions()
        messages.success(self.request, _("Files have been deleted successfully."))
        return HttpResponseRedirect(self.get_success_url())

    def _refresh_file_positions(self) -> None:
        """Normalizes file positions of a StaticBlock."""
        static_block = self.get_static_block()
        for i, file in enumerate(static_block.files.all()):
            file.position = (i + 1) * 10
            file.save()

    def _delete_files_by_keys(self, request: HttpRequest) -> None:
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

    def _update_files_by_keys(self, request: HttpRequest) -> None:
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

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with static block."""
        ctx = super().get_context_data(**kwargs)
        static_block = self.get_static_block()
        ctx.update(
            {
                "static_block": static_block,
            }
        )
        return ctx


class AddStaticBlockView(PermissionRequiredMixin, CreateView):
    """Provides a modal form to add a new static block."""

    model = StaticBlock
    fields = ["name"]
    template_name = "manage/static_block/add_static_block.html"
    permission_required = "core.manage_shop"

    def form_valid(self, form):
        static_block = form.save()

        response = HttpResponse()
        response["HX-Redirect"] = reverse("lfs_manage_static_block", kwargs={"id": static_block.id})

        messages.success(self.request, _("Static block has been created."))

        return response


class StaticBlockDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a static block."""

    template_name = "manage/static_block/delete_static_block.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["static_block"] = get_object_or_404(StaticBlock, pk=self.kwargs["id"])
        return context


class StaticBlockDeleteView(PermissionRequiredMixin, DeleteView):
    """Deletes static block with passed id."""

    model = StaticBlock
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get(self, request, *args, **kwargs):
        """Handle GET request - delete directly without confirmation."""
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request - delete static block and redirect with message."""
        self.object = self.get_object()
        self.object.delete()

        messages.success(request, _("Static block has been deleted."))

        response = HttpResponseRedirect(reverse("lfs_manage_static_blocks"))
        return response


class StaticBlockPreviewView(PermissionRequiredMixin, TemplateView):
    """Displays a preview of a static block"""

    permission_required = "core.manage_shop"
    template_name = "manage/static_block/preview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["static_block"] = get_object_or_404(StaticBlock, pk=self.kwargs["id"])
        return context
