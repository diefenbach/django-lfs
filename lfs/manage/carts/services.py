from datetime import datetime
from typing import Dict, Any

from django.utils import timezone


class CartFilterService:
    """Service for filtering carts based on various criteria."""

    def filter_carts(self, queryset, filters: Dict[str, Any]):
        """Filter carts based on session filters."""
        if not filters:
            return queryset

        # Apply date filters
        start = filters.get("start", "")
        end = filters.get("end", "")

        # Parse start date using ISO format
        start_date = self.parse_iso_date(start)
        if start_date:
            start_date = timezone.make_aware(start_date.replace(hour=0, minute=0, second=0))
        else:
            start_date = timezone.make_aware(datetime(1970, 1, 1))

        # Parse end date using ISO format
        end_date = self.parse_iso_date(end)
        if end_date:
            end_date = timezone.make_aware(end_date.replace(hour=23, minute=59, second=59))
        else:
            end_date = timezone.now()

        return queryset.filter(modification_date__range=(start_date, end_date))

    def parse_iso_date(self, date_string: str) -> datetime:
        """Parse ISO format date string (YYYY-MM-DD)."""
        if not date_string:
            return None

        try:
            return datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            return None

    def format_iso_date(self, date_obj: datetime) -> str:
        """Format date as ISO format string (YYYY-MM-DD)."""
        if not date_obj:
            return ""

        return date_obj.strftime("%Y-%m-%d")


class CartDataService:
    """Service for calculating cart data and totals."""

    def get_cart_summary(self, cart, request):
        """Get summary data for a cart including totals and products."""
        total = 0
        item_count = 0
        products = []

        for item in cart.get_items():
            total += item.get_price_gross(request)
            item_count += item.amount
            products.append(item.product.get_name())

        return {
            "total": total,
            "item_count": item_count,
            "products": products,
        }

    def get_carts_with_data(self, carts, request):
        """Get list of carts with calculated data."""
        from lfs.customer.models import Customer

        carts_with_data = []
        for cart in carts:
            summary = self.get_cart_summary(cart, request)

            # Get customer information
            try:
                if cart.user:
                    customer = Customer.objects.get(user=cart.user)
                else:
                    customer = Customer.objects.get(session=cart.session)
            except Customer.DoesNotExist:
                customer = None

            carts_with_data.append(
                {
                    "cart": cart,
                    "total": summary["total"],
                    "item_count": summary["item_count"],
                    "products": summary["products"],
                    "customer": customer,
                }
            )

        return carts_with_data
