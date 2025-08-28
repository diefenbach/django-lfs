import json
from typing import Dict, List, Tuple, Any, Optional

# django imports
from django.contrib.auth.decorators import permission_required
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import UpdateView, FormView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django import forms

# lfs imports
import lfs.core.utils
from lfs.core.utils import LazyEncoder

from lfs.catalog.models import StaticBlock, File
from lfs.manage.static_blocks.forms import StaticBlockForm


class FileUploadForm(forms.Form):
    """Simple form for file uploads in FilesView."""

    pass  # No form fields needed - we handle file uploads directly in the view


class StaticBlockTabMixin:
    """Mixin für Tab-Navigation in StaticBlock Views."""

    template_name = "manage/static_block/static_block.html"
    tab_name: Optional[str] = None

    def get_static_block(self) -> StaticBlock:
        """Holt das StaticBlock-Objekt."""
        return get_object_or_404(StaticBlock, pk=self.kwargs["id"])

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Erweitert Kontext um Tab-Navigation und StaticBlock."""
        ctx = super().get_context_data(**kwargs)
        static_block = getattr(self, "object", None) or self.get_static_block()

        ctx.update(
            {
                "current_static_block": static_block,
                "static_blocks": StaticBlock.objects.all().order_by("name"),
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(static_block),
                "current_id": static_block.pk,
            }
        )
        return ctx

    def _get_tabs(self, static_block: StaticBlock) -> List[Tuple[str, str]]:
        """Erstellt Tab-Navigation URLs."""
        return [
            ("data", reverse("lfs_manage_static_block", args=[static_block.pk])),
            ("files", reverse("lfs_manage_static_block_files", args=[static_block.pk])),
        ]


# views
@permission_required("core.manage_shop")
def manage_static_blocks(request: HttpRequest) -> HttpResponseRedirect:
    """Dispatches to the first static block or to the add static block form."""
    try:
        sb = StaticBlock.objects.all().order_by("name")[0]
        url = reverse("lfs_manage_static_block", kwargs={"id": sb.id})
    except IndexError:
        url = reverse("lfs_manage_no_static_blocks")

    return HttpResponseRedirect(url)


class StaticBlockDataView(PermissionRequiredMixin, StaticBlockTabMixin, UpdateView):
    """View für Stammdaten-Tab eines StaticBlocks."""

    model = StaticBlock
    form_class = StaticBlockForm
    tab_name = "data"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Bleibt auf dem Data-Tab nach erfolgreichem Speichern."""
        return reverse("lfs_manage_static_block", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Speichert und zeigt Success-Message."""
        response = super().form_valid(form)
        return lfs.core.utils.set_message_cookie(
            url=self.get_success_url(),
            msg=_("Static block has been saved."),
        )

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Erweitert Kontext für Data-Tab."""
        ctx = super().get_context_data(**kwargs)
        return ctx


@permission_required("core.manage_shop")
def no_static_blocks(
    request: HttpRequest, template_name: str = "manage/static_block/no_static_blocks.html"
) -> HttpResponse:
    """Displays that no static blocks exist."""
    return render(request, template_name, {})


class StaticBlockFilesView(PermissionRequiredMixin, StaticBlockTabMixin, FormView):
    """View für Files-Tab eines StaticBlocks."""

    tab_name = "files"
    template_name = "manage/static_block/static_block.html"
    permission_required = "core.manage_shop"
    form_class = FileUploadForm

    def get_static_block(self) -> StaticBlock:
        """Überschreibt um id aus kwargs zu nutzen."""
        return get_object_or_404(StaticBlock, pk=self.kwargs["id"])

    def get_success_url(self) -> str:
        """Bleibt auf dem Files-Tab."""
        return reverse("lfs_manage_static_block_files", kwargs={"id": self.kwargs["id"]})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Behandelt File-Uploads und -Updates."""
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
        """Behandelt File-Upload."""
        for file_content in request.FILES.getlist("files[]"):
            file = File(content=static_block, title=file_content.name)
            file.file.save(file_content.name, file_content, save=True)

        refresh_file_positions(static_block)

        # Redirect to files tab instead of returning JSON
        return HttpResponseRedirect(self.get_success_url())

    def _handle_file_action(self, request: HttpRequest, static_block: StaticBlock, action: str) -> HttpResponse:
        """Behandelt File-Update/Delete Aktionen."""
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
        """Erweitert Kontext um Files."""
        ctx = super().get_context_data(**kwargs)
        static_block = self.get_static_block()
        ctx.update(
            {
                "static_block": static_block,
                "current_static_block": static_block,  # Alias für Template-Kompatibilität
            }
        )
        return ctx


@permission_required("core.manage_shop")
def add_static_block(
    request: HttpRequest, template_name: str = "manage/static_block/add_static_block.html"
) -> HttpResponse:
    """Provides a form to add a new static block."""
    if request.method == "POST":
        form = StaticBlockForm(data=request.POST)
        if form.is_valid():
            new_sb = form.save()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_static_block", kwargs={"id": new_sb.id}),
                msg=_("Static block has been added."),
            )
    else:
        form = StaticBlockForm()

    return render(
        request,
        template_name,
        {
            "form": form,
            "static_blocks": StaticBlock.objects.all(),
            "came_from": (request.POST if request.method == "POST" else request.GET).get(
                "came_from", reverse("lfs_manage_static_blocks")
            ),
        },
    )


@permission_required("core.manage_shop")
def preview_static_block(
    request: HttpRequest, id: str, template_name: str = "manage/static_block/preview.html"
) -> HttpResponse:
    """Displays a preview of an static block"""
    sb = get_object_or_404(StaticBlock, pk=id)

    return render(
        request,
        template_name,
        {
            "static_block": sb,
        },
    )


@permission_required("core.manage_shop")
@require_POST
def sort_static_blocks(request: HttpRequest) -> HttpResponse:
    """Sorts static blocks after drag 'n drop."""
    static_blocks = request.POST.get("objs", "").split("&")
    assert isinstance(static_blocks, list)
    if len(static_blocks) > 0:
        position = 10
        for sb_str in static_blocks:
            try:
                sb_id = sb_str.split("=")[1]
                sb_obj = StaticBlock.objects.get(pk=sb_id)
                sb_obj.position = position
                sb_obj.save()
                position = position + 10
            except (IndexError, StaticBlock.DoesNotExist):
                continue

        result = json.dumps(
            {
                "message": _("The static blocks have been sorted."),
            },
            cls=LazyEncoder,
        )

        return HttpResponse(result, content_type="application/json")


@permission_required("core.manage_shop")
@require_POST
def delete_static_block(request: HttpRequest, id: str) -> HttpResponse:
    """Deletes static block with passed id."""
    sb = get_object_or_404(StaticBlock, pk=id)
    sb.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_static_blocks"),
        msg=_("Static block has been deleted."),
    )


# Utility functions
def refresh_file_positions(static_block: StaticBlock) -> None:
    """Normalisiert File-Positionen eines StaticBlocks."""
    for i, file in enumerate(static_block.files.all()):
        file.position = (i + 1) * 10
        file.save()


def delete_files_by_keys(request: HttpRequest) -> None:
    """Löscht Files basierend auf delete-* Keys im POST-Request."""
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
    """Updated File-Titel und Positionen basierend auf POST-Keys."""
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
