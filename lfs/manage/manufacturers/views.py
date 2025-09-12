from typing import Dict, List, Tuple, Any, Optional

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, CreateView, DeleteView, RedirectView, TemplateView, View

from lfs.caching.utils import lfs_get_object_or_404
from lfs.manage.mixins import DirectDeleteMixin
from lfs.manage.manufacturers.forms import ManufacturerAddForm, ManufacturerForm
from lfs.manage.portlets.views import PortletsInlineView
from lfs.catalog.models import Category, Product
from lfs.manufacturer.models import Manufacturer


class ManageManufacturersView(PermissionRequiredMixin, RedirectView):
    """Dispatches to the first manufacturer or to the add manufacturer form."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        try:
            manufacturer = Manufacturer.objects.all()[0]
            return reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id})
        except IndexError:
            return reverse("lfs_manage_no_manufacturers")


# Legacy function-based view for backward compatibility
def manufacturer_dispatcher(request):
    """Legacy dispatcher - redirects to class-based view."""
    return ManageManufacturersView.as_view()(request)


class ManufacturerTabMixin:
    """Mixin for tab navigation in Manufacturer views."""

    template_name = "manage/manufacturers/manufacturer.html"
    tab_name: Optional[str] = None

    def get_manufacturer(self) -> Manufacturer:
        """Gets the Manufacturer object."""
        return get_object_or_404(Manufacturer, pk=self.kwargs["id"])

    def get_manufacturers_queryset(self):
        """Returns filtered Manufacturers based on search parameter."""
        queryset = Manufacturer.objects.all().order_by("name")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with tab navigation and Manufacturer."""
        ctx = super().get_context_data(**kwargs)
        manufacturer = getattr(self, "object", None) or self.get_manufacturer()

        ctx.update(
            {
                "manufacturer": manufacturer,
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(manufacturer),
                **self._get_navigation_context(manufacturer),
            }
        )
        return ctx

    def _get_tabs(self, manufacturer: Manufacturer) -> List[Tuple[str, str]]:
        """Creates tab navigation URLs with search parameter."""
        search_query = self.request.GET.get("q", "").strip()

        # Add search parameter if present
        if search_query:
            from urllib.parse import urlencode

            query_params = urlencode({"q": search_query})
        else:
            query_params = ""

        tabs = [
            (
                "data",
                reverse("lfs_manage_manufacturer", args=[manufacturer.pk])
                + (f"?{query_params}" if query_params else ""),
            ),
            (
                "products",
                reverse("lfs_manage_manufacturer_products", args=[manufacturer.pk])
                + (f"?{query_params}" if query_params else ""),
            ),
            (
                "seo",
                reverse("lfs_manage_manufacturer_seo", args=[manufacturer.pk])
                + (f"?{query_params}" if query_params else ""),
            ),
            (
                "portlets",
                reverse("lfs_manage_manufacturer_portlets", args=[manufacturer.pk])
                + (f"?{query_params}" if query_params else ""),
            ),
        ]

        return tabs

    def _get_navigation_context(self, manufacturer: Manufacturer) -> Dict[str, Any]:
        """Returns navigation context data."""
        return {
            "manufacturer": manufacturer,
            "manufacturers": self.get_manufacturers_queryset(),
            "search_query": self.request.GET.get("q", ""),
        }


