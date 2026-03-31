from typing import Dict, List, Tuple, Any, Optional

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, CreateView, DeleteView, RedirectView, TemplateView

from lfs.caching.utils import lfs_get_object_or_404
from lfs.manage.mixins import DirectDeleteMixin
from lfs.manage.categories.forms import CategoryAddForm, CategoryForm, CategoryViewForm
from lfs.manage.portlets.views import PortletsInlineView
from lfs.catalog.models import Category, Product
from lfs.manufacturer.models import Manufacturer
from lfs.core.utils import LazyEncoder, set_category_levels
from django.template.loader import render_to_string
import json


class ManageCategoriesView(PermissionRequiredMixin, RedirectView):
    """Dispatches to the first category or to the add category form."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        try:
            category = Category.objects.all()[0]
            return reverse("lfs_manage_category", kwargs={"id": category.id})
        except IndexError:
            return reverse("lfs_manage_no_categories")


class CategoryTabMixin:
    """Mixin for tab navigation in Category views."""

    template_name = "manage/categories/category.html"
    tab_name: Optional[str] = None

    def get_category(self) -> Category:
        """Gets the Category object."""
        return get_object_or_404(Category, pk=self.kwargs["id"])

    def get_categories_queryset(self):
        """Returns filtered Categories based on search parameter."""
        queryset = Category.objects.all().order_by("name")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with tab navigation and Category."""
        ctx = super().get_context_data(**kwargs)
        category = getattr(self, "object", None) or self.get_category()

        ctx.update(
            {
                "category": category,
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(category),
                **self._get_navigation_context(category),
            }
        )
        return ctx

    def _get_tabs(self, category: Category) -> List[Tuple[str, str]]:
        """Creates tab navigation URLs with search parameter."""
        search_query = self.request.GET.get("q", "").strip()

        # Add search parameter if present
        if search_query:
            from urllib.parse import urlencode

            query_params = urlencode({"q": search_query})
        else:
            query_params = ""

        tabs = [
            ("data", reverse("lfs_manage_category", args=[category.pk]) + (f"?{query_params}" if query_params else "")),
            (
                "view",
                reverse("lfs_manage_category_view", args=[category.pk]) + (f"?{query_params}" if query_params else ""),
            ),
            (
                "products",
                reverse("lfs_manage_category_products", args=[category.pk])
                + (f"?{query_params}" if query_params else ""),
            ),
            (
                "seo",
                reverse("lfs_manage_category_seo", args=[category.pk]) + (f"?{query_params}" if query_params else ""),
            ),
            (
                "portlets",
                reverse("lfs_manage_category_portlets", args=[category.pk])
                + (f"?{query_params}" if query_params else ""),
            ),
        ]

        return tabs

    def _get_navigation_context(self, category: Category) -> Dict[str, Any]:
        """Returns navigation context data."""
        return {
            "category": category,
            "categories": self.get_categories_queryset(),
            "hierarchical_categories": self._build_hierarchical_categories(),
            "search_query": self.request.GET.get("q", ""),
        }

    def _build_hierarchical_categories(self):
        """Build a hierarchical list of categories for sortable sidebar."""
        search_query = self.request.GET.get("q", "").strip()

        # Get filtered categories based on search query
        filtered_categories = self.get_categories_queryset()

        # If no search query, show all categories in hierarchy
        if not search_query:

            def _add_category_with_children(category, level=0):
                """Recursively add category and its children with hierarchical structure."""
                # Create a category object with hierarchical data
                category_data = type(
                    "CategoryHierarchy",
                    (),
                    {"id": category.id, "name": category.name, "level": level, "category": category, "children": []},
                )()

                # Add children recursively - use direct database query instead of get_children()
                children = Category.objects.filter(parent=category).order_by("position", "name")
                for child in children:
                    child_data = _add_category_with_children(child, level + 1)
                    category_data.children.append(child_data)

                return category_data

            # Start with top-level categories (no parent)
            top_level_categories = Category.objects.filter(parent=None).order_by("position", "name")
            # Build hierarchical structure starting from top-level categories
            result = []
            for category in top_level_categories:
                result.append(_add_category_with_children(category))
        else:
            # For search results, show only matching categories in a flat structure
            # but maintain parent-child relationships where both match
            result = []
            for category in filtered_categories:
                # Create a category object with hierarchical data
                category_data = type(
                    "CategoryHierarchy",
                    (),
                    {
                        "id": category.id,
                        "name": category.name,
                        "level": category.level,
                        "category": category,
                        "children": [],
                    },
                )()
                result.append(category_data)

        return result


