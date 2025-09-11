import json
from typing import Dict, List, Tuple, Any, Optional

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, CreateView, DeleteView, RedirectView, TemplateView

from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category, GroupsPropertiesRelation, Product, Property, PropertyGroup
from lfs.core.utils import LazyEncoder
from lfs.core.signals import product_removed_property_group
from lfs.manage.mixins import DirectDeleteMixin
from lfs.manage.property_groups.forms import PropertyGroupForm


class ManagePropertyGroupsView(PermissionRequiredMixin, RedirectView):
    """Dispatches to the first property group or to the add property group form."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        # Use the same filtering logic as the tab mixin
        queryset = PropertyGroup.objects.all().order_by("name")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        try:
            property_group = queryset[0]
            return reverse("lfs_manage_property_group", kwargs={"id": property_group.id})
        except IndexError:
            return reverse("lfs_manage_no_property_groups")


class PropertyGroupTabMixin:
    """Mixin for tab navigation in PropertyGroup views."""

    template_name = "manage/property_groups/property_group.html"
    tab_name: Optional[str] = None

    def get_property_group(self) -> PropertyGroup:
        """Gets the PropertyGroup object."""
        return get_object_or_404(PropertyGroup, pk=self.kwargs["id"])

    def get_property_groups_queryset(self):
        """Returns filtered PropertyGroups based on search parameter."""
        queryset = PropertyGroup.objects.all().order_by("name")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with tab navigation and PropertyGroup."""
        # Ensure object is set before calling super()
        if not hasattr(self, "object") or self.object is None:
            self.object = self.get_property_group()

        ctx = super().get_context_data(**kwargs)
        property_group = self.object

        ctx.update(
            {
                "property_group": property_group,
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(property_group),
                **self._get_navigation_context(property_group),
            }
        )
        return ctx

    def _get_tabs(self, property_group: PropertyGroup) -> List[Tuple[str, str]]:
        """Creates tab navigation URLs with search parameter."""
        search_query = self.request.GET.get("q", "").strip()

        data_url = reverse("lfs_manage_property_group", args=[property_group.pk])
        products_url = reverse("lfs_manage_property_group_products", args=[property_group.pk])
        properties_url = reverse("lfs_manage_property_group_properties", args=[property_group.pk])

        # Add search parameter if present
        if search_query:
            from urllib.parse import urlencode

            query_params = urlencode({"q": search_query})
            data_url += "?" + query_params
            products_url += "?" + query_params
            properties_url += "?" + query_params

        tabs = [
            ("data", data_url),
            ("products", products_url),
            ("properties", properties_url),
        ]

        return tabs

    def _get_navigation_context(self, property_group: PropertyGroup) -> Dict[str, Any]:
        """Returns navigation context data."""
        return {
            "property_group": property_group,
            "property_groups": self.get_property_groups_queryset(),
            "search_query": self.request.GET.get("q", ""),
        }


