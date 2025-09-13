from typing import Dict, List, Tuple, Any, Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, TemplateView

import lfs.core.utils
from lfs.core.models import Shop
from lfs.core.signals import shop_changed
from lfs.core.utils import import_symbol
from lfs.manage.portlets.views import PortletsInlineView
from lfs.manage.seo.views import SEOView
from lfs.manage.shop.forms import ShopDataForm, ShopDefaultValuesForm


class ShopSEOView(SEOView):
    """SEO view for Shop with signal handling."""

    def form_valid(self, form):
        res = super().form_valid(form)
        shop_changed.send(form.instance)
        return res


class ShopTabMixin:
    """Mixin for tab navigation in Shop views."""

    template_name = "manage/shop/shop.html"
    tab_name: Optional[str] = None

    def get_shop(self) -> Shop:
        """Gets the Shop object."""
        return lfs.core.utils.get_default_shop()

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with tab navigation and Shop."""
        ctx = super().get_context_data(**kwargs)
        shop = getattr(self, "object", None) or self.get_shop()

        ctx.update(
            {
                "shop": shop,
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(shop),
            }
        )
        return ctx

    def _get_tabs(self, shop: Shop) -> List[Tuple[str, str]]:
        """Creates tab navigation URLs."""
        tabs = [
            ("data", reverse("lfs_manage_shop_data")),
            ("default_values", reverse("lfs_manage_shop_default_values")),
            ("order_numbers", reverse("lfs_manage_shop_order_numbers")),
            ("seo", reverse("lfs_manage_shop_seo")),
            ("portlets", reverse("lfs_manage_shop_portlets")),
        ]
        return tabs


class ShopDataView(PermissionRequiredMixin, ShopTabMixin, UpdateView):
    """View for data tab of Shop."""

    model = Shop
    form_class = ShopDataForm
    tab_name = "data"
    permission_required = "core.manage_shop"

    def get_object(self, queryset=None):
        """Returns the default shop."""
        return self.get_shop()

    def get_success_url(self) -> str:
        """Stays on the data tab after successful save."""
        return reverse("lfs_manage_shop_data")

    def form_valid(self, form):
        """Saves and shows success message."""
        # Handle image deletion if checkbox is checked
        if self.request.POST.get("delete_image"):
            shop = self.get_object()
            if shop.image:
                shop.image.delete()

        response = super().form_valid(form)
        shop_changed.send(self.object)
        messages.success(self.request, _("Shop data has been saved."))
        return response


class ShopDefaultValuesView(PermissionRequiredMixin, ShopTabMixin, UpdateView):
    """View for default values tab of Shop."""

    model = Shop
    form_class = ShopDefaultValuesForm
    tab_name = "default_values"
    permission_required = "core.manage_shop"

    def get_object(self, queryset=None):
        """Returns the default shop."""
        return self.get_shop()

    def get_success_url(self) -> str:
        """Stays on the default values tab after successful save."""
        return reverse("lfs_manage_shop_default_values")

    def form_valid(self, form):
        """Saves and shows success message."""
        response = super().form_valid(form)
        shop_changed.send(self.object)
        messages.success(self.request, _("Shop default values have been saved."))
        return response


class ShopOrderNumbersView(PermissionRequiredMixin, ShopTabMixin, TemplateView):
    """View for order numbers tab of Shop."""

    tab_name = "order_numbers"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with order numbers form."""
        ctx = super().get_context_data(**kwargs)
        shop = self.get_shop()

        ong = import_symbol(settings.LFS_ORDER_NUMBER_GENERATOR)
        try:
            order_number = ong.objects.get(id="order_number")
        except ong.DoesNotExist:
            order_number = ong.objects.create(id="order_number")

        form = order_number.get_form(instance=order_number)
        ctx["order_numbers_form"] = form
        return ctx

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles order numbers form submission."""
        shop = self.get_shop()

        ong = import_symbol(settings.LFS_ORDER_NUMBER_GENERATOR)
        order_number = ong.objects.get(id="order_number")
        form = order_number.get_form(instance=order_number, data=request.POST)

        if form.is_valid():
            form.save()
            shop_changed.send(shop)
            messages.success(request, _("Order numbers have been saved."))
        else:
            messages.error(request, _("Please correct the indicated errors."))

        return HttpResponseRedirect(reverse("lfs_manage_shop_order_numbers"))


class ShopSEOTabView(PermissionRequiredMixin, ShopTabMixin, UpdateView):
    """View for SEO tab of Shop."""

    model = Shop
    fields = ["meta_title", "meta_description", "meta_keywords"]
    tab_name = "seo"
    permission_required = "core.manage_shop"

    def get_object(self, queryset=None):
        """Returns the default shop."""
        return self.get_shop()

    def get_success_url(self) -> str:
        """Stays on the SEO tab after successful save."""
        return reverse("lfs_manage_shop_seo")

    def form_valid(self, form):
        """Saves and shows success message."""
        response = super().form_valid(form)
        shop_changed.send(self.object)
        messages.success(self.request, _("SEO data has been saved."))
        return response


class ShopPortletsView(PermissionRequiredMixin, ShopTabMixin, TemplateView):
    """View for portlets tab of Shop."""

    tab_name = "portlets"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with portlets."""
        ctx = super().get_context_data(**kwargs)
        shop = self.get_shop()
        ctx["portlets"] = PortletsInlineView().get(self.request, shop)
        return ctx
