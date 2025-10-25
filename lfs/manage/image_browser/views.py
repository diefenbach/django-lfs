from django.http import JsonResponse
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q
from typing import List, Dict

from lfs.catalog.models import Image
from lfs.catalog.settings import THUMBNAIL_SIZES


class TinyMCEImageBrowserView(PermissionRequiredMixin, TemplateView):
    """HTMX endpoint for TinyMCE custom image browser."""

    permission_required = "core.manage_shop"
    template_name = "manage/image_browser/image_grid.html"

    def get_context_data(self, **kwargs):
        """Return images for HTMX rendering."""
        context = super().get_context_data(**kwargs)

        # Get search query
        query = self.request.GET.get("q", "")

        # Get pagination parameters
        try:
            page = int(self.request.GET.get("page", 1))
        except (ValueError, TypeError):
            page = 1

        # Get images (only those not associated with content)
        images_qs = Image.objects.filter(content_id=None)

        if query:
            images_qs = images_qs.filter(Q(title__icontains=query) | Q(alt__icontains=query))

        # Paginate results
        paginator = Paginator(images_qs, 20)  # 20 images per page

        try:
            current_page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            current_page = paginator.page(paginator.num_pages)

        # Format images for template
        images = []
        for image in current_page.object_list:
            images.append(
                {
                    "id": image.id,
                    "url": image.image.url,
                    "title": image.title or image.alt or f"Image {image.id}",
                    "alt": image.alt or "",
                    "thumb": image.image.url_100x100 if hasattr(image.image, "url_100x100") else image.image.url,
                    "sizes": self._get_available_sizes(image),
                }
            )

        context.update(
            {
                "images": images,
                "pagination": {
                    "current_page": current_page.number,
                    "total_pages": paginator.num_pages,
                    "has_next": current_page.has_next(),
                    "has_previous": current_page.has_previous(),
                    "total_count": paginator.count,
                    "page_range": current_page.paginator.page_range,
                },
                "query": query,
            }
        )

        return context

    def _get_available_sizes(self, image) -> List[Dict[str, str]]:
        """Get available sizes for an image."""
        sizes = [{"value": "", "label": "Original"}]

        for size in THUMBNAIL_SIZES:
            size_str = f"{size[0]}x{size[1]}"
            try:
                # Check if this size exists for the image
                size_url = getattr(image.image, f"url_{size_str}", None)
                if size_url:
                    sizes.append({"value": size_str, "label": size_str})
            except AttributeError:
                continue

        return sizes


class TinyMCEImageBrowserAPIView(PermissionRequiredMixin, View):
    """Legacy API endpoint for backward compatibility."""

    permission_required = "core.manage_shop"

    def get(self, request):
        """Return images in format expected by TinyMCE (JSON)."""
        # Get search query
        query = request.GET.get("q", "")

        # Get pagination parameters
        try:
            page = int(request.GET.get("page", 1))
        except (ValueError, TypeError):
            page = 1

        # Get images (only those not associated with content)
        images_qs = Image.objects.filter(content_id=None)

        if query:
            images_qs = images_qs.filter(Q(title__icontains=query) | Q(alt__icontains=query))

        # Paginate results
        paginator = Paginator(images_qs, 20)  # 20 images per page

        try:
            current_page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            current_page = paginator.page(paginator.num_pages)

        # Format images for TinyMCE
        images = []
        for image in current_page.object_list:
            images.append(
                {
                    "value": image.image.url,
                    "text": image.title or image.alt or f"Image {image.id}",
                    "title": image.title or "",
                    "alt": image.alt or "",
                    "thumb": image.image.url_100x100 if hasattr(image.image, "url_100x100") else image.image.url,
                    "sizes": self._get_available_sizes(image),
                }
            )

        return JsonResponse(
            {
                "images": images,
                "pagination": {
                    "current_page": current_page.number,
                    "total_pages": paginator.num_pages,
                    "has_next": current_page.has_next(),
                    "has_previous": current_page.has_previous(),
                    "total_count": paginator.count,
                },
            }
        )

    def _get_available_sizes(self, image) -> List[Dict[str, str]]:
        """Get available sizes for an image."""
        sizes = [{"value": "", "label": "Original"}]

        for size in THUMBNAIL_SIZES:
            size_str = f"{size[0]}x{size[1]}"
            try:
                # Check if this size exists for the image
                size_url = getattr(image.image, f"url_{size_str}", None)
                if size_url:
                    sizes.append({"value": size_str, "label": size_str})
            except AttributeError:
                continue

        return sizes


class TinyMCEImageBrowserModalView(PermissionRequiredMixin, View):
    """Modal view for TinyMCE image browser."""

    permission_required = "core.manage_shop"
    template_name = "manage/image_browser/image_browser_modal.html"

    def get(self, request):
        """Display the image browser modal."""
        from django.shortcuts import render

        return render(request, self.template_name)
