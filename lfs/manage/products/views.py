from typing import Any, Dict, List, Optional, Tuple

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView, TemplateView, UpdateView, CreateView, DeleteView, FormView

from lfs.catalog.models import (
    Product,
    Category,
    Image,
    ProductAttachment,
    Property,
    PropertyGroup,
    PropertyOption,
    ProductPropertyValue,
    ProductsPropertiesRelation,
)
from lfs.catalog.settings import VARIANT as PRODUCT_VARIANT
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_VARIANT, PROPERTY_VALUE_TYPE_FILTER, PROPERTY_SELECT_FIELD
from lfs.catalog.settings import (
    PROPERTY_NUMBER_FIELD,
    PROPERTY_TEXT_FIELD,
    PROPERTY_VALUE_TYPE_DEFAULT,
    PROPERTY_VALUE_TYPE_DISPLAY,
)
from lfs.manage.portlets.views import PortletsInlineView
from lfs.manage.mixins import DirectDeleteMixin
from lfs.manage.products.services import ProductFilterService, ProductDataService

from .forms import (
    ProductFilterForm,
    CategoryVariantForm,
    DefaultVariantForm,
    DisplayTypeForm,
    ProductAddForm,
    ProductDataForm,
    ProductStockForm,
    ProductVariantCreateForm,
    SEOForm,
    VariantDataForm,
)
from lfs.core.signals import category_changed, product_changed
from lfs.core.utils import atof
from lfs.manage import utils as manage_utils
from lfs.caching.listeners import update_product_cache
from lfs.core.signals import product_removed_property_group


class ProductListView(PermissionRequiredMixin, TemplateView):
    """Shows a table view of all products with filtering and pagination."""

    permission_required = "core.manage_shop"
    template_name = "manage/products/product_list.html"

    def get_context_data(self, **kwargs):
        """Extends context with products and filter form."""
        from django.core.paginator import Paginator
        from django.db.models import Q
        from lfs.catalog.settings import VARIANT as PRODUCT_VARIANT, PRODUCT_TYPE_LOOKUP

        ctx = super().get_context_data(**kwargs)

        # Initialize services
        filter_service = ProductFilterService()
        data_service = ProductDataService()

        # Get filters from session
        product_filters = self.request.session.get("product-filters", {})

        # Filter products
        try:
            queryset = Product.objects.exclude(sub_type=PRODUCT_VARIANT).order_by("-creation_date")
            filtered_products = filter_service.filter_products(queryset, product_filters)
        except Exception:
            filtered_products = Product.objects.none()

        # Paginate products
        paginator = Paginator(filtered_products, 22)
        page_number = self.request.GET.get("page", 1)
        products_page = paginator.get_page(page_number)

        # Enrich products with data
        products_with_data = []
        for product in products_page:
            product_data = {
                "product": product,
                "categories": ", ".join([cat.name for cat in product.categories.all()[:3]]),
                "price": product.get_price(None),  # Get price for anonymous user
                "stock": product.stock_amount if product.manage_stock_amount else None,
                "active": product.active,
                "sub_type_display": PRODUCT_TYPE_LOOKUP.get(product.sub_type, product.sub_type),
            }
            products_with_data.append(product_data)

        # Prepare filter form
        try:
            filter_form = ProductFilterForm(
                initial={
                    "name": product_filters.get("name", ""),
                    "sku": product_filters.get("sku", ""),
                    "sub_type": product_filters.get("sub_type", ""),
                    "price_calculator": product_filters.get("price_calculator", ""),
                    "status": product_filters.get("status", ""),
                }
            )
        except Exception:
            filter_form = ProductFilterForm()

        ctx.update(
            {
                "products_page": products_page,
                "products_with_data": products_with_data,
                "product_filters": product_filters,
                "filter_form": filter_form,
            }
        )
        return ctx


