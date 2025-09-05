from typing import Dict, List, Tuple, Any, Optional

# django imports
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, CreateView, DeleteView, RedirectView, TemplateView

# lfs imports
from lfs.catalog.models import Category, Product
from lfs.caching.utils import lfs_get_object_or_404
from lfs.discounts.models import Discount
from lfs.manage.discounts.forms import DiscountForm
from lfs.manage.mixins import DirectDeleteMixin
from lfs.manufacturer.models import Manufacturer


class ManageDiscountsView(PermissionRequiredMixin, RedirectView):
    """Dispatches to the first discount or to the add discount form."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        try:
            discount = Discount.objects.all().order_by("name")[0]
            return reverse("lfs_manage_discount", kwargs={"id": discount.id})
        except IndexError:
            return reverse("lfs_manage_no_discounts")


class NoDiscountsView(PermissionRequiredMixin, TemplateView):
    """Displays that no discounts exist."""

    permission_required = "core.manage_shop"
    template_name = "manage/discounts/no_discounts.html"


class DiscountTabMixin:
    """Mixin for tab navigation in Discount views."""

    template_name = "manage/discounts/discount.html"
    tab_name: Optional[str] = None

    def get_discount(self) -> Discount:
        """Gets the Discount object."""
        return get_object_or_404(Discount, pk=self.kwargs["id"])

    def get_discounts_queryset(self):
        """Returns filtered Discounts based on search parameter."""
        queryset = Discount.objects.all().order_by("name")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with tab navigation and Discount."""
        ctx = super().get_context_data(**kwargs)
        discount = getattr(self, "object", None) or self.get_discount()

        ctx.update(
            {
                "discount": discount,
                "discounts": self.get_discounts_queryset(),
                "search_query": self.request.GET.get("q", ""),
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(discount),
            }
        )
        return ctx

    def _get_tabs(self, discount: Discount) -> List[Tuple[str, str]]:
        """Creates tab navigation URLs with search parameter."""
        search_query = self.request.GET.get("q", "").strip()

        data_url = reverse("lfs_manage_discount", args=[discount.pk])
        criteria_url = reverse("lfs_manage_discount_criteria", args=[discount.pk])
        products_url = reverse("lfs_manage_discount_products", args=[discount.pk])

        # Add search parameter if present
        if search_query:
            from urllib.parse import urlencode

            query_params = urlencode({"q": search_query})
            data_url += "?" + query_params
            criteria_url += "?" + query_params
            products_url += "?" + query_params

        return [
            ("data", data_url),
            ("criteria", criteria_url),
            ("products", products_url),
        ]


class DiscountDataView(PermissionRequiredMixin, DiscountTabMixin, UpdateView):
    """View for data tab of a Discount."""

    model = Discount
    form_class = DiscountForm
    tab_name = "data"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the data tab after successful save."""
        return reverse("lfs_manage_discount", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        response = super().form_valid(form)
        messages.success(self.request, _("Discount has been saved."))
        return response


class DiscountCriteriaView(PermissionRequiredMixin, DiscountTabMixin, TemplateView):
    """View for criteria tab of a Discount."""

    tab_name = "criteria"
    template_name = "manage/discounts/discount.html"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the criteria tab."""
        return reverse("lfs_manage_discount_criteria", kwargs={"id": self.kwargs["id"]})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles criteria saving."""
        discount = self.get_discount()
        discount.save_criteria(request)

        messages.success(self.request, _("Criteria have been saved."))

        # Check if this is an HTMX request
        if request.headers.get("HX-Request"):
            # Return the updated criteria tab content
            return render(request, "manage/discounts/tabs/_criteria.html", self.get_context_data())

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with criteria."""
        ctx = super().get_context_data(**kwargs)
        discount = self.get_discount()

        criteria = []
        position = 0
        for criterion_object in discount.get_criteria():
            position += 10
            criterion_html = criterion_object.get_content_object().render(self.request, position)
            criteria.append(criterion_html)

        ctx.update(
            {
                "criteria": criteria,
            }
        )
        return ctx


