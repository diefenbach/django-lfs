from typing import Dict, Any

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, CreateView, DeleteView, RedirectView, TemplateView

from lfs.caching.listeners import invalidate_cache_group_id
from lfs.catalog.models import Property, PropertyOption
from lfs.core.signals import property_type_changed
from lfs.core.utils import atof
from lfs.manage.mixins import DirectDeleteMixin
from lfs.manage.properties.forms import PropertyAddForm, PropertyDataForm


class ManagePropertiesView(PermissionRequiredMixin, RedirectView):
    """Dispatches to the first property or to the add property form."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        try:
            property = Property.objects.filter(local=False)[0]
            return reverse("lfs_manage_property", kwargs={"id": property.id})
        except IndexError:
            return reverse("lfs_add_property")


class PropertyNavigationMixin:
    """Mixin for navigation in Property views."""

    template_name = "manage/properties/property.html"

    def get_property(self) -> Property:
        """Gets the Property object."""
        return get_object_or_404(Property, pk=self.kwargs["id"])

    def get_properties_queryset(self):
        """Returns filtered Properties based on search parameter."""
        queryset = Property.objects.filter(local=False).order_by("name")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            from django.db.models import Q

            queryset = queryset.filter(Q(name__icontains=search_query) | Q(title__icontains=search_query))

        return queryset

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with navigation and Property."""
        ctx = super().get_context_data(**kwargs)
        property = getattr(self, "object", None) or self.get_property()

        ctx.update(
            {
                "property": property,
                **self._get_navigation_context(property),
            }
        )
        return ctx

    def _get_navigation_context(self, property: Property) -> Dict[str, Any]:
        """Returns navigation context data."""
        properties = self.get_properties_queryset()

        return {
            "property": property,
            "properties": properties,
            "page": properties,  # Use properties directly instead of paginated page
            "search_query": self.request.GET.get("q", ""),
        }


class PropertyDataView(PermissionRequiredMixin, PropertyNavigationMixin, UpdateView):
    """View for data tab of a Property."""

    model = Property
    form_class = PropertyDataForm
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the data tab after successful save."""
        return reverse("lfs_manage_property", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        old_type = self.get_object().type
        response = super().form_valid(form)

        # Send signal only when the type changed as all values are deleted.
        if old_type != self.object.type:
            property_type_changed.send(self.object)

        # invalidate global properties version number (all product property caches will be invalidated)
        invalidate_cache_group_id("global-properties-version")

        self._update_property_positions()
        messages.success(self.request, _("Property has been saved."))
        return response

    def _update_property_positions(self):
        """Updates position of properties."""
        for i, property in enumerate(Property.objects.exclude(local=True)):
            property.position = (i + 1) * 10
            property.save()


class PropertyCreateView(SuccessMessageMixin, PermissionRequiredMixin, CreateView):
    """Provides a form to add a new property."""

    model = Property
    form_class = PropertyAddForm
    template_name = "manage/properties/add_property.html"
    permission_required = "core.manage_shop"
    success_message = _("Property has been created.")

    def get_success_url(self):
        return reverse("lfs_manage_property", kwargs={"id": self.object.id})

    def form_valid(self, form):
        """Saves the property with default values."""
        response = super().form_valid(form)
        self.object.position = 1000
        self.object.title = self.object.name
        self.object.save()
        self._update_property_positions()
        return response

    def _update_property_positions(self):
        """Updates position of properties."""
        for i, property in enumerate(Property.objects.exclude(local=True)):
            property.position = (i + 1) * 10
            property.save()


class PropertyDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a property."""

    template_name = "manage/properties/delete_property.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["property"] = get_object_or_404(Property, pk=self.kwargs["id"])
        return context


class PropertyDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes property with passed id."""

    model = Property
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"
    success_message = _("Property has been deleted.")

    def get_success_url(self):
        return reverse("lfs_manage_properties")

    def delete(self, request, *args, **kwargs):
        """Deletes and updates positions."""
        response = super().delete(request, *args, **kwargs)
        self._update_property_positions()
        # invalidate global properties version number (all product property caches will be invalidated)
        invalidate_cache_group_id("global-properties-version")
        return response

    def _update_property_positions(self):
        """Updates position of properties."""
        for i, property in enumerate(Property.objects.exclude(local=True)):
            property.position = (i + 1) * 10
            property.save()


class NoPropertiesView(PermissionRequiredMixin, TemplateView):
    """Displays that no properties exist."""

    template_name = "manage/properties/no_properties.html"
    permission_required = "core.manage_shop"


class PropertyOptionAddView(PermissionRequiredMixin, RedirectView):
    """Adds option to property with passed property id."""

    permission_required = "core.manage_shop"

    def post(self, request, *args, **kwargs):
        property = get_object_or_404(Property, pk=kwargs["property_id"])

        name = request.POST.get("name", "").strip()
        price_str = request.POST.get("price", "")

        if name:
            try:
                price = abs(atof(str(price_str))) if price_str else 0.0
            except (TypeError, ValueError):
                price = 0.0

            PropertyOption.objects.create(name=name, price=price, property=property)

            # invalidate global properties version number (all product property caches will be invalidated)
            invalidate_cache_group_id("global-properties-version")

            messages.success(request, _("Option has been added."))
        else:
            messages.error(request, _("Option could not be added. Name is required."))

        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("lfs_manage_property", kwargs={"id": kwargs["property_id"]})

    def _update_positions(self, property):
        """Updates position of options of given property."""
        for i, option in enumerate(property.options.all()):
            option.position = (i + 1) * 10
            option.save()


class PropertyOptionUpdateView(PermissionRequiredMixin, RedirectView):
    """Updates option of property with passed property id."""

    permission_required = "core.manage_shop"

    def post(self, request, *args, **kwargs):
        property = get_object_or_404(Property, pk=kwargs["property_id"])
        option_id = request.POST.get("option_id")

        try:
            option = PropertyOption.objects.get(pk=option_id, property=property)
        except PropertyOption.DoesNotExist:
            messages.error(request, _("Option not found."))
        else:
            name = request.POST.get("name", "").strip()
            price_str = request.POST.get("price", "")

            if name:
                try:
                    price = abs(atof(str(price_str))) if price_str else 0.0
                except (TypeError, ValueError):
                    price = 0.0

                option.name = name
                option.price = price
                option.save()

                # invalidate global properties version number (all product property caches will be invalidated)
                invalidate_cache_group_id("global-properties-version")

                messages.success(request, _("Option has been updated."))
            else:
                messages.error(request, _("Option could not be updated. Name is required."))

        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("lfs_manage_property", kwargs={"id": kwargs["property_id"]})

    def _update_positions(self, property):
        """Updates position of options of given property."""
        for i, option in enumerate(property.options.all()):
            option.position = (i + 1) * 10
            option.save()


class PropertyOptionDeleteView(PermissionRequiredMixin, DeleteView):
    """Deletes option with given id."""

    model = PropertyOption
    pk_url_kwarg = "option_id"
    permission_required = "core.manage_shop"

    def get_success_url(self):
        property = self.object.property
        return reverse("lfs_manage_property", kwargs={"id": property.id})

    def delete(self, request, *args, **kwargs):
        """Deletes and updates positions."""
        property = self.get_object().property
        response = super().delete(request, *args, **kwargs)

        self._update_positions(property)
        # invalidate global properties version number (all product property caches will be invalidated)
        invalidate_cache_group_id("global-properties-version")

        messages.success(request, _("Option has been deleted."))
        return response

    def _update_positions(self, property):
        """Updates position of options of given property."""
        for i, option in enumerate(property.options.all()):
            option.position = (i + 1) * 10
            option.save()
