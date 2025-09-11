from django.core.paginator import Paginator

from lfs.manage.products.services import ProductFilterService
from lfs.manage.products.forms import ProductFilterForm


class ProductFilterMixin:
    """Mixin for handling product filtering logic."""

    def get_product_filters(self):
        """Get product filters from session."""
        if not hasattr(self, "request") or self.request is None:
            return {}
        if not hasattr(self.request, "session") or self.request.session is None:
            return {}
        return self.request.session.get("product-filters", {})

    def get_filtered_products_queryset(self):
        """Get filtered products based on session filters."""
        try:
            from lfs.catalog.models import Product
            from lfs.catalog.settings import VARIANT as PRODUCT_VARIANT

            queryset = Product.objects.exclude(sub_type=PRODUCT_VARIANT).order_by("-creation_date")
            product_filters = self.get_product_filters()

            filter_service = ProductFilterService()
            return filter_service.filter_products(queryset, product_filters)
        except Exception:
            # If there's a database error, return empty queryset
            from lfs.catalog.models import Product

            return Product.objects.none()

    def get_filter_form_initial(self):
        """Get initial data for filter form."""
        product_filters = self.get_product_filters()

        return {
            "name": product_filters.get("name", ""),
            "sku": product_filters.get("sku", ""),
            "sub_type": product_filters.get("sub_type", ""),
            "price_calculator": product_filters.get("price_calculator", ""),
        }


class ProductPaginationMixin:
    """Mixin for handling product pagination."""

    def get_paginated_products(self, page_size=22):
        """Get paginated products."""
        queryset = self.get_filtered_products_queryset()
        paginator = Paginator(queryset, page_size)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)


class ProductDataMixin:
    """Mixin for handling product data calculations."""

    def get_products_with_data(self, products_page):
        """Get products with enriched data for display."""
        from lfs.catalog.settings import PRODUCT_TYPE_LOOKUP

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

        return products_with_data

    def get_product_with_data(self, product):
        """Get single product with enriched data."""
        from lfs.catalog.settings import PRODUCT_TYPE_LOOKUP

        return {
            "product": product,
            "categories": ", ".join([cat.name for cat in product.categories.all()]),
            "price": product.get_price(None),
            "stock": product.stock_amount if product.manage_stock_amount else None,
            "active": product.active,
            "sub_type_display": PRODUCT_TYPE_LOOKUP.get(product.sub_type, product.sub_type),
        }


class ProductContextMixin:
    """Mixin for providing common product context data."""

    def get_product_context_data(self, **kwargs):
        """Get common context data for product views."""
        # Get product filters from session
        if not hasattr(self, "request") or self.request is None:
            return {}
        elif not hasattr(self.request, "session") or self.request.session is None:
            return {}

        product_filters = self.request.session.get("product-filters", {})

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

        return {
            "product_filters": product_filters,
            "filter_form": filter_form,
        }