class DiscountProductsView(PermissionRequiredMixin, DiscountTabMixin, TemplateView):
    """View for products tab of a Discount."""

    tab_name = "products"
    template_name = "manage/discounts/discount.html"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the products tab."""
        return reverse("lfs_manage_discount_products", kwargs={"id": self.kwargs["id"]})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles product operations (assign/remove)."""
        if "assign_products" in request.POST:
            return self._handle_assign_products(request)
        elif "remove_products" in request.POST:
            return self._handle_remove_products(request)

        return super().post(request, *args, **kwargs)

    def _handle_assign_products(self, request: HttpRequest) -> HttpResponse:
        """Handles assigning products to discount."""
        discount = self.get_discount()

        for temp_id in request.POST.keys():
            if temp_id.startswith("product"):
                temp_id = temp_id.split("-")[1]
                product = Product.objects.get(pk=temp_id)
                discount.products.add(product)

        messages.success(self.request, _("Products have been assigned."))
        return HttpResponseRedirect(self.get_success_url())

    def _handle_remove_products(self, request: HttpRequest) -> HttpResponse:
        """Handles removing products from discount."""
        discount = self.get_discount()

        for temp_id in request.POST.keys():
            if temp_id.startswith("product"):
                temp_id = temp_id.split("-")[1]
                product = Product.objects.get(pk=temp_id)
                discount.products.remove(product)

        messages.success(self.request, _("Products have been removed."))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with products and filters."""
        ctx = super().get_context_data(**kwargs)
        discount = self.get_discount()

        # Get assigned products
        discount_products = discount.products.all().select_related("parent")

        # Handle filters
        r = self.request.POST if self.request.method == "POST" else self.request.GET
        s = self.request.session

        if r.get("keep-filters") or r.get("page"):
            page = r.get("page", s.get("discount_page", 1))
            filter_ = r.get("filter", s.get("filter"))
            category_filter = r.get("products_category_filter", s.get("products_category_filter"))
            manufacturer_filter = r.get("products_manufacturer_filter", s.get("products_manufacturer_filter"))
        else:
            page = r.get("page", 1)
            filter_ = r.get("filter")
            category_filter = r.get("products_category_filter")
            manufacturer_filter = r.get("products_manufacturer_filter")

        # Save filters in session (convert None to empty string for display)
        s["discount_page"] = page
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
                category = lfs_get_object_or_404(Category, pk=category_filter)
                categories = [category]
                categories.extend(category.get_all_children())
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
        paginator = Paginator(products.exclude(pk__in=discount_products), 25)

        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = 0

        ctx.update(
            {
                "discount_products": discount_products,
                "page": page_obj,
                "paginator": paginator,
                "filter": filter_ or "",
                "category_filter": category_filter or "",
                "manufacturer_filter": manufacturer_filter or "",
            }
        )
        return ctx


class DiscountCreateView(PermissionRequiredMixin, CreateView):
    """Provides a modal form to add a new discount."""

    model = Discount
    form_class = DiscountForm
    template_name = "manage/discounts/add_discount.html"
    permission_required = "core.manage_shop"

    def form_valid(self, form):
        """Saves discount and redirects."""
        discount = form.save()

        messages.success(self.request, _("Discount has been created."))
        return HttpResponseRedirect(reverse("lfs_manage_discount", kwargs={"id": discount.id}))

    def get_success_url(self):
        """Return the URL to redirect to after successful form submission."""
        return reverse("lfs_manage_discount", kwargs={"id": self.object.id})


class DiscountDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a discount."""

    template_name = "manage/discounts/delete_discount.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["discount"] = get_object_or_404(Discount, pk=self.kwargs["id"])
        return context


class DiscountDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes discount with passed id."""

    model = Discount
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"
    success_message = _("Discount has been deleted.")

    def get_success_url(self):
        return reverse("lfs_manage_discounts")
