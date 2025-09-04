from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, DeleteView, CreateView

from lfs.catalog.models import DeliveryTime
from lfs.catalog.models import Product
from lfs.manage.mixins import DirectDeleteMixin


from django.views.generic.base import RedirectView


class ManageDeliveryTimesView(PermissionRequiredMixin, RedirectView):
    """Redirects to the first delivery time or to the form to add a delivery
    time (if there is no delivery time yet).
    """

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        try:
            delivery_time = DeliveryTime.objects.all()[0]
            return reverse("lfs_manage_delivery_time", kwargs={"pk": delivery_time.id})
        except IndexError:
            return reverse("lfs_no_delivery_times")


class DeliveryTimeUpdateView(PermissionRequiredMixin, UpdateView):
    model = DeliveryTime
    fields = ("min", "max", "unit", "description")
    template_name = "manage/delivery_times/delivery_time.html"
    permission_required = "core.manage_shop"
    context_object_name = "delivery_time"

    def get_success_url(self):
        search_query = self.request.POST.get("q", "")
        url = reverse_lazy("lfs_manage_delivery_time", kwargs={"pk": self.object.id})
        if search_query:
            url = f"{url}?q={search_query}"
        return url

    def get_delivery_times_queryset(self):
        """Liefert gefilterte DeliveryTimes basierend auf Suchparameter."""
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            # Filter delivery times based on min, max, description and unit
            queryset = DeliveryTime.objects.filter(
                Q(min__icontains=search_query) | Q(max__icontains=search_query) | Q(description__icontains=search_query)
            )

            # Search in unit display values (translated units)
            from lfs.catalog.settings import (
                DELIVERY_TIME_UNIT_HOURS,
                DELIVERY_TIME_UNIT_DAYS,
                DELIVERY_TIME_UNIT_WEEKS,
                DELIVERY_TIME_UNIT_MONTHS,
                DELIVERY_TIME_UNIT_CHOICES,
            )
            from django.utils.translation import gettext

            # Get translated unit names
            unit_choices_dict = dict(DELIVERY_TIME_UNIT_CHOICES)
            translated_hours = gettext(unit_choices_dict[DELIVERY_TIME_UNIT_HOURS])
            translated_days = gettext(unit_choices_dict[DELIVERY_TIME_UNIT_DAYS])
            translated_weeks = gettext(unit_choices_dict[DELIVERY_TIME_UNIT_WEEKS])
            translated_months = gettext(unit_choices_dict[DELIVERY_TIME_UNIT_MONTHS])

            unit_filters = Q()
            search_lower = search_query.lower()
            if translated_hours.lower() in search_lower or search_lower in translated_hours.lower():
                unit_filters |= Q(unit=DELIVERY_TIME_UNIT_HOURS)
            if translated_days.lower() in search_lower or search_lower in translated_days.lower():
                unit_filters |= Q(unit=DELIVERY_TIME_UNIT_DAYS)
            if translated_weeks.lower() in search_lower or search_lower in translated_weeks.lower():
                unit_filters |= Q(unit=DELIVERY_TIME_UNIT_WEEKS)
            if translated_months.lower() in search_lower or search_lower in translated_months.lower():
                unit_filters |= Q(unit=DELIVERY_TIME_UNIT_MONTHS)

            if unit_filters:
                queryset = queryset | DeliveryTime.objects.filter(unit_filters)

            return queryset.order_by("min")
        else:
            # All delivery times
            return DeliveryTime.objects.all().order_by("min")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["delivery_times"] = self.get_delivery_times_queryset()
        context["search_query"] = self.request.GET.get("q", "")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Delivery time has been saved."))
        return response


class NoDeliveryTimesView(PermissionRequiredMixin, TemplateView):
    """Displays a view when there are no delivery times."""

    template_name = "manage/delivery_times/no_delivery_times.html"
    permission_required = "core.manage_shop"


class DeliveryTimeCreateView(PermissionRequiredMixin, CreateView):
    model = DeliveryTime
    fields = ("min", "max", "unit")
    template_name = "manage/delivery_times/add_delivery_time.html"
    permission_required = "core.manage_shop"

    def get_success_url(self):
        search_query = self.request.POST.get("q", "")
        url = reverse_lazy("lfs_manage_delivery_time", kwargs={"pk": self.object.id})
        if search_query:
            url = f"{url}?q={search_query}"
        return url

    def get_form_kwargs(self):
        # Add prefix to form fields to avoid conflicts with existing fields, as this view is used within a modal
        kwargs = super().get_form_kwargs()
        kwargs["prefix"] = "create"
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["came_from"] = self.request.POST.get("came_from", reverse("lfs_manage_delivery_times"))
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Delivery time has been added."))
        # Always redirect to the created delivery time to avoid blank HTMX renders
        return HttpResponseRedirect(self.get_success_url())


class DeliveryTimeDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a delivery time."""

    template_name = "manage/delivery_times/delete_delivery_time.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["delivery_time"] = get_object_or_404(DeliveryTime, pk=self.kwargs["pk"])
        return context


class DeliveryTimeDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes the delivery time with passed id."""

    model = DeliveryTime
    permission_required = "core.manage_shop"
    success_message = _("Delivery time has been deleted.")

    def get_success_url(self):
        """Return the URL to redirect to after successful deletion."""
        # Find next delivery time to redirect to
        first_delivery_time = DeliveryTime.objects.exclude(pk=self.object.pk).first()
        if first_delivery_time:
            return reverse("lfs_manage_delivery_time", kwargs={"pk": first_delivery_time.id})
        else:
            return reverse("lfs_no_delivery_times")

    def delete(self, request, *args, **kwargs):
        """Override delete to clean up references before deletion."""
        delivery_time = self.get_object()

        # Remove the delivery time from all products delivery
        for product in Product.objects.filter(delivery_time=delivery_time):
            product.delivery_time = None
            product.save()

        # Remove the delivery time from all products order_time
        for product in Product.objects.filter(order_time=delivery_time):
            product.order_time = None
            product.save()

        # Remove the delivery time from the shop
        from lfs.core.utils import get_default_shop

        shop = get_default_shop(request)
        if shop.delivery_time == delivery_time:
            shop.delivery_time = None
            shop.save()

        return super().delete(request, *args, **kwargs)