class CategoryDataView(PermissionRequiredMixin, CategoryTabMixin, UpdateView):
    """View for data tab of a Category."""

    model = Category
    form_class = CategoryForm
    tab_name = "data"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the data tab after successful save."""
        return reverse("lfs_manage_category", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        # Handle image deletion if checkbox is checked
        if self.request.POST.get("delete_image"):
            category = self.get_object()
            if category.image:
                category.image.delete()
                category.image = None
                category.save()

        response = super().form_valid(form)
        messages.success(self.request, _("Category data has been saved."))
        return response


class CategoryViewView(PermissionRequiredMixin, CategoryTabMixin, UpdateView):
    """View for view tab of a Category."""

    model = Category
    form_class = CategoryViewForm
    tab_name = "view"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the view tab after successful save."""
        return reverse("lfs_manage_category_view", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        response = super().form_valid(form)
        messages.success(self.request, _("View data has been saved."))
        return response


class CategoryProductsView(PermissionRequiredMixin, CategoryTabMixin, TemplateView):
    """View for products tab of a Category."""

    tab_name = "products"
    template_name = "manage/categories/category.html"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the products tab."""
        return reverse("lfs_manage_category_products", kwargs={"id": self.kwargs["id"]})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles product operations (assign/remove)."""
        if "assign_products" in request.POST:
            return self._handle_assign_products(request)
        elif "remove_products" in request.POST:
            return self._handle_remove_products(request)

        return super().post(request, *args, **kwargs)

    def _handle_assign_products(self, request: HttpRequest) -> HttpResponse:
        """Handles assigning products to category."""
        category = self.get_category()

        for temp_id in request.POST.keys():
            if temp_id.startswith("product"):
                temp_id = temp_id.split("-")[1]
                product = Product.objects.get(pk=temp_id)
                category.products.add(product)

        messages.success(self.request, _("Products have been assigned."))
        return HttpResponseRedirect(self.get_success_url())

    def _handle_remove_products(self, request: HttpRequest) -> HttpResponse:
        """Handles removing products from category."""
        category = self.get_category()

        for temp_id in request.POST.keys():
            if temp_id.startswith("product"):
                temp_id = temp_id.split("-")[1]
                product = Product.objects.get(pk=temp_id)
                category.products.remove(product)

        messages.success(self.request, _("Products have been removed."))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with products and filters."""
        ctx = super().get_context_data(**kwargs)
        category = self.get_category()

        # Get assigned products
        category_products = category.products.all().select_related("parent")

        # Handle filters
        r = self.request.POST if self.request.method == "POST" else self.request.GET
        s = self.request.session

        if r.get("keep-filters") or r.get("page"):
            page = r.get("page", s.get("category_page", 1))
            filter_ = r.get("filter", s.get("filter"))
            category_filter = r.get("products_category_filter", s.get("products_category_filter"))
            manufacturer_filter = r.get("products_manufacturer_filter", s.get("products_manufacturer_filter"))
        else:
            page = r.get("page", 1)
            filter_ = r.get("filter")
            category_filter = r.get("products_category_filter")
            manufacturer_filter = r.get("products_manufacturer_filter")

        # Save filters in session (convert None to empty string for display)
        s["category_page"] = page
        s["filter"] = filter_ or ""
        s["products_category_filter"] = category_filter or ""
        s["products_manufacturer_filter"] = manufacturer_filter or ""

        # Apply filters
        filters = Q()
        if filter_:
            filters &= Q(name__icontains=filter_)

        if category_filter:
            if category_filter == "None":
                filters &= Q(categories=None)
            elif category_filter == "All":
                pass
            else:
                filter_category = lfs_get_object_or_404(Category, pk=category_filter)
                categories = [filter_category]
                categories.extend(filter_category.get_all_children())
                filters &= Q(categories__in=categories)

        if manufacturer_filter:
            if manufacturer_filter == "None":
                filters &= Q(manufacturer=None)
            elif manufacturer_filter == "All":
                pass
            else:
                manufacturer = lfs_get_object_or_404(Manufacturer, pk=manufacturer_filter)
                filters &= Q(manufacturer=manufacturer)

        # Get available products (excluding already assigned)
        products = Product.objects.select_related("parent").filter(filters)
        paginator = Paginator(products.exclude(pk__in=category_products), 25)

        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = 0

        # Get all categories for filter dropdown in hierarchical structure
        categories = self._build_hierarchical_categories()

        # Get all manufacturers for filter dropdown
        manufacturers = Manufacturer.objects.all().order_by("name")

        ctx.update(
            {
                "category_products": category_products,
                "page": page_obj,
                "paginator": paginator,
                "filter": filter_ or "",
                "category_filter": category_filter or "",
                "manufacturer_filter": manufacturer_filter or "",
                "categories": categories,
                "manufacturers": manufacturers,
            }
        )
        return ctx


class CategorySEOView(PermissionRequiredMixin, CategoryTabMixin, UpdateView):
    """View for SEO tab of a Category."""

    model = Category
    fields = ["meta_title", "meta_description", "meta_keywords"]
    tab_name = "seo"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the SEO tab after successful save."""
        return reverse("lfs_manage_category_seo", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        response = super().form_valid(form)
        messages.success(self.request, _("SEO data has been saved."))
        return response


class CategoryPortletsView(PermissionRequiredMixin, CategoryTabMixin, TemplateView):
    """View for portlets tab of a Category."""

    tab_name = "portlets"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with portlets."""
        ctx = super().get_context_data(**kwargs)
        category = self.get_category()
        ctx["portlets"] = PortletsInlineView().get(self.request, category)
        return ctx


class CategoryCreateView(SuccessMessageMixin, PermissionRequiredMixin, CreateView):
    """Provides a form to add a new category."""

    model = Category
    form_class = CategoryAddForm
    template_name = "manage/categories/add_category.html"
    permission_required = "core.manage_shop"
    success_message = _("Category has been created.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parent_id"] = self.kwargs.get("parent_id")
        try:
            parent_category = Category.objects.get(pk=self.kwargs.get("parent_id"))
        except Category.DoesNotExist:
            context["parent_name"] = ""
        else:
            context["parent_name"] = parent_category.name
        return context

    def get_success_url(self):
        return reverse("lfs_manage_category", kwargs={"id": self.object.id})

    def form_valid(self, form):
        """Saves the category with proper parent and position."""
        category = form.save(commit=False)

        # Set parent if provided
        parent_id = self.kwargs.get("parent_id")
        if parent_id:
            parent = get_object_or_404(Category, pk=parent_id)
            category.parent = parent
            category.level = parent.level + 1
        else:
            category.parent = None
            category.level = 0

        category.position = 999
        category.save()

        # Update positions
        from lfs.manage import utils as manage_utils

        manage_utils.update_category_positions(category.parent)

        return super().form_valid(form)


class CategoryDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a category."""

    template_name = "manage/categories/delete_category.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(Category, pk=self.kwargs["id"])
        return context


class CategoryDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes category with passed id."""

    model = Category
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"
    success_message = _("Category has been deleted.")

    def get_success_url(self):
        return reverse("lfs_manage_categories")

    def delete(self, request, *args, **kwargs):
        """Delete category and update positions."""
        category = self.get_object()
        parent = category.parent
        response = super().delete(request, *args, **kwargs)

        # Update positions
        from lfs.manage import utils as manage_utils

        manage_utils.update_category_positions(parent)

        return response


class CategoryViewByIDView(PermissionRequiredMixin, RedirectView):
    """Displays category with passed id."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        category_id = self.kwargs["id"]
        category = lfs_get_object_or_404(Category, pk=category_id)
        return reverse("lfs_category", kwargs={"slug": category.slug})


class NoCategoriesView(PermissionRequiredMixin, TemplateView):
    """Displays that there are no categories."""

    template_name = "manage/categories/no_categories.html"
    permission_required = "core.manage_shop"


def category_view(request, category_id):
    """Renders the view tab content for a category."""
    category = lfs_get_object_or_404(Category, pk=category_id)
    form = CategoryViewForm(instance=category)

    return render_to_string(
        "manage/categories/tabs/_view.html",
        request=request,
        context={
            "category": category,
            "form": form,
        },
    )


class SortCategoriesView(PermissionRequiredMixin, TemplateView):
    """View for sorting categories."""

    permission_required = "core.manage_shop"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles category sorting."""
        categories_data = request.POST.get("categories", "")

        if categories_data:
            try:
                # Parse the hierarchical category data
                category_pairs = categories_data.split("&")

                # Group categories by parent for proper positioning
                categories_by_parent = {}

                for pair in category_pairs:
                    if "=" in pair:
                        child_part, parent_id = pair.split("=", 1)

                        # Extract category ID from format: category[123]
                        if child_part.startswith("category[") and child_part.endswith("]"):
                            child_id = child_part[9:-1]  # Extract ID from category[123]

                            if parent_id not in categories_by_parent:
                                categories_by_parent[parent_id] = []
                            categories_by_parent[parent_id].append(child_id)

                # Update categories with proper positioning
                for parent_id, child_ids in categories_by_parent.items():
                    pos = 10

                    for child_id in child_ids:
                        try:
                            child_obj = Category.objects.get(pk=child_id)

                            # Set parent
                            parent_obj = None
                            if parent_id != "root":
                                parent_obj = Category.objects.get(pk=parent_id)

                            child_obj.parent = parent_obj
                            child_obj.position = pos
                            child_obj.save()

                            pos += 10

                        except Category.DoesNotExist:
                            continue

                # Update category levels after all changes
                set_category_levels()

                result = json.dumps(
                    {
                        "message": _("The categories have been sorted."),
                    },
                    cls=LazyEncoder,
                )

            except Exception as e:
                result = json.dumps(
                    {
                        "message": _("Error sorting categories: {}").format(str(e)),
                    },
                    cls=LazyEncoder,
                )
        else:
            result = json.dumps(
                {
                    "message": _("No category data received."),
                },
                cls=LazyEncoder,
            )

        return HttpResponse(result, content_type="application/json")
