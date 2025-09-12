import json

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import RedirectView, TemplateView, View

from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category, Product
from lfs.catalog.settings import VARIANT
from lfs.core.signals import topseller_changed
from lfs.marketing.models import Topseller


class ManageTopsellerView(PermissionRequiredMixin, TemplateView):
    """Main view for managing topseller products with two-column layout."""

    template_name = "manage/topseller/topseller.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get topseller products
        topseller = Topseller.objects.all().order_by("position")
        topseller_ids = [t.product.id for t in topseller]

        # Get filter parameters
        r = self.request.POST if self.request.method == "POST" else self.request.GET
        s = self.request.session

        # Handle filters and pagination
        if r.get("keep-filters") or r.get("page"):
            page = r.get("page", s.get("topseller_products_page", 1))
            filter_ = r.get("filter", s.get("filter"))
            category_filter = r.get("topseller_category_filter", s.get("topseller_category_filter"))
        else:
            page = r.get("page", 1)
            filter_ = r.get("filter")
            category_filter = r.get("topseller_category_filter")

        # Save current filters in session
        s["topseller_products_page"] = page
        s["filter"] = filter_
        s["topseller_category_filter"] = category_filter

        try:
            s["topseller-amount"] = int(r.get("topseller-amount", s.get("topseller-amount")))
        except TypeError:
            s["topseller-amount"] = 25

        # Build filters
        filters = Q()
        if filter_:
            filters &= Q(name__icontains=filter_)
            filters |= Q(sku__icontains=filter_)
            filters |= Q(sub_type=VARIANT) & Q(active_sku=False) & Q(parent__sku__icontains=filter_)
            filters |= Q(sub_type=VARIANT) & Q(active_name=False) & Q(parent__name__icontains=filter_)

        if category_filter:
            if category_filter == "None":
                filters &= Q(categories=None)
            elif category_filter == "All":
                pass
            else:
                category = lfs_get_object_or_404(Category, pk=category_filter)
                categories = [category]
                categories.extend(category.get_all_children())
                filters &= Q(categories__in=categories)

        # Get products (excluding already topseller ones)
        products = Product.objects.filter(filters).exclude(pk__in=topseller_ids)
        paginator = Paginator(products, s["topseller-amount"])

        total = products.count()
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            # If the page is out of range, return 0
            page_obj = 0

        # Amount options for pagination
        amount_options = []
        for value in (10, 25, 50, 100):
            amount_options.append({"value": value, "selected": value == s.get("topseller-amount")})

        # Get all categories for filter dropdown in hierarchical structure
        categories = self._build_hierarchical_categories()

        context.update(
            {
                "topseller": topseller,
                "total": total,
                "page": page_obj,
                "paginator": paginator,
                "filter": filter_ or "",
                "category_filter": category_filter,
                "amount_options": amount_options,
                "categories": categories,
            }
        )

        return context

    def _build_hierarchical_categories(self):
        """Build a hierarchical list of categories with proper indentation."""
        categories = []

        def _add_category_with_children(category, level=0):
            """Recursively add category and its children with proper indentation."""
            # Create a simple object that mimics the Category model but with indented name
            indent = "&nbsp;" * 5 * level
            category_with_indent = type(
                "CategoryWithIndent",
                (),
                {"id": category.id, "name": f"{indent}{category.name}", "level": level, "category": category},
            )()
            categories.append(category_with_indent)

            # Add children recursively
            children = category.get_children().order_by("name")
            for child in children:
                _add_category_with_children(child, level + 1)

        # Start with top-level categories (no parent)
        top_level_categories = Category.objects.filter(parent=None).order_by("name")
        for category in top_level_categories:
            _add_category_with_children(category)

        return categories


class AddTopsellerView(PermissionRequiredMixin, RedirectView):
    """Adds topseller products by given ids (within request body)."""

    permission_required = "core.manage_shop"

    def post(self, request, *args, **kwargs):
        """Handle POST request to add topseller products."""
        for temp_id in request.POST.keys():
            if temp_id.startswith("product") is False:
                continue

            temp_id = temp_id.split("-")[1]
            Topseller.objects.create(product_id=temp_id)

        _update_positions()

        return redirect("lfs_manage_topseller")


class RemoveTopsellerView(PermissionRequiredMixin, RedirectView):
    """Removes passed topseller product passed id (within request body)."""

    permission_required = "core.manage_shop"

    def post(self, request, *args, **kwargs):
        """Handle POST request to remove topseller products."""
        if request.POST.get("action") == "remove":
            for temp_id in request.POST.keys():
                if not temp_id.startswith("product"):
                    continue

                temp_id = temp_id.split("-")[1]
                try:
                    topseller = Topseller.objects.get(pk=temp_id)
                    topseller_changed.send(topseller)
                    topseller.delete()
                except (Topseller.DoesNotExist, ValueError):
                    pass

            _update_positions()

        return redirect("lfs_manage_topseller")


class SortTopsellerView(PermissionRequiredMixin, View):
    """Handle drag and drop sorting of topseller products."""

    permission_required = "core.manage_shop"

    def post(self, request, *args, **kwargs):
        """Handle POST request for drag and drop sorting."""
        data = json.loads(request.body)
        topseller_ids = data.get("topseller_ids", [])

        for index, topseller_id in enumerate(topseller_ids):
            try:
                topseller = Topseller.objects.get(pk=topseller_id)
                topseller.position = (index + 1) * 10
                topseller.save()
            except Topseller.DoesNotExist:
                continue

        return HttpResponse()


def _update_positions():
    """Update positions of topseller products."""
    for i, topseller in enumerate(Topseller.objects.all()):
        topseller.position = (i + 1) * 10
        topseller.save()
