from datetime import datetime, date
from typing import Dict, Any, Optional

from django.db.models import Q


class ProductFilterService:
    """Service for filtering products based on various criteria."""

    def filter_products(self, queryset, filters: Dict[str, Any]):
        """Filter products based on session filters."""
        # Handle case where filters might be a string (corrupted session data)
        if not isinstance(filters, dict):
            filters = {}

        # Apply name filter
        name = filters.get("name", "").strip()
        if name:
            queryset = queryset.filter(Q(name__icontains=name) | Q(short_description__icontains=name))

        # Apply SKU filter
        sku = filters.get("sku", "").strip()
        if sku:
            queryset = queryset.filter(sku__icontains=sku)

        # Apply sub_type filter
        sub_type = filters.get("sub_type", "").strip()
        if sub_type:
            queryset = queryset.filter(sub_type=sub_type)

        # Apply price_calculator filter
        price_calculator = filters.get("price_calculator", "").strip()
        if price_calculator:
            from lfs.core.utils import get_default_shop

            # Get the default shop's price calculator
            shop = get_default_shop()
            shop_price_calculator = shop.price_calculator

            # Filter products that either:
            # 1. Have the explicit price_calculator set, OR
            # 2. Have price_calculator=None and the shop default matches the filter
            if price_calculator == shop_price_calculator:
                # Include both explicit matches and products inheriting from shop
                queryset = queryset.filter(Q(price_calculator=price_calculator) | Q(price_calculator__isnull=True))
            else:
                # Only include explicit matches (not inheriting from shop)
                queryset = queryset.filter(price_calculator=price_calculator)

        # Apply status filter
        status = filters.get("status", "").strip()
        if status:
            if status == "active":
                queryset = queryset.filter(active=True)
            elif status == "inactive":
                queryset = queryset.filter(active=False)

        return queryset

    def parse_iso_date(self, date_string: str) -> Optional[date]:
        """Parse ISO format date string (YYYY-MM-DD) and return a date."""
        if not date_string or not str(date_string).strip():
            return None

        try:
            return datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError:
            return None

    def format_iso_date(self, date_obj: datetime | date) -> str:
        """Format date as ISO format string (YYYY-MM-DD)."""
        if isinstance(date_obj, datetime):
            return date_obj.strftime("%Y-%m-%d")
        return date_obj.strftime("%Y-%m-%d")


class ProductDataService:
    """Service for enriching product data."""

    def get_product_summary(self, product):
        """Get summary data for a product."""
        return {
            "categories": ", ".join([cat.name for cat in product.categories.all()[:3]]),
            "price": product.get_price(None),
            "stock": product.stock_amount if product.manage_stock_amount else None,
            "active": product.active,
        }
