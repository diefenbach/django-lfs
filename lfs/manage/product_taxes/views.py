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

from lfs.catalog.models import Product
from lfs.tax.models import Tax
from lfs.manage.mixins import DirectDeleteMixin


from django.views.generic.base import RedirectView


class ManageTaxesView(PermissionRequiredMixin, RedirectView):
    """Redirects to the first tax or to the form to add a tax
    (if there is no tax yet).
    """

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        try:
            tax = Tax.objects.all()[0]
            return reverse("lfs_manage_tax", kwargs={"pk": tax.id})
        except IndexError:
            return reverse("lfs_no_taxes")


class TaxUpdateView(PermissionRequiredMixin, UpdateView):
    model = Tax
    fields = ("rate", "description")
    template_name = "manage/product_taxes/tax.html"
    permission_required = "core.manage_shop"
    context_object_name = "tax"

    def get_success_url(self):
        search_query = self.request.POST.get("q", "")
        url = reverse_lazy("lfs_manage_tax", kwargs={"pk": self.object.id})
        if search_query:
            url = f"{url}?q={search_query}"
        return url

    def get_taxes_queryset(self):
        """Returns filtered Taxes based on search parameter."""
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            # Filter taxes based on rate and description
            queryset = Tax.objects.filter(Q(rate__icontains=search_query) | Q(description__icontains=search_query))
            return queryset.order_by("rate")
        else:
            # All taxes
            return Tax.objects.all().order_by("rate")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["taxes"] = self.get_taxes_queryset()
        context["search_query"] = self.request.GET.get("q", "")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Tax has been saved."))
        return response


class NoTaxesView(PermissionRequiredMixin, TemplateView):
    """Displays a view when there are no taxes."""

    template_name = "manage/product_taxes/no_taxes.html"
    permission_required = "core.manage_shop"


class TaxCreateView(PermissionRequiredMixin, CreateView):
    model = Tax
    fields = ("rate", "description")
    template_name = "manage/product_taxes/add_tax.html"
    permission_required = "core.manage_shop"

    def get_success_url(self):
        search_query = self.request.POST.get("q", "")
        url = reverse_lazy("lfs_manage_tax", kwargs={"pk": self.object.id})
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
        context["came_from"] = self.request.POST.get("came_from", reverse("lfs_manage_taxes"))
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Tax has been added."))
        # Always redirect to the created tax to avoid blank HTMX renders
        return HttpResponseRedirect(self.get_success_url())


class TaxDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a tax."""

    template_name = "manage/product_taxes/delete_tax.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tax"] = get_object_or_404(Tax, pk=self.kwargs["pk"])
        return context


class TaxDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes the tax with passed id."""

    model = Tax
    permission_required = "core.manage_shop"
    success_message = _("Tax has been deleted.")

    def get_success_url(self):
        """Return the URL to redirect to after successful deletion."""
        # Find next tax to redirect to
        first_tax = Tax.objects.exclude(pk=self.object.pk).first()
        if first_tax:
            return reverse("lfs_manage_tax", kwargs={"pk": first_tax.id})
        else:
            return reverse("lfs_no_taxes")

    def delete(self, request, *args, **kwargs):
        """Override delete to clean up references before deletion."""
        tax = self.get_object()

        # Remove the tax from all products
        for product in Product.objects.filter(tax=tax):
            product.tax = None
            product.save()

        return super().delete(request, *args, **kwargs)