class ManageProductsView(PermissionRequiredMixin, RedirectView):
    """Redirect to the first product's data tab or to the 'no products' page."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        from lfs.catalog.settings import VARIANT as PRODUCT_VARIANT

        p = Product.objects.exclude(sub_type=PRODUCT_VARIANT).order_by("name").first()
        if p is not None:
            return reverse("lfs_manage_product_data", kwargs={"id": p.id})
        return reverse("lfs_manage_no_products")


class ProductCreateView(PermissionRequiredMixin, CreateView):
    """View for adding a new product."""

    model = Product
    form_class = ProductAddForm
    template_name = "manage/products/add_product.html"
    permission_required = "core.manage_shop"

    def form_valid(self, form):
        """Saves the product and redirects."""
        product = form.save()
        messages.success(self.request, _("Product has been added."))
        return HttpResponseRedirect(reverse("lfs_manage_product_data", kwargs={"id": product.id}))


class ProductTabMixin:
    """Mixin for tab navigation in Product views (Bootstrap shell)."""

    template_name = "manage/products/product.html"
    tab_name: Optional[str] = None

    def get_product(self) -> Product:
        return get_object_or_404(Product, pk=self.kwargs["id"])

    def _get_tabs(self, product: Product) -> List[Tuple[str, str]]:
        # Get search query parameter to preserve it in tab URLs
        search_query = self.request.GET.get("q", "").strip()
        query_param = f"?q={search_query}" if search_query else ""

        tabs: List[Tuple[str, str]] = [
            ("data", reverse("lfs_manage_product_data", args=[product.pk]) + query_param),
            ("images", reverse("lfs_manage_product_images", args=[product.pk]) + query_param),
            ("attachments", reverse("lfs_manage_product_attachments", args=[product.pk]) + query_param),
        ]

        # Only include categories tab for non-variant products
        if product.sub_type != PRODUCT_VARIANT:
            tabs.insert(1, ("categories", reverse("lfs_manage_product_categories", args=[product.pk]) + query_param))
        if product.is_product_with_variants():
            tabs.append(("variants", reverse("lfs_manage_product_variants", args=[product.pk]) + query_param))
        tabs.extend(
            [
                ("properties", reverse("lfs_manage_product_properties", args=[product.pk]) + query_param),
                ("accessories", reverse("lfs_manage_product_accessories", args=[product.pk]) + query_param),
                ("related", reverse("lfs_manage_product_related", args=[product.pk]) + query_param),
            ]
        )

        # Only show bulk prices tab if price calculator is set to bulk prices
        if product.price_calculator == "lfs_bulk_prices.calculator.BulkPricesCalculator":
            tabs.append(("bulk_prices", reverse("lfs_manage_product_bulk_prices", args=[product.pk]) + query_param))

        tabs.extend(
            [
                ("stock", reverse("lfs_manage_product_stock", args=[product.pk]) + query_param),
                ("seo", reverse("lfs_manage_product_seo", args=[product.pk]) + query_param),
                ("portlets", reverse("lfs_manage_product_portlets", args=[product.pk]) + query_param),
            ]
        )
        return tabs

    def _get_products_queryset(self):
        q = self.request.GET.get("q", "").strip()
        # Get all non-variant products (standard, product_with_variants, configurable)
        # Prefetch variants to avoid N+1 queries
        qs = Product.objects.exclude(sub_type=PRODUCT_VARIANT).prefetch_related("variants").order_by("name")
        if q:
            from django.db.models import Q

            qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))
        return qs

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        product = getattr(self, "object", None) or self.get_product()
        ctx.update(
            {
                "product": product,
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(product),
                "products": self._get_products_queryset(),
                "search_query": self.request.GET.get("q", ""),
            }
        )
        return ctx


class ProductDataView(PermissionRequiredMixin, ProductTabMixin, UpdateView):
    """Data tab for a Product (uses correct form for product/variant)."""

    model = Product
    tab_name = "data"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_form_class(self):
        obj = self.get_object()
        is_variant = (obj.sub_type == PRODUCT_VARIANT) if hasattr(obj, "sub_type") else obj.is_variant()
        return VariantDataForm if is_variant else ProductDataForm

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Product data has been saved."))
        return response

    def get_success_url(self) -> str:
        return reverse("lfs_manage_product_data", kwargs={"id": self.object.pk})

    def delete(self, request, *args, **kwargs):
        """Handle product deletion via POST request."""
        product = self.get_object()
        url = reverse("lfs_manage_products")  # Redirect to products overview
        if product.is_variant():
            url = reverse("lfs_manage_product_data", kwargs={"id": product.parent_id})

        product.delete()
        messages.success(request, _("Product has been deleted."))
        return HttpResponseRedirect(url)

    def get(self, request, *args, **kwargs):
        """Handle GET requests - support viewing product by redirecting to public page."""
        if "view" in request.GET:
            product = self.get_object()
            url = reverse("lfs_product", kwargs={"slug": product.slug})
            return HttpResponseRedirect(url)
        return super().get(request, *args, **kwargs)


class ProductStockView(PermissionRequiredMixin, ProductTabMixin, UpdateView):
    """Stock tab for a Product."""

    model = Product
    form_class = ProductStockForm
    tab_name = "stock"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # keep legacy prefix behavior used by ProductStockForm
        kwargs["prefix"] = "stock"
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Product stock data has been saved."))
        return response

    def get_success_url(self) -> str:
        return reverse("lfs_manage_product_stock", kwargs={"id": self.object.pk})


class ProductSEOView(PermissionRequiredMixin, ProductTabMixin, UpdateView):
    """SEO tab for a Product."""

    model = Product
    form_class = SEOForm
    tab_name = "seo"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("SEO data has been saved."))
        return response

    def get_success_url(self) -> str:
        return reverse("lfs_manage_product_seo", kwargs={"id": self.object.pk})


class ProductPortletsView(PermissionRequiredMixin, ProductTabMixin, TemplateView):
    """Portlets tab for a Product."""

    tab_name = "portlets"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        product = self.get_product()
        ctx["portlets"] = PortletsInlineView().get(self.request, product)
        return ctx


class NoProductsView(PermissionRequiredMixin, TemplateView):
    template_name = "manage/products/no_products.html"
    permission_required = "core.manage_shop"


class ProductCategoriesView(PermissionRequiredMixin, ProductTabMixin, TemplateView):
    """Categories tab for a Product (checkbox tree + save)."""

    tab_name = "categories"
    permission_required = "core.manage_shop"

    def _build_tree(self, selected_ids):
        def build(node: Category):
            children_qs = Category.objects.filter(parent=node).order_by("position", "name")
            return {
                "id": node.id,
                "name": node.name,
                "checked": node.id in selected_ids,
                "children": [build(c) for c in children_qs],
            }

        roots = Category.objects.filter(parent=None).order_by("position", "name")
        return [build(r) for r in roots]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        product = self.get_product()

        # signal that old categories changed
        for c in product.categories.all():
            category_changed.send(c)

        selected = request.POST.getlist("categories")
        product.categories.set(selected)
        product.save()

        # signal that new categories changed
        for c in product.categories.all():
            category_changed.send(c)

        messages.success(self.request, _("Categories have been saved."))
        return self.get(self.request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        product = self.get_product()
        selected_ids = list(product.get_categories().values_list("id", flat=True))
        ctx["category_tree"] = self._build_tree(selected_ids)
        return ctx


class ProductImagesView(PermissionRequiredMixin, ProductTabMixin, TemplateView):
    """Images tab for a Product (upload + list + edit)."""

    tab_name = "images"
    permission_required = "core.manage_shop"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        product = self.get_product()

        if "toggle_active_images" in request.POST:
            product.active_images = bool(request.POST.get("active_images"))
            product.save()
            product_changed.send(product, request=request)
            messages.success(self.request, _("Active images has been updated."))
            return self.get(request, *args, **kwargs)

        if request.FILES.getlist("files[]"):
            for file_content in request.FILES.getlist("files[]"):
                img = Image(content=product, title=file_content.name)
                img.image.save(file_content.name, file_content, save=True)

            # Refresh positions
            for i, image in enumerate(product.images.all()):
                image.position = (i + 1) * 10
                image.save()

            product_changed.send(product, request=request)
            messages.success(self.request, _("Images have been added."))
            return self.get(request, *args, **kwargs)

        # Update/delete
        action = request.POST.get("action")
        if action == "delete":
            deleted = 0
            for key in request.POST.keys():
                if key.startswith("delete-"):
                    img_id = key.split("-", 1)[1]
                    try:
                        Image.objects.get(pk=img_id).delete()
                        deleted += 1
                    except Image.DoesNotExist:
                        pass
            if deleted:
                messages.success(self.request, _("Images have been deleted."))
        elif action == "update":
            for key, value in request.POST.items():
                if key.startswith("title-") or key.startswith("alt-") or key.startswith("position-"):
                    field, img_id = key.split("-", 1)
                    try:
                        img = Image.objects.get(pk=img_id)
                    except Image.DoesNotExist:
                        continue
                    if field == "title":
                        img.title = value
                    elif field == "alt":
                        img.alt = value
                    elif field == "position":
                        img.position = value
                    img.save()
            # Refresh positions
            for i, image in enumerate(product.images.all()):
                image.position = (i + 1) * 10
                image.save()
            product_changed.send(product, request=request)
            messages.success(self.request, _("Images have been updated."))

        return self.get(request, *args, **kwargs)


class ProductAttachmentsView(PermissionRequiredMixin, ProductTabMixin, TemplateView):
    """Attachments tab for a Product (upload + list + edit)."""

    tab_name = "attachments"
    permission_required = "core.manage_shop"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        product = self.get_product()

        if request.FILES.getlist("files[]"):
            for file_content in request.FILES.getlist("files[]"):
                att = ProductAttachment(product=product, title=file_content.name[:50])
                att.file.save(file_content.name, file_content, save=True)
            # Refresh positions
            for i, a in enumerate(product.attachments.all()):
                a.position = (i + 1) * 10
                a.save()
            product_changed.send(product, request=request)
            messages.success(self.request, _("Attachments have been added."))
            return self.get(request, *args, **kwargs)

        action = request.POST.get("action")
        if action == "delete":
            deleted = 0
            for key in request.POST.keys():
                if key.startswith("delete-"):
                    att_id = key.split("-", 1)[1]
                    try:
                        ProductAttachment.objects.get(pk=att_id).delete()
                        deleted += 1
                    except ProductAttachment.DoesNotExist:
                        pass
            if deleted:
                messages.success(self.request, _("Attachment has been deleted."))
        elif action == "update":
            for att in product.attachments.all():
                att.title = request.POST.get(f"title-{att.id}", att.title)[:50]
                att.position = request.POST.get(f"position-{att.id}", att.position)
                att.description = request.POST.get(f"description-{att.id}", att.description)
                att.save()
            # Refresh positions
            for i, a in enumerate(product.attachments.all()):
                a.position = (i + 1) * 10
                a.save()
            product_changed.send(product, request=request)
            messages.success(self.request, _("Attachment has been updated."))

        return self.get(request, *args, **kwargs)


class ProductBulkPricesView(PermissionRequiredMixin, ProductTabMixin, TemplateView):
    """Bulk prices tab (Bootstrap, non-AJAX)."""

    tab_name = "bulk_prices"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        from lfs_bulk_prices.models import BulkPrice
        from django.conf import settings

        ctx = super().get_context_data(**kwargs)
        product = self.get_product()
        prices = list(BulkPrice.objects.filter(product=product).order_by("amount"))
        ctx.update(
            {
                "prices": prices,
                "currency": getattr(settings, "LFS_CURRENCY", "EUR"),
            }
        )
        return ctx

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        from django.utils.formats import sanitize_separators
        from django.db import IntegrityError
        from lfs_bulk_prices.models import BulkPrice

        product = self.get_product()

        # delete all bulk prices then re-create from POST (mirrors plugin)
        BulkPrice.objects.filter(product=product).delete()

        message = None
        for price_id in request.POST.getlist("price_id"):
            try:
                amount = float(sanitize_separators(request.POST.get(f"amount-{price_id}")))
            except (TypeError, ValueError):
                amount = 1.0

            try:
                price_absolute = float(sanitize_separators(request.POST.get(f"price_absolute-{price_id}")))
            except (TypeError, ValueError):
                price_absolute = 0.0

            try:
                price_percentual = float(sanitize_separators(request.POST.get(f"price_percentual-{price_id}")))
            except (TypeError, ValueError):
                price_percentual = 0.0

            try:
                BulkPrice.objects.create(
                    product_id=product.id,
                    amount=amount,
                    price_absolute=price_absolute,
                    price_percentual=price_percentual,
                )
            except IntegrityError:
                message = _("Duplicated prices have been removed.")

        if message:
            messages.info(self.request, message)
        messages.success(self.request, _("Bulk prices have been saved."))
        return HttpResponseRedirect(reverse("lfs_manage_product_bulk_prices", kwargs={"id": product.pk}))


class ProductVariantsView(PermissionRequiredMixin, ProductTabMixin, TemplateView):
    """"""

    tab_name = "variants"
    permission_required = "core.manage_shop"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        product = self.get_product()
        action = request.POST.get("action")

        if action == "delete":
            # delete selected variants
            to_delete = []
            for key in request.POST.keys():
                if key.startswith("delete-"):
                    try:
                        to_delete.append(int(key.split("-", 1)[1]))
                    except Exception:
                        pass
            for vid in to_delete:
                try:
                    v = Product.objects.get(pk=vid)
                except Product.DoesNotExist:
                    continue
                if product.default_variant_id == v.id:
                    product.default_variant = None
                    product.save()
                v.delete()
            messages.success(self.request, _("Variants have been deleted."))
            return self.get(request, *args, **kwargs)

        if action == "update":
            # update variants
            for key in request.POST.keys():
                if key.startswith("variant-"):
                    try:
                        vid = int(key.split("-", 1)[1])
                    except Exception:
                        continue
                    try:
                        variant = Product.objects.get(pk=vid)
                    except Product.DoesNotExist:
                        continue

                    # fields
                    slug = request.POST.get(f"slug-{vid}")
                    if slug is not None and variant.slug != slug:
                        # ensure unique slug similar to legacy
                        base_slug = slug[:80]
                        new_slug = base_slug
                        counter = 1
                        while Product.objects.exclude(pk=variant.pk).filter(slug=new_slug).exists():
                            new_slug = f"{base_slug[: (79 - len(str(counter)))]}-{counter}"
                            counter += 1
                        variant.slug = new_slug

                    name = request.POST.get(f"name-{vid}")
                    if name is not None:
                        variant.name = name

                    sku = request.POST.get(f"sku-{vid}")
                    if sku is not None:
                        variant.sku = sku

                    variant.active = bool(request.POST.get(f"active-{vid}"))
                    variant.active_price = bool(request.POST.get(f"active_price-{vid}"))
                    variant.active_sku = bool(request.POST.get(f"active_sku-{vid}"))
                    variant.active_name = bool(request.POST.get(f"active_name-{vid}"))

                    pos = request.POST.get(f"position-{vid}")
                    try:
                        variant.variant_position = int(pos)
                    except (TypeError, ValueError):
                        pass

                    price_val = request.POST.get(f"price-{vid}")
                    if price_val is not None:
                        try:
                            variant.price = abs(atof(str(price_val)))
                        except (TypeError, ValueError):
                            variant.price = 0.0

                    variant.save()

            # default variant
            dv = request.POST.get("default_variant")
            if dv:
                try:
                    product.default_variant_id = int(dv)
                    product.save()
                except (TypeError, ValueError):
                    pass

            # update property values for variants
            for key, value in request.POST.items():
                if key.startswith("property-"):
                    try:
                        temp = key.split("-", 1)[1]
                        variant_id, property_group_id, property_id = temp.split("|")
                        variant_id = int(variant_id)
                        property_id = int(property_id)
                    except Exception:
                        continue
                    property_group_id = None if property_group_id == "0" else property_group_id

                    try:
                        variant = Product.objects.get(pk=variant_id)
                    except Product.DoesNotExist:
                        continue

                    try:
                        prop = Property.objects.get(pk=property_id)
                    except Property.DoesNotExist:
                        continue

                    try:
                        ppv = ProductPropertyValue.objects.get(
                            product=variant,
                            property_id=property_id,
                            property_group_id=property_group_id,
                            type=PROPERTY_VALUE_TYPE_VARIANT,
                        )
                    except ProductPropertyValue.DoesNotExist:
                        ppv = None

                    if prop.filterable:
                        ppv_filterables = ProductPropertyValue.objects.filter(
                            product=variant,
                            property_group_id=property_group_id,
                            property_id=property_id,
                            type=PROPERTY_VALUE_TYPE_FILTER,
                        )
                    else:
                        ppv_filterables = ProductPropertyValue.objects.none()

                    if value != "":
                        is_changed = True
                        if not ppv:
                            ppv = ProductPropertyValue.objects.create(
                                product=variant,
                                property_group_id=property_group_id,
                                property_id=property_id,
                                type=PROPERTY_VALUE_TYPE_VARIANT,
                                value=value,
                            )
                        else:
                            is_changed = ppv.value != value
                            ppv.value = value
                            ppv.save()

                        if prop.filterable and is_changed:
                            ppv_filterables.delete()
                            ProductPropertyValue.objects.create(
                                product=variant,
                                property_group_id=property_group_id,
                                property_id=property_id,
                                value=value,
                                type=PROPERTY_VALUE_TYPE_FILTER,
                            )
                    elif ppv:
                        # clear
                        ppv.delete()
                        ppv_filterables.delete()

            # normalize positions
            for i, variant in enumerate(product.variants.order_by("variant_position", "pk")):
                variant.variant_position = (i + 1) * 10
                variant.save()

            product_changed.send(product)
            messages.success(self.request, _("Variants have been saved."))
            return self.get(request, *args, **kwargs)

        if action == "edit_sub_type":
            form = DisplayTypeForm(instance=product, data=request.POST)
            if form.is_valid():
                product.variants_display_type = form.cleaned_data.get(
                    "variants_display_type", product.variants_display_type
                )
                product.save()
                product_changed.send(product)
                messages.success(self.request, _("Sub type has been saved."))
            return self.get(request, *args, **kwargs)

        if action == "update_category_variant":
            form = CategoryVariantForm(instance=product, data=request.POST)
            if form.is_valid():
                form.save()
                product_changed.send(product)
                messages.success(self.request, _("Category variant has been saved."))
            return self.get(request, *args, **kwargs)

        if action == "update_property_groups":
            selected_group_ids = request.POST.getlist("selected-property-groups")
            # assign/remove m2m
            for pg in PropertyGroup.objects.all():
                if str(pg.id) in selected_group_ids:
                    if not pg.products.filter(pk=product.pk).exists():
                        pg.products.add(product.pk)
                else:
                    if pg.products.filter(pk=product.pk).exists():
                        pg.products.remove(product.pk)
                        product_removed_property_group.send(sender=pg, product=product)
            update_product_cache(product)
            messages.success(self.request, _("Property groups have been updated."))
            return self.get(request, *args, **kwargs)

        if action == "add_variants":
            # Build cartesian set from selected property options
            all_properties = product.get_variants_properties()
            properties = []
            for pd in all_properties:
                prop = pd["property"]
                pg = pd["property_group"]
                pg_id = pg.pk if pg else 0
                key = f"property_{pg_id}_{prop.id}"
                val = request.POST.get(key)
                if val == "all":
                    tmp = []
                    for option in PropertyOption.objects.filter(property=prop.id):
                        tmp.append(f"{pg_id}|{prop.id}|{option.id}")
                    properties.append(tmp)
                elif val in (None, ""):
                    continue
                else:
                    properties.append([f"{pg_id}|{prop.id}|{val}"])

            added_count = 0
            variants_count = product.variants.count()
            for i, options in enumerate(manage_utils.cartesian_product(*properties)) if properties else []:
                # skip if variant already exists (legacy check)
                if getattr(product, "has_variant", None) and product.has_variant(options, only_active=False):
                    continue
                pvcf = ProductVariantCreateForm(options=options, product=product, data=request.POST)
                if pvcf.is_valid():
                    variant = pvcf.save(commit=False)
                    variant.price = product.price
                    variant.sku = f"{product.sku}-{variants_count + i + 1}"
                    variant.parent = product
                    variant.variant_position = (variants_count + i + 1) * 10
                    variant.sub_type = PRODUCT_VARIANT
                    try:
                        variant.save()
                    except Exception:
                        continue
                    added_count += 1
                    for pg in product.property_groups.all():
                        variant.property_groups.add(pg)
                    for item in options:
                        pg_id, prop_id, opt_id = item.split("|")
                        pg_id = None if pg_id == "0" else pg_id
                        ProductPropertyValue.objects.create(
                            product=variant,
                            property_group_id=pg_id,
                            property_id=prop_id,
                            value=opt_id,
                            type=PROPERTY_VALUE_TYPE_VARIANT,
                        )
                        if Property.objects.get(pk=prop_id).filterable:
                            ProductPropertyValue.objects.create(
                                product=variant,
                                property_group_id=pg_id,
                                property_id=prop_id,
                                value=opt_id,
                                type=PROPERTY_VALUE_TYPE_FILTER,
                            )
            product_changed.send(product)
            if added_count:
                messages.success(self.request, _("Variants have been added."))
            else:
                messages.info(self.request, _("No variants have been added."))
            return self.get(request, *args, **kwargs)

        if action == "add_local_property":
            name = (request.POST.get("name") or "").strip()
            if name:
                prop = Property(name=name, title=name, type=PROPERTY_SELECT_FIELD)
                prop.local = True
                prop.filterable = False
                prop.save()
                ppr = ProductsPropertiesRelation(product=product, property=prop, position=999)
                ppr.save()
                # refresh positions
                for i, ppr in enumerate(product.productsproperties.all()):
                    ppr.position = i
                    ppr.save()
                product_changed.send(product)
                messages.success(self.request, _("Property has been added."))
            else:
                messages.error(self.request, _("Invalid data. Correct it and try again."))
            return self.get(request, *args, **kwargs)

        if action == "delete_local_property":
            try:
                prop_id = int(request.POST.get("property_id"))
                prop = Property.objects.get(pk=prop_id)
                prop.delete()
                product_changed.send(product)
                messages.success(self.request, _("Property has been deleted."))
            except Exception:
                messages.error(self.request, _("Invalid property."))
            return self.get(request, *args, **kwargs)

        if action == "add_local_property_option":
            prop_id = request.POST.get("property_id")
            names = (request.POST.get("option_names") or "").strip()
            if not prop_id or not names:
                messages.error(self.request, _("Invalid data. Correct it and try again."))
                return self.get(request, *args, **kwargs)
            position = 999
            for name in [x.strip() for x in names.split(",") if x.strip()]:
                po = PropertyOption(name=name, property_id=prop_id, position=position)
                po.save()
                position += 1
            # normalize positions
            for i, opt in enumerate(PropertyOption.objects.filter(property=prop_id).order_by("position", "pk")):
                opt.position = i
                opt.save()
            product_changed.send(product)
            messages.success(self.request, _("Option has been added."))
            return self.get(request, *args, **kwargs)

        if action == "delete_local_property_option":
            try:
                option_id = int(request.POST.get("option_id"))
                PropertyOption.objects.get(pk=option_id).delete()
                product_changed.send(product)
                messages.success(self.request, _("Property has been deleted."))
            except Exception:
                messages.error(self.request, _("Invalid option."))
            return self.get(request, *args, **kwargs)

        if action == "move_local_property":
            prop_id = request.POST.get("property_id")
            direction = request.POST.get("direction")
            try:
                ppr = ProductsPropertiesRelation.objects.get(product=product, property_id=prop_id)
                if direction == "up":
                    ppr.position = (ppr.position or 0) - 3
                else:
                    ppr.position = (ppr.position or 0) + 3
                ppr.save()
                # normalize
                for i, rel in enumerate(
                    ProductsPropertiesRelation.objects.filter(product=product).order_by("position", "pk")
                ):
                    rel.position = i * 2
                    rel.save()
                product_changed.send(product)
            except ProductsPropertiesRelation.DoesNotExist:
                messages.error(self.request, _("Invalid property."))
            return self.get(request, *args, **kwargs)

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        product = self.get_product()

        # prepare properties and options
        props_dicts = product.get_variants_properties()
        all_props = [pd["property"] for pd in props_dicts]
        props_options: Dict[int, Dict[str, Dict[str, Any]]] = {}
        for o in PropertyOption.objects.filter(property__in=all_props):
            props_options.setdefault(o.property_id, {})
            props_options[o.property_id][str(o.pk)] = {"id": o.pk, "name": o.name, "selected": False}

        # selected options per variant
        from lfs.catalog.models import Product as ProductModel

        product_variants = product.variants.all().order_by("variant_position")
        selected_options: Dict[int, Dict[int, Dict[int, str]]] = {}
        for pd in props_dicts:
            prop = pd["property"]
            property_group = pd["property_group"]
            property_group_id = property_group.pk if property_group else 0
            for so in ProductPropertyValue.objects.filter(
                property=prop,
                property_group=property_group,
                product__in=product_variants,
                type=PROPERTY_VALUE_TYPE_VARIANT,
            ):
                selected_groups = selected_options.setdefault(so.product_id, {})
                selected_groups.setdefault(property_group_id, {})[so.property_id] = so.value

        variants: List[Dict[str, Any]] = []
        for variant in product_variants:
            properties = []
            for pd in props_dicts:
                prop = pd["property"]
                property_group = pd["property_group"]
                property_group_id = property_group.pk if property_group else 0

                options = {k: dict(v) for k, v in props_options.get(prop.pk, {}).items()}
                try:
                    sop = selected_options[variant.pk][property_group_id][prop.pk]
                    options[str(sop)]["selected"] = True
                except Exception:
                    pass

                properties.append(
                    {
                        "id": prop.pk,
                        "name": prop.name,
                        "options": options.values(),
                        "property_group_id": property_group_id,
                        "property_group": property_group,
                    }
                )

            variants.append(
                {
                    "id": variant.id,
                    "active": variant.active,
                    "slug": variant.slug,
                    "sku": variant.sku,
                    "name": variant.name,
                    "price": variant.price,
                    "active_price": variant.active_price,
                    "active_sku": variant.active_sku,
                    "active_name": variant.active_name,
                    "position": variant.variant_position,
                    "properties": properties,
                }
            )

        ctx.update(
            {
                "variants": variants,
                "all_properties": props_dicts,
                "local_properties": product.get_local_properties(),
                "display_type_form": DisplayTypeForm(instance=product),
                "default_variant_form": DefaultVariantForm(instance=product),
                "category_variant_form": CategoryVariantForm(instance=product),
                "variant_columns": 9 + len(props_dicts),
                # Property groups (selection)
                "shop_property_groups": [
                    {
                        "id": g.id,
                        "name": g.name,
                        "selected": g in product.property_groups.all(),
                    }
                    for g in PropertyGroup.objects.all()
                ],
            }
        )
        return ctx


class ProductAccessoriesView(PermissionRequiredMixin, ProductTabMixin, TemplateView):
    """Accessories tab (Bootstrap, non-AJAX)."""

    tab_name = "accessories"
    permission_required = "core.manage_shop"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        from lfs.catalog.models import ProductAccessories

        product = self.get_product()
        action = request.POST.get("action")

        if action == "toggle_active":
            product.active_accessories = bool(request.POST.get("active_accessories"))
            product.save()
            product_changed.send(product)
            # For HTMX requests, don't show success message to avoid page disruption
            if not request.headers.get("HX-Request"):
                messages.success(self.request, _("Accessories have been updated."))
            return self.get(request, *args, **kwargs)

        if action == "add":
            selected_ids = [k.split("-", 1)[1] for k in request.POST.keys() if k.startswith("product-")]
            for sid in selected_ids:
                try:
                    acc = Product.objects.get(pk=sid)
                except Product.DoesNotExist:
                    continue
                ProductAccessories.objects.get_or_create(product=product, accessory=acc)

            # refresh positions
            for i, pa in enumerate(ProductAccessories.objects.filter(product=product).order_by("position", "pk")):
                pa.position = (i + 1) * 10
                pa.save()
            product_changed.send(product)
            # For HTMX requests, don't show success message to avoid page disruption
            if not request.headers.get("HX-Request"):
                messages.success(self.request, _("Accessories have been added."))
            return self.get(request, *args, **kwargs)

        if action == "remove":
            selected_ids = [k.split("-", 1)[1] for k in request.POST.keys() if k.startswith("accessory-")]
            from lfs.catalog.models import ProductAccessories as PA

            PA.objects.filter(product=product, accessory_id__in=selected_ids).delete()
            # refresh positions
            for i, pa in enumerate(PA.objects.filter(product=product).order_by("position", "pk")):
                pa.position = (i + 1) * 10
                pa.save()
            product_changed.send(product)
            # For HTMX requests, don't show success message to avoid page disruption
            if not request.headers.get("HX-Request"):
                messages.success(self.request, _("Accessories have been removed."))
            return self.get(request, *args, **kwargs)

        if action == "save":
            from lfs.catalog.models import ProductAccessories as PA

            for pa in PA.objects.filter(product=product):
                qty = request.POST.get(f"quantity-{pa.accessory_id}")
                pos = request.POST.get(f"position-{pa.accessory_id}")
                if qty is not None:
                    try:
                        pa.quantity = int(qty)
                    except (TypeError, ValueError):
                        pass
                if pos is not None:
                    try:
                        pa.position = int(pos)
                    except (TypeError, ValueError):
                        pass
                pa.save()
            # normalize positions
            for i, pa in enumerate(PA.objects.filter(product=product).order_by("position", "pk")):
                pa.position = (i + 1) * 10
                pa.save()
            product_changed.send(product)
            # For HTMX requests, don't show success message to avoid page disruption
            if not request.headers.get("HX-Request"):
                messages.success(self.request, _("Accessories have been updated."))
            return self.get(request, *args, **kwargs)

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        from django.core.paginator import Paginator
        from django.db.models import Q
        from lfs.catalog.models import ProductAccessories as PA

        ctx = super().get_context_data(**kwargs)
        product = self.get_product()

        # Handle both GET and POST parameters for HTMX compatibility
        request_data = (
            self.request.POST
            if self.request.method == "POST" and self.request.POST.get("keep-filters")
            else self.request.GET
        )

        filter_q = request_data.get("filter", "").strip()
        try:
            amount = int(request_data.get("amount", 25))
        except (TypeError, ValueError):
            amount = 25
        page_num = request_data.get("page", 1)

        product_accessories = PA.objects.filter(product=product).select_related("accessory").order_by("position", "pk")
        accessory_ids = list(product_accessories.values_list("accessory_id", flat=True))

        filters = Q()
        if filter_q:
            filters &= Q(name__icontains=filter_q) | Q(sku__icontains=filter_q)

        available_qs = (
            Product.objects.filter(filters).exclude(pk=product.pk).exclude(pk__in=accessory_ids).order_by("name")
        )
        paginator = Paginator(available_qs, amount)
        try:
            available_page = paginator.page(page_num)
        except Exception:
            available_page = paginator.page(1)

        ctx.update(
            {
                "product_accessories": product_accessories,
                "filter": filter_q,
                "amount": amount,
                "page_sizes": [10, 25, 50, 100],
                "available_page": available_page,
                "available_paginator": paginator,
            }
        )
        return ctx


class ProductRelatedProductsView(PermissionRequiredMixin, ProductTabMixin, TemplateView):
    """Related products tab (Bootstrap, non-AJAX)."""

    tab_name = "related"
    permission_required = "core.manage_shop"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        product = self.get_product()
        action = request.POST.get("action")

        if action == "toggle_active":
            product.active_related_products = bool(request.POST.get("active_related_products"))
            product.save()
            product_changed.send(product)
            # For HTMX requests, don't show success message to avoid page disruption
            if not request.headers.get("HX-Request"):
                messages.success(self.request, _("Related products have been updated."))
            return self.get(request, *args, **kwargs)

        if action == "add":
            selected_ids = [k.split("-", 1)[1] for k in request.POST.keys() if k.startswith("product-")]
            for sid in selected_ids:
                try:
                    rp = Product.objects.get(pk=sid)
                except Product.DoesNotExist:
                    continue
                product.related_products.add(rp)
            product.save()
            product_changed.send(product)
            # For HTMX requests, don't show success message to avoid page disruption
            if not request.headers.get("HX-Request"):
                messages.success(self.request, _("Related products have been added."))
            return self.get(request, *args, **kwargs)

        if action == "remove":
            selected_ids = [k.split("-", 1)[1] for k in request.POST.keys() if k.startswith("product-")]
            product.related_products.remove(*selected_ids)
            product.save()
            product_changed.send(product)
            # For HTMX requests, don't show success message to avoid page disruption
            if not request.headers.get("HX-Request"):
                messages.success(self.request, _("Related products have been removed."))
            return self.get(request, *args, **kwargs)

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        from django.core.paginator import Paginator
        from django.db.models import Q

        ctx = super().get_context_data(**kwargs)
        product = self.get_product()

        # Handle both GET and POST parameters for HTMX compatibility
        request_data = (
            self.request.POST
            if self.request.method == "POST" and self.request.POST.get("keep-filters")
            else self.request.GET
        )

        filter_q = request_data.get("filter", "").strip()
        try:
            amount = int(request_data.get("amount", 25))
        except (TypeError, ValueError):
            amount = 25
        page_num = request_data.get("page", 1)

        related_qs = product.related_products.all().order_by("name")
        related_ids = list(related_qs.values_list("id", flat=True))

        filters = Q()
        if filter_q:
            filters &= Q(name__icontains=filter_q) | Q(sku__icontains=filter_q)

        available_qs = (
            Product.objects.filter(filters).exclude(pk=product.pk).exclude(pk__in=related_ids).order_by("name")
        )
        paginator = Paginator(available_qs, amount)
        try:
            available_page = paginator.page(page_num)
        except Exception:
            available_page = paginator.page(1)

        ctx.update(
            {
                "related_products": related_qs,
                "filter": filter_q,
                "amount": amount,
                "page_sizes": [10, 25, 50, 100],
                "available_page": available_page,
                "available_paginator": paginator,
            }
        )
        return ctx


class ProductPropertiesView(PermissionRequiredMixin, ProductTabMixin, TemplateView):
    """Properties tab for a Product."""

    tab_name = "properties"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        product = self.get_product()

        # Generate lists of properties. For entering values.
        display_configurables = False
        display_filterables = False
        display_displayables = False
        configurables = []
        filterables = []
        displayables = []
        product_variant_properties = []

        # Configurable
        if not product.is_product_with_variants():
            for property_group in product.property_groups.all():
                properties = []
                for prop in property_group.properties.filter(configurable=True).order_by("groupspropertiesrelation"):
                    display_configurables = True

                    try:
                        ppv = ProductPropertyValue.objects.get(
                            property=prop,
                            property_group=property_group,
                            product=product,
                            type=PROPERTY_VALUE_TYPE_DEFAULT,
                        )
                    except ProductPropertyValue.DoesNotExist:
                        ppv_value = ""
                    else:
                        ppv_value = ppv.value

                    # Mark selected options
                    options = []
                    for option in prop.options.all():
                        if str(option.id) == ppv_value:
                            selected = True
                        else:
                            selected = False

                        options.append(
                            {
                                "id": option.id,
                                "name": option.name,
                                "selected": selected,
                            }
                        )

                    properties.append(
                        {
                            "id": prop.id,
                            "name": prop.name,
                            "title": prop.title,
                            "type": prop.type,
                            "options": options,
                            "display_number_field": prop.type == PROPERTY_NUMBER_FIELD,
                            "display_text_field": prop.type == PROPERTY_TEXT_FIELD,
                            "display_select_field": prop.type == PROPERTY_SELECT_FIELD,
                            "value": ppv_value,
                        }
                    )

                if properties:
                    configurables.append(
                        {
                            "id": property_group.id,
                            "name": property_group.name,
                            "properties": properties,
                        }
                    )

            # Filterable
            for property_group in product.property_groups.all():
                properties = []
                for prop in property_group.properties.filter(filterable=True).order_by("groupspropertiesrelation"):
                    display_filterables = True

                    # Try to get the value, if it already exists.
                    ppvs = ProductPropertyValue.objects.filter(
                        property=prop, property_group=property_group, product=product, type=PROPERTY_VALUE_TYPE_FILTER
                    )
                    value_ids = [p.value for p in ppvs]

                    # Mark selected options
                    options = []
                    for option in prop.options.all():
                        if str(option.id) in value_ids:
                            selected = True
                        else:
                            selected = False

                        options.append(
                            {
                                "id": option.id,
                                "name": option.name,
                                "selected": selected,
                            }
                        )

                    value = ""
                    if prop.type == PROPERTY_SELECT_FIELD:
                        display_select_field = True
                    else:
                        display_select_field = False
                        try:
                            value = value_ids[0]
                        except IndexError:
                            pass

                    properties.append(
                        {
                            "id": prop.id,
                            "name": prop.name,
                            "title": prop.title,
                            "type": prop.type,
                            "options": options,
                            "value": value,
                            "display_on_product": prop.display_on_product,
                            "display_number_field": prop.type == PROPERTY_NUMBER_FIELD,
                            "display_text_field": prop.type == PROPERTY_TEXT_FIELD,
                            "display_select_field": display_select_field,
                        }
                    )
                if properties:
                    filterables.append(
                        {
                            "id": property_group.id,
                            "name": property_group.name,
                            "properties": properties,
                        }
                    )

            # Displayable
            for property_group in product.property_groups.all():
                properties = []
                for prop in property_group.properties.filter(display_on_product=True).order_by(
                    "groupspropertiesrelation"
                ):
                    display_displayables = True

                    # Try to get the value, if it already exists.
                    ppvs = ProductPropertyValue.objects.filter(
                        property=prop, property_group=property_group, product=product, type=PROPERTY_VALUE_TYPE_DISPLAY
                    )
                    value_ids = [p.value for p in ppvs]

                    # Mark selected options
                    options = []
                    for option in prop.options.all():
                        if str(option.id) in value_ids:
                            selected = True
                        else:
                            selected = False

                        options.append(
                            {
                                "id": option.id,
                                "name": option.name,
                                "selected": selected,
                            }
                        )

                    value = ""
                    if prop.type == PROPERTY_SELECT_FIELD:
                        display_select_field = True
                    else:
                        display_select_field = False
                        try:
                            value = value_ids[0]
                        except IndexError:
                            pass

                    properties.append(
                        {
                            "id": prop.id,
                            "name": prop.name,
                            "title": prop.title,
                            "type": prop.type,
                            "options": options,
                            "value": value,
                            "filterable": prop.filterable,
                            "display_number_field": prop.type == PROPERTY_NUMBER_FIELD,
                            "display_text_field": prop.type == PROPERTY_TEXT_FIELD,
                            "display_select_field": display_select_field,
                        }
                    )

                if properties:
                    displayables.append(
                        {
                            "id": property_group.id,
                            "name": property_group.name,
                            "properties": properties,
                        }
                    )

        if product.is_variant():
            product_variant_properties_dict = {}
            qs = ProductPropertyValue.objects.filter(product=product, type=PROPERTY_VALUE_TYPE_VARIANT)
            for ppv in qs:
                try:
                    property_option = PropertyOption.objects.get(property_id=ppv.property_id, pk=ppv.value)
                    property_group_name = ppv.property_group.name if ppv.property_group_id else ""
                    group_dict = product_variant_properties_dict.setdefault(
                        ppv.property_group_id or 0, {"property_group_name": property_group_name, "properties": []}
                    )
                    group_dict["properties"].append(property_option)
                except (ProductPropertyValue.DoesNotExist, PropertyOption.DoesNotExist):
                    continue

            groups = product_variant_properties_dict.values()
            sorted_groups = sorted(groups, key=lambda group: group["property_group_name"])
            for group in sorted_groups:
                product_variant_properties.append(group)

        # Generate list of all property groups; used for group selection
        product_property_group_ids = [p.id for p in product.property_groups.all()]
        shop_property_groups = []
        for property_group in PropertyGroup.objects.all():
            shop_property_groups.append(
                {
                    "id": property_group.id,
                    "name": property_group.name,
                    "selected": property_group.id in product_property_group_ids,
                }
            )

        ctx.update(
            {
                "filterables": filterables,
                "display_filterables": display_filterables,
                "configurables": configurables,
                "display_configurables": display_configurables,
                "displayables": displayables,
                "display_displayables": display_displayables,
                "product_property_groups": product.property_groups.all(),
                "shop_property_groups": shop_property_groups,
                "product_variant_properties": product_variant_properties,
            }
        )
        return ctx

    def post(self, request, *args, **kwargs):
        """Handle property updates."""
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.urls import reverse
        from lfs.core.signals import product_removed_property_group
        from lfs.caching.listeners import update_product_cache

        product = self.get_product()
        action = request.POST.get("action", "")

        if action == "update_property_groups":
            # Handle property group updates
            selected_group_ids = request.POST.getlist("selected-property-groups")

            for property_group in PropertyGroup.objects.all():
                # if the group is within selected groups we try to add it to the product
                # otherwise we try do delete it
                if str(property_group.id) in selected_group_ids:
                    if not property_group.products.filter(pk=product.pk).exists():
                        property_group.products.add(product.pk)
                else:
                    if property_group.products.filter(pk=product.pk).exists():
                        property_group.products.remove(product.pk)
                        product_removed_property_group.send(sender=property_group, product=product)

            update_product_cache(product)
            messages.success(request, _("Property groups have been updated."))

        elif action == "update_properties":
            # Handle individual property updates
            ppv_type = int(request.POST.get("type", PROPERTY_VALUE_TYPE_DEFAULT))
            ProductPropertyValue.objects.filter(product=product.pk, type=ppv_type).delete()

            # Update property values
            for key in request.POST.keys():
                if not key.startswith("property"):
                    continue

                try:
                    _property, property_group_id, property_id = key.split("-")
                    if property_group_id == "0":
                        property_group_id = None
                    prop = Property.objects.get(pk=property_id)

                    for value in request.POST.getlist(key):
                        if prop.is_valid_value(value):
                            # we have to use get_or_create because it is possible that we get same property values twice
                            ProductPropertyValue.objects.get_or_create(
                                product=product,
                                property_group_id=property_group_id,
                                property=prop,
                                value=value,
                                type=ppv_type,
                            )
                except (ValueError, Property.DoesNotExist):
                    continue

            update_product_cache(product)
            messages.success(request, _("Properties have been updated."))

        # Redirect back to the properties tab
        return redirect(reverse("lfs_manage_product_properties", kwargs={"id": product.pk}))


class ProductDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a product."""

    template_name = "manage/products/delete_product.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = get_object_or_404(Product, pk=self.kwargs["id"])
        return context


class ProductDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes product with passed id."""

    model = Product
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"
    success_message = _("Product has been deleted.")

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, self.success_message)

        # Check if this is an HTMX request
        if request.headers.get("HX-Request"):
            # For HTMX requests, use HX-Redirect header to redirect the browser
            response = HttpResponse()
            response["HX-Redirect"] = success_url
            return response

        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse("lfs_manage_products_list")


class ApplyProductFiltersView(PermissionRequiredMixin, FormView):
    """Handles filter form submissions and redirects back to product view."""

    permission_required = "core.manage_shop"
    form_class = ProductFilterForm

    def form_valid(self, form):
        """Save filters to session and redirect."""
        filters = {}

        # Text filters
        if form.cleaned_data.get("name"):
            filters["name"] = form.cleaned_data["name"]
        if form.cleaned_data.get("sku"):
            filters["sku"] = form.cleaned_data["sku"]
        if form.cleaned_data.get("sub_type"):
            filters["sub_type"] = form.cleaned_data["sub_type"]
        if form.cleaned_data.get("price_calculator"):
            filters["price_calculator"] = form.cleaned_data["price_calculator"]
        if form.cleaned_data.get("status"):
            filters["status"] = form.cleaned_data["status"]

        self.request.session["product-filters"] = filters

        # Determine redirect URL based on current context
        if "id" in self.kwargs:
            # We're in a product detail view
            return HttpResponseRedirect(reverse("lfs_manage_product_data", kwargs={"id": self.kwargs["id"]}))
        else:
            # We're in the product list view
            return HttpResponseRedirect(reverse("lfs_manage_products_list"))

    def form_invalid(self, form):
        """Handle invalid form - redirect back with error."""
        messages.error(self.request, _("Invalid filter data."))
        if "id" in self.kwargs:
            return HttpResponseRedirect(reverse("lfs_manage_product_data", kwargs={"id": self.kwargs["id"]}))
        else:
            return HttpResponseRedirect(reverse("lfs_manage_products_list"))


class ResetProductFiltersView(PermissionRequiredMixin, RedirectView):
    """Resets all product filters."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        """Reset filters and redirect."""
        if "product-filters" in self.request.session:
            del self.request.session["product-filters"]

        # Determine redirect URL based on current context
        if "id" in self.kwargs:
            return reverse("lfs_manage_product_data", kwargs={"id": self.kwargs["id"]})
        else:
            return reverse("lfs_manage_products_list")
