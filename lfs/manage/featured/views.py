from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Q
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView

from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category, Product
from lfs.catalog.settings import VARIANT
from lfs.marketing.models import FeaturedProduct


class ManageFeaturedView(PermissionRequiredMixin, TemplateView):
    """Main view for managing featured products with two-column layout."""

    template_name = "manage/featured/featured.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get featured products
        featured = FeaturedProduct.objects.all().order_by("position")
        featured_ids = [f.product.id for f in featured]

        # Get filter parameters
        r = self.request.POST if self.request.method == "POST" else self.request.GET
        s = self.request.session

        # Handle filters and pagination
        if r.get("keep-filters") or r.get("page"):
            page = r.get("page", s.get("featured_products_page", 1))
            filter_ = r.get("filter", s.get("filter"))
            category_filter = r.get("featured_category_filter", s.get("featured_category_filter"))
        else:
            page = r.get("page", 1)
            filter_ = r.get("filter")
            category_filter = r.get("featured_category_filter")

        # Save current filters in session
        s["featured_products_page"] = page
        s["filter"] = filter_
        s["featured_category_filter"] = category_filter

        try:
            s["featured-amount"] = int(r.get("featured-amount", s.get("featured-amount")))
        except TypeError:
            s["featured-amount"] = 25

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

        # Get products (excluding already featured ones)
        products = Product.objects.filter(filters).exclude(pk__in=featured_ids)
        paginator = Paginator(products, s["featured-amount"])

        total = products.count()
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = 0

        # Amount options for pagination
        amount_options = []
        for value in (10, 25, 50, 100):
            amount_options.append({"value": value, "selected": value == s.get("featured-amount")})

        # Get all categories for filter dropdown
        categories = Category.objects.all().order_by("name")

        context.update(
            {
                "featured": featured,
                "total": total,
                "page": page_obj,
                "paginator": paginator,
                "filter": filter_,
                "category_filter": category_filter,
                "amount_options": amount_options,
                "categories": categories,
            }
        )

        return context


def add_featured(request):
    """Adds featured products by given ids (within request body)."""
    for temp_id in request.POST.keys():
        if temp_id.startswith("product") is False:
            continue

        temp_id = temp_id.split("-")[1]
        FeaturedProduct.objects.create(product_id=temp_id)

    _update_positions()

    # Render ManageFeaturedView
    view = ManageFeaturedView()
    view.request = request
    context = view.get_context_data()

    return render(
        request,
        "manage/featured/featured.html",
        context=context,
    )


def update_featured(request):
    """Saves or removes passed featured product passed id (within request body)."""
    if request.POST.get("action") == "remove":
        for temp_id in request.POST.keys():
            if not temp_id.startswith("product"):
                continue

            temp_id = temp_id.split("-")[1]
            try:
                featured = FeaturedProduct.objects.get(pk=temp_id)
                featured.delete()
            except (FeaturedProduct.DoesNotExist, ValueError):
                pass

        _update_positions()

    else:
        for temp_id in request.POST.keys():
            if temp_id.startswith("position") is False:
                continue

            temp_id = temp_id.split("-")[1]
            featured = FeaturedProduct.objects.get(pk=temp_id)

            # Update position
            position = request.POST.get("position-%s" % temp_id)
            featured.position = position
            featured.save()

        _update_positions()

    # Render ManageFeaturedView
    view = ManageFeaturedView()
    view.request = request
    context = view.get_context_data()

    return render(
        request,
        "manage/featured/featured.html",
        context=context,
    )


def _update_positions():
    """Update positions of featured products."""
    for i, featured in enumerate(FeaturedProduct.objects.all()):
        featured.position = (i + 1) * 10
        featured.save()
