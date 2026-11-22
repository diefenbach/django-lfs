from typing import Dict, List, Tuple, Any, Optional
import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, ngettext
from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from lfs.catalog.models import Image
from lfs.core.utils import lfs_pagination

logger = logging.getLogger(__name__)


class ImagesTabMixin:
    """Mixin for tab navigation in Images views."""

    template_name = "manage/images/images.html"
    tab_name: Optional[str] = None

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add tab navigation context."""
        ctx = super().get_context_data(**kwargs)

        ctx.update(
            {
                "tabs": self._get_tabs(),
                "active_tab": self.tab_name or "list",
                "search_query": self.request.GET.get("q", ""),
            }
        )

        return ctx

    def _get_tabs(self) -> List[Tuple[str, str]]:
        """Creates tab navigation URLs with search parameter."""
        search_query = self.request.GET.get("q", "").strip()

        # Add search parameter if present
        if search_query:
            from urllib.parse import urlencode

            query_params = urlencode({"q": search_query})
        else:
            query_params = ""

        tabs = [
            ("list", reverse("lfs_manage_images_list") + (f"?{query_params}" if query_params else "")),
            ("upload", reverse("lfs_manage_images_upload") + (f"?{query_params}" if query_params else "")),
        ]

        return tabs


class ImagesListView(PermissionRequiredMixin, ImagesTabMixin, TemplateView):
    """Display images management with pagination and filtering."""

    permission_required = "core.manage_shop"
    template_name = "manage/images/images.html"
    tab_name = "list"
    paginate_by = 50

    def get_queryset(self):
        """Get filtered queryset based on search query."""
        query = self.request.GET.get("q", "")
        if query:
            return Image.objects.filter(content_id=None, title__istartswith=query).order_by("-id")
        return Image.objects.filter(content_id=None).order_by("-id")

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add pagination and images to context."""
        context = super().get_context_data(**kwargs)

        # Get pagination parameters (use standard Django 'page' parameter)
        try:
            page_num = int(self.request.GET.get("page", 1))
        except (ValueError, TypeError):
            page_num = 1

        query = self.request.GET.get("q", "")
        images_qs = self.get_queryset()

        # Setup pagination
        paginator = Paginator(images_qs, self.paginate_by)
        try:
            current_page = paginator.page(page_num)
        except (EmptyPage, InvalidPage):
            current_page = paginator.page(paginator.num_pages)

        # Calculate pagination data
        pagination_data = lfs_pagination(self.request, current_page, url=self.request.path)
        pagination_data["total_text"] = ngettext("%(count)d image", "%(count)d images", images_qs.count()) % {
            "count": images_qs.count()
        }
        pagination_data["has_other_pages"] = current_page.has_other_pages()

        context.update(
            {
                "images": current_page.object_list,
                "pagination": current_page,  # Pass the page object for the pagination snippet
                "pagination_data": pagination_data,  # Keep the old pagination data for backward compatibility
                "query": query,
            }
        )

        return context

    def render_to_response(self, context, **response_kwargs):
        """Handle both regular requests and HTMX search requests."""
        # Check if this is an HTMX request (for search functionality)
        if self.request.headers.get("HX-Request"):
            # Return just the files-list div content for HTMX
            html = render_to_string("manage/images/tabs/_list.html", context, request=self.request)
            # Extract just the files-list div content
            from django.utils.html import strip_tags
            import re

            match = re.search(r'<div id="files-list".*?</div>(?=\s*</div>)', html, re.DOTALL)
            if match:
                return HttpResponse(match.group(0))
            else:
                # Fallback: return the entire _list.html content
                return HttpResponse(html)
        else:
            # Regular request: return full page
            return super().render_to_response(context, **response_kwargs)


class ImagePreviewView(PermissionRequiredMixin, View):
    """HTMX view for image preview modal."""

    permission_required = "core.manage_shop"
    http_method_names = ["get"]

    def get(self, request: HttpRequest, image_id: int) -> HttpResponse:
        """Return image preview modal content."""
        try:
            image = Image.objects.get(pk=image_id, content_id=None)
        except Image.DoesNotExist:
            context = {
                "error": _("Image not found"),
            }
        else:
            context = {
                "image": image,
            }

        # Update modal title
        modal_title = _("Image Preview") if "image" in context else _("Error")

        html = render_to_string("manage/images/image_preview_modal.html", context, request=request)

        # Return both modal content and title update
        return HttpResponse(f'<div id="modal-title-lg" hx-swap-oob="true">{modal_title}</div>' + html)


class DeleteImagesConfirmView(PermissionRequiredMixin, View):
    """Show delete confirmation modal for selected images."""

    permission_required = "core.manage_shop"
    http_method_names = ["get"]

    def get(self, request: HttpRequest) -> HttpResponse:
        """Return delete confirmation modal content."""
        selected_image_ids = request.GET.getlist("images")
        selected_count = len(selected_image_ids)

        context = {
            "selected_image_ids": selected_image_ids,
            "selected_count": selected_count,
        }

        html = render_to_string("manage/images/delete_images_confirm.html", context, request=request)
        return HttpResponse(html)


class DeleteImagesView(PermissionRequiredMixin, View):
    """Delete selected images."""

    permission_required = "core.manage_shop"
    http_method_names = ["post"]

    def post(self, request: HttpRequest) -> HttpResponseRedirect:
        """Delete images specified in POST data."""
        image_ids = request.POST.getlist("images")
        deleted_count = len(image_ids)

        if deleted_count > 0:
            Image.objects.filter(pk__in=image_ids).delete()

            # Add success message
            message = ngettext(
                "%(count)d image has been successfully deleted.",
                "%(count)d images have been successfully deleted.",
                deleted_count,
            ) % {"count": deleted_count}

            messages.success(request, message)
        else:
            messages.warning(request, _("No images were selected for deletion."))

        return HttpResponseRedirect(reverse("lfs_manage_images_list"))


class AddImagesView(PermissionRequiredMixin, View):
    """Handle image uploads via AJAX."""

    permission_required = "core.manage_shop"
    http_method_names = ["post"]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request: HttpRequest) -> JsonResponse:
        """Process uploaded image files."""
        results = []

        for file_content in request.FILES.getlist("files[]"):
            image = Image(title=file_content.name)
            try:
                image.image.save(file_content.name, file_content, save=True)
                results.append(
                    {"name": file_content.name, "type": "image/jpeg", "size": file_content.size, "success": True}
                )
            except Exception as e:
                image.delete()
                logger.info("Upload of image failed: %s %s", file_content.name, e)
                results.append({"name": file_content.name, "error": str(e), "success": False})

        return JsonResponse({"results": results})


class ImagesUploadView(PermissionRequiredMixin, ImagesTabMixin, TemplateView):
    """Display images upload interface."""

    permission_required = "core.manage_shop"
    template_name = "manage/images/images.html"
    tab_name = "upload"
