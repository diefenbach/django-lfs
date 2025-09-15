from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView

import lfs.caching.utils
import lfs.core.utils
import lfs.catalog.models
import lfs.marketing.utils


class ToolsView(PermissionRequiredMixin, TemplateView):
    """Main tools view displaying available utility functions."""

    template_name = "manage/tools/tools.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["utilities"] = [
            {
                "name": _("Clear Cache"),
                "description": _("Clears the whole cache"),
                "url": reverse("lfs_clear_cache"),
                "icon": "bi-arrow-clockwise",
            },
            {
                "name": _("Set Category Levels"),
                "description": _("Sets the category levels based on the position in category hierarchy"),
                "url": reverse("lfs_set_category_levels"),
                "icon": "bi-diagram-3",
            },
            {
                "name": _("Reindex Topseller"),
                "description": _("Clears and reindexes the topsellers"),
                "url": reverse("lfs_reindex_topseller"),
                "icon": "bi-star",
            },
            {
                "name": _("Update Effective Prices"),
                "description": _("Saves the price or sale price to effective price"),
                "url": reverse("lfs_update_effective_price"),
                "icon": "bi-currency-dollar",
            },
        ]
        return context


@permission_required("core.manage_shop")
def reindex_topseller(request):
    """Clears and reindexes the topsellers."""
    lfs.marketing.utils.calculate_product_sales()
    messages.success(request, _("Topseller have been reindexed."))
    return HttpResponseRedirect(reverse("lfs_manage_tools"))


@permission_required("core.manage_shop")
def clear_cache(request):
    """Clears the whole cache."""
    lfs.caching.utils.clear_cache()
    messages.success(request, _("Cache has been cleared."))
    return HttpResponseRedirect(reverse("lfs_manage_tools"))


@permission_required("core.manage_shop")
def set_category_levels(request):
    """Sets the category levels based on the position in category hierarchy."""
    lfs.core.utils.set_category_levels()
    messages.success(request, _("Category levels have been created."))
    return HttpResponseRedirect(reverse("lfs_manage_tools"))


@permission_required("core.manage_shop")
def update_effective_price(request):
    """Saves the price or sale price to effective price."""
    for product in lfs.catalog.models.Product.objects.all():
        product.save()

    messages.success(request, _("Effective prices have been set."))
    return HttpResponseRedirect(reverse("lfs_manage_tools"))
