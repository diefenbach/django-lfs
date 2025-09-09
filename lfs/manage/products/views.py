from typing import Any, Dict, List, Optional, Tuple

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView, TemplateView, UpdateView

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
from lfs.manage.portlets.views import PortletsInlineView

from .product import (
    ProductDataForm,
    ProductStockForm,
    VariantDataForm,
)
from .seo import SEOForm
from lfs.core.signals import category_changed, product_changed
from lfs.manage.products.variants import (
    DefaultVariantForm,
    DisplayTypeForm,
    CategoryVariantForm,
    ProductVariantCreateForm,
)
from lfs.core.utils import atof
from lfs.manage import utils as manage_utils
from lfs.caching.listeners import update_product_cache
from lfs.core.signals import product_removed_property_group


class ManageProductsView(PermissionRequiredMixin, RedirectView):
    """Redirect to the first product or to the 'no products' page."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        p = Product.objects.exclude(sub_type=PRODUCT_VARIANT).first()
        if p is not None:
            return reverse("lfs_manage_product_data", kwargs={"id": p.id})
        return reverse("lfs_manage_no_products")


class ProductTabMixin:
    """Mixin for tab navigation in Product views (Bootstrap shell)."""

    template_name = "manage/products/product.html"
    tab_name: Optional[str] = None

    def get_product(self) -> Product:
        return get_object_or_404(Product, pk=self.kwargs["id"])

    def _get_tabs(self, product: Product) -> List[Tuple[str, str]]:
        tabs: List[Tuple[str, str]] = [
            ("data", reverse("lfs_manage_product_data", args=[product.pk])),
            ("categories", reverse("lfs_manage_product_categories", args=[product.pk])),
            ("images", reverse("lfs_manage_product_images", args=[product.pk])),
            ("attachments", reverse("lfs_manage_product_attachments", args=[product.pk])),
        ]
        if product.is_product_with_variants():
            tabs.append(("variants", reverse("lfs_manage_product_variants", args=[product.pk])))
        tabs.extend(
            [
                ("accessories", reverse("lfs_manage_product_accessories", args=[product.pk])),
                ("related", reverse("lfs_manage_product_related", args=[product.pk])),
                ("stock", reverse("lfs_manage_product_stock", args=[product.pk])),
                ("seo", reverse("lfs_manage_product_seo", args=[product.pk])),
                ("portlets", reverse("lfs_manage_product_portlets", args=[product.pk])),
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
    """Variants tab (Bootstrap, non-AJAX)."""

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