class PropertyGroupDataView(PermissionRequiredMixin, PropertyGroupTabMixin, UpdateView):
    """View for data tab of a PropertyGroup."""

    model = PropertyGroup
    form_class = PropertyGroupForm
    tab_name = "data"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_object(self, queryset=None):
        """Get the PropertyGroup object."""
        return self.get_property_group()

    def get_success_url(self) -> str:
        """Stays on the data tab after successful save."""
        return reverse("lfs_manage_property_group", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        response = super().form_valid(form)
        messages.success(self.request, _("Property group has been saved."))
        return response


class PropertyGroupProductsView(PermissionRequiredMixin, PropertyGroupTabMixin, TemplateView):
    """View for products tab of a PropertyGroup."""

    tab_name = "products"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the products tab."""
        return reverse("lfs_manage_property_group_products", kwargs={"id": self.kwargs["id"]})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles product operations (assign/remove)."""
        if "assign_products" in request.POST:
            return self._handle_assign_products(request)
        elif "remove_products" in request.POST:
            return self._handle_remove_products(request)

        return super().post(request, *args, **kwargs)

    def _handle_assign_products(self, request: HttpRequest) -> HttpResponse:
        """Handles assigning products to property group."""
        property_group = self.get_property_group()

        # Get all checked product checkboxes
        for key, value in request.POST.items():
            if key.startswith("product-") and value == "on":
                product_id = key.split("-")[1]
                # Skip if product_id is empty or not a valid integer
                if not product_id or not product_id.isdigit():
                    continue
                try:
                    product = Product.objects.get(pk=product_id)
                    property_group.products.add(product)
                except Product.DoesNotExist:
                    pass

        messages.success(self.request, _("Products have been assigned."))
        return HttpResponseRedirect(self.get_success_url())

    def _handle_remove_products(self, request: HttpRequest) -> HttpResponse:
        """Handles removing products from property group."""
        property_group = self.get_property_group()

        # Get all checked product checkboxes
        for key, value in request.POST.items():
            if key.startswith("product-") and value == "on":
                product_id = key.split("-")[1]
                # Skip if product_id is empty or not a valid integer
                if not product_id or not product_id.isdigit():
                    continue
                try:
                    product = Product.objects.get(pk=product_id)
                    property_group.products.remove(product)

                    # Notify removing
                    product_removed_property_group.send(sender=property_group, product=product)
                except Product.DoesNotExist:
                    pass

        messages.success(self.request, _("Products have been removed."))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with products and filters."""
        ctx = super().get_context_data(**kwargs)
        property_group = self.get_property_group()

        # Get assigned products
        group_products = property_group.products.all().select_related("parent")

        # Handle filters
        r = self.request.POST if self.request.method == "POST" else self.request.GET
        s = self.request.session

        if r.get("keep-filters") or r.get("page"):
            page = r.get("page", s.get("property_group_page", 1))
            filter_ = r.get("filter", s.get("filter"))
            category_filter = r.get("products_category_filter", s.get("products_category_filter"))
            amount = int(r.get("products-amount", s.get("products_amount", 25)))
        else:
            page = r.get("page", 1)
            filter_ = r.get("filter")
            category_filter = r.get("products_category_filter")
            amount = int(r.get("products-amount", 25))

        # Save filters in session (convert None to empty string for display)
        s["property_group_page"] = page
        s["filter"] = filter_ or ""
        s["products_category_filter"] = category_filter or ""
        s["products_amount"] = amount

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

        # Get available products (excluding already assigned)
        products = Product.objects.select_related("parent").filter(filters)
        paginator = Paginator(products.exclude(pk__in=group_products), amount)

        page_obj = paginator.get_page(page)

        # Get all categories for filter dropdown in hierarchical structure
        categories = self._build_hierarchical_categories()

        ctx.update(
            {
                "group_products": group_products,
                "page": page_obj,
                "paginator": paginator,
                "filter": filter_ or "",
                "category_filter": category_filter or "",
                "categories": categories,
                "amount": amount,
            }
        )
        return ctx

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


class PropertyGroupPropertiesView(PermissionRequiredMixin, PropertyGroupTabMixin, TemplateView):
    """View for properties tab of a PropertyGroup."""

    tab_name = "properties"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the properties tab."""
        return reverse("lfs_manage_property_group_properties", kwargs={"id": self.kwargs["id"]})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles property operations (assign/update/remove)."""
        if "assign_properties" in request.POST:
            return self._handle_assign_properties(request)
        elif "update_properties" in request.POST:
            return self._handle_update_properties(request)
        elif "remove_properties" in request.POST:
            return self._handle_remove_properties(request)

        return super().post(request, *args, **kwargs)

    def _handle_assign_properties(self, request: HttpRequest) -> HttpResponse:
        """Handles assigning properties to property group."""
        property_group = self.get_property_group()

        for temp_id in request.POST.keys():
            if temp_id.startswith("property"):
                property_id = temp_id.split("-")[1]
                GroupsPropertiesRelation.objects.get_or_create(group_id=property_group.id, property_id=property_id)

        _udpate_positions(property_group.id)
        messages.success(self.request, _("Properties have been assigned."))
        return HttpResponseRedirect(self.get_success_url())

    def _handle_update_properties(self, request: HttpRequest) -> HttpResponse:
        """Handles updating property positions."""
        property_group = self.get_property_group()

        for gp in GroupsPropertiesRelation.objects.filter(group=property_group.id):
            position = request.POST.get("position-%s" % gp.property.id, 999)
            gp.position = int(position)
            gp.save()

        _udpate_positions(property_group.id)
        messages.success(self.request, _("Properties have been updated."))
        return HttpResponseRedirect(self.get_success_url())

    def _handle_remove_properties(self, request: HttpRequest) -> HttpResponse:
        """Handles removing properties from property group."""
        property_group = self.get_property_group()

        # Get all checked property checkboxes
        for key, value in request.POST.items():
            if key.startswith("property-") and value == "on":
                property_id = key.split("-")[1]
                # Skip if property_id is empty or not a valid integer
                if not property_id or not property_id.isdigit():
                    continue
                try:
                    gp = GroupsPropertiesRelation.objects.get(group=property_group.id, property=property_id)
                    gp.delete()
                except GroupsPropertiesRelation.DoesNotExist:
                    pass

        _udpate_positions(property_group.id)
        messages.success(self.request, _("Properties have been removed."))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with properties."""
        ctx = super().get_context_data(**kwargs)
        property_group = self.get_property_group()

        # Get filters from request
        filter_value = self.request.GET.get("filter", "")
        type_filter = self.request.GET.get("properties_type_filter", "All")
        amount = int(self.request.GET.get("properties-amount", 25))

        gps = GroupsPropertiesRelation.objects.filter(group=property_group.id).select_related("property")
        group_properties = gps

        # Calculate assignable properties with filters
        assignable_properties = Property.objects.exclude(local=True).exclude(groupspropertiesrelation__in=gps)

        # Apply search filter
        if filter_value:
            assignable_properties = assignable_properties.filter(name__icontains=filter_value)

        # Apply type filter
        if type_filter != "All":
            assignable_properties = assignable_properties.filter(type=type_filter)

        assignable_properties = assignable_properties.order_by("name")

        # Pagination
        paginator = Paginator(assignable_properties, amount)
        page_number = self.request.GET.get("page", 1)
        page = paginator.get_page(page_number)

        ctx.update(
            {
                "property_group": property_group,
                "properties": assignable_properties,
                "gps": gps,
                "group_properties": group_properties,
                "page": page,
                "filter": filter_value,
                "type_filter": type_filter,
                "amount": amount,
            }
        )
        return ctx


class NoPropertyGroupsView(PermissionRequiredMixin, TemplateView):
    """Displays that there are no property groups."""

    template_name = "manage/property_groups/no_property_groups.html"
    permission_required = "core.manage_shop"


class PropertyGroupCreateView(SuccessMessageMixin, PermissionRequiredMixin, CreateView):
    """Provides a form to add a new property group."""

    model = PropertyGroup
    form_class = PropertyGroupForm
    template_name = "manage/property_groups/add_property_group.html"
    permission_required = "core.manage_shop"
    success_message = _("Property group has been created.")

    def get_success_url(self):
        return reverse("lfs_manage_property_group", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        # CreateView doesn't need object set, but ensure it's None for consistency
        if not hasattr(self, "object"):
            self.object = None

        context = super().get_context_data(**kwargs)
        context["property_groups"] = PropertyGroup.objects.all()
        context["came_from"] = self.request.GET.get("came_from", reverse("lfs_manage_property_groups"))
        return context


class PropertyGroupDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a property group."""

    template_name = "manage/property_groups/delete_property_group.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["property_group"] = get_object_or_404(PropertyGroup, pk=self.kwargs["id"])
        return context


class PropertyGroupDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes property group with passed id."""

    model = PropertyGroup
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"
    success_message = _("Property group has been deleted.")

    def get_success_url(self):
        return reverse("lfs_manage_property_groups")


def _udpate_positions(group_id):
    """ """
    for i, gp in enumerate(GroupsPropertiesRelation.objects.filter(group=group_id)):
        gp.position = (i + 1) * 10
        gp.save()


def sort_property_groups(request):
    """Sort property groups"""
    property_group_list = request.POST.get("serialized", "").split("&")
    assert isinstance(property_group_list, list)
    if len(property_group_list) > 0:
        pos = 10
        for cat_str in property_group_list:
            elem, pg_id = cat_str.split("=")
            pg = PropertyGroup.objects.get(pk=pg_id)
            pg.position = pos
            pg.save()
            pos += 10

    result = json.dumps(
        {
            "message": _("The Property groups have been sorted."),
        },
        cls=LazyEncoder,
    )

    return HttpResponse(result, content_type="application/json")