class ManufacturerDataView(PermissionRequiredMixin, ManufacturerTabMixin, UpdateView):
    """View for data tab of a Manufacturer."""

    model = Manufacturer
    form_class = ManufacturerForm
    tab_name = "data"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the data tab after successful save."""
        return reverse("lfs_manage_manufacturer", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        # Handle image deletion if checkbox is checked
        if self.request.POST.get("delete_image"):
            manufacturer = self.get_object()
            if manufacturer.image:
                manufacturer.image.delete()
                manufacturer.image = None
                manufacturer.save()

        response = super().form_valid(form)
        messages.success(self.request, _("Manufacturer data has been saved."))
        return response


class ManufacturerProductsView(PermissionRequiredMixin, ManufacturerTabMixin, TemplateView):
    """View for products tab of a Manufacturer."""

    tab_name = "products"
    template_name = "manage/manufacturers/manufacturer.html"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the products tab."""
        return reverse("lfs_manage_manufacturer_products", kwargs={"id": self.kwargs["id"]})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles product operations (assign/remove)."""
        if "assign_products" in request.POST:
            return self._handle_assign_products(request)
        elif "remove_products" in request.POST:
            return self._handle_remove_products(request)

        return super().post(request, *args, **kwargs)

    def _handle_assign_products(self, request: HttpRequest) -> HttpResponse:
        """Handles assigning products to manufacturer."""
        manufacturer = self.get_manufacturer()

        for temp_id in request.POST.keys():
            if temp_id.startswith("product"):
                temp_id = temp_id.split("-")[1]
                product = Product.objects.get(pk=temp_id)
                product.manufacturer = manufacturer
                product.save()

        messages.success(self.request, _("Products have been assigned."))
        return HttpResponseRedirect(self.get_success_url())

    def _handle_remove_products(self, request: HttpRequest) -> HttpResponse:
        """Handles removing products from manufacturer."""
        manufacturer = self.get_manufacturer()

        for temp_id in request.POST.keys():
            if temp_id.startswith("product"):
                temp_id = temp_id.split("-")[1]
                product = Product.objects.get(pk=temp_id)
                product.manufacturer = None
                product.save()

        messages.success(self.request, _("Products have been removed."))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with products and filters."""
        ctx = super().get_context_data(**kwargs)
        manufacturer = self.get_manufacturer()

        # Get assigned products
        manufacturer_products = Product.objects.filter(manufacturer=manufacturer).select_related("parent")

        # Handle filters
        r = self.request.POST if self.request.method == "POST" else self.request.GET
        s = self.request.session

        if r.get("keep-filters") or r.get("page"):
            page = r.get("page", s.get("manufacturer_page", 1))
            filter_ = r.get("filter", s.get("filter"))
            category_filter = r.get("products_category_filter", s.get("products_category_filter"))
        else:
            page = r.get("page", 1)
            filter_ = r.get("filter")
            category_filter = r.get("products_category_filter")

        # Save filters in session (convert None to empty string for display)
        s["manufacturer_page"] = page
        s["filter"] = filter_ or ""
        s["products_category_filter"] = category_filter or ""

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

        # Get available products (excluding already assigned)
        products = Product.objects.select_related("parent").filter(filters)
        paginator = Paginator(products.exclude(pk__in=manufacturer_products), 25)

        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = 0

        # Get all categories for filter dropdown
        categories = Category.objects.all().order_by("name")

        ctx.update(
            {
                "manufacturer_products": manufacturer_products,
                "page": page_obj,
                "paginator": paginator,
                "filter": filter_ or "",
                "category_filter": category_filter or "",
                "categories": categories,
            }
        )
        return ctx


class ManufacturerSEOView(PermissionRequiredMixin, ManufacturerTabMixin, UpdateView):
    """View for SEO tab of a Manufacturer."""

    model = Manufacturer
    fields = ["meta_title", "meta_description", "meta_keywords"]
    tab_name = "seo"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the SEO tab after successful save."""
        return reverse("lfs_manage_manufacturer_seo", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        response = super().form_valid(form)
        messages.success(self.request, _("SEO data has been saved."))
        return response


class ManufacturerPortletsView(PermissionRequiredMixin, ManufacturerTabMixin, TemplateView):
    """View for portlets tab of a Manufacturer."""

    tab_name = "portlets"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with portlets."""
        ctx = super().get_context_data(**kwargs)
        manufacturer = self.get_manufacturer()
        ctx["portlets"] = PortletsInlineView().get(self.request, manufacturer)
        return ctx


class ManufacturerCreateView(SuccessMessageMixin, PermissionRequiredMixin, CreateView):
    """Provides a form to add a new manufacturer."""

    model = Manufacturer
    form_class = ManufacturerAddForm
    template_name = "manage/manufacturers/add_manufacturer.html"
    permission_required = "core.manage_shop"
    success_message = _("Manufacturer has been created.")

    def get_success_url(self):
        return reverse("lfs_manage_manufacturer", kwargs={"id": self.object.id})


class ManufacturerDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a manufacturer."""

    template_name = "manage/manufacturers/delete_manufacturer.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["manufacturer"] = get_object_or_404(Manufacturer, pk=self.kwargs["id"])
        return context


class ManufacturerDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes manufacturer with passed id."""

    model = Manufacturer
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"
    success_message = _("Manufacturer has been deleted.")

    def get_success_url(self):
        return reverse("lfs_manage_manufacturers")


class ManufacturerViewByIDView(PermissionRequiredMixin, RedirectView):
    """Displays manufacturer with passed id."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        manufacturer_id = self.kwargs["id"]
        manufacturer = lfs_get_object_or_404(Manufacturer, pk=manufacturer_id)
        return reverse("lfs_manufacturer", kwargs={"slug": manufacturer.slug})


class NoManufacturersView(PermissionRequiredMixin, TemplateView):
    """Displays that there are no manufacturers."""

    template_name = "manage/manufacturers/no_manufacturers.html"
    permission_required = "core.manage_shop"


class ManufacturersAjaxView(PermissionRequiredMixin, View):
    """Returns list of manufacturers for autocomplete"""

    permission_required = "core.manage_shop"

    def get(self, request, *args, **kwargs):
        term = request.GET.get("term", "")
        manufacturers = Manufacturer.objects.filter(name__istartswith=term)[:10]

        out = []
        for man in manufacturers:
            out.append({"label": man.name, "value": man.pk})

        return JsonResponse(out, safe=False)
