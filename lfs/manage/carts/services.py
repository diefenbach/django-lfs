from datetime import datetime, date, time
from typing import Dict, Any, Optional

from django.utils import timezone


class CartFilterService:
    """Service for filtering carts based on various criteria."""

    def filter_carts(self, queryset, filters: Dict[str, Any]):
        """Filter carts based on session filters using half-open intervals.

        - start: interpreted as the start of that day (00:00:00)
        - end: interpreted as exclusive end; if omitted, defaults to start of tomorrow
        """
        # Handle case where filters might be a string (corrupted session data)
        if not isinstance(filters, dict):
            filters = {}

        # Apply date filters
        start = filters.get("start", "")
        end = filters.get("end", "")

        # Start datetime (aware) — default to epoch start
        start_date = self.parse_iso_date(start)
        if start_date:
            start_dt = timezone.make_aware(datetime.combine(start_date, time.min))
        else:
            start_dt = timezone.make_aware(datetime(1970, 1, 1))

        # End datetime exclusive (aware)
        end_date = self.parse_iso_date(end)
        if end_date:
            # If a calendar end date is given, treat it as exclusive next-day start
            end_dt = timezone.make_aware(datetime.combine(end_date, time.min))
            return queryset.filter(modification_date__gte=start_dt, modification_date__lt=end_dt)
        else:
            # If no end given, only filter by start date
            return queryset.filter(modification_date__gte=start_dt)

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

        try:
            for item in cart.get_items():
                total += item.get_price_gross(request)
                item_count += item.amount
                products.append(item.product.get_name())
        except Exception:
            # If there's an error calculating items, return empty summary
            pass

        return {
            "total": total,
            "item_count": item_count,
            "products": products,
        }

    def get_carts_with_data(self, carts, request):
        """Get list of carts with calculated data with batched customer lookup."""
        from lfs.customer.models import Customer

        # Handle None or empty carts list
        if not carts:
            return []

        # Collect keys for batched customer lookup
        user_ids = set()
        sessions = set()
        for cart in carts:
            if getattr(cart, "user_id", None):
                user_ids.add(cart.user_id)
            elif getattr(cart, "session", None):
                sessions.add(cart.session)

        # Fetch customers in batches
        customers_by_user = {}
        customers_by_session = {}
        try:
            if user_ids:
                for cust in Customer.objects.filter(user_id__in=user_ids):
                    if getattr(cust, "user_id", None) is not None:
                        customers_by_user[cust.user_id] = cust
            if sessions:
                for cust in Customer.objects.filter(session__in=sessions):
                    if getattr(cust, "session", None) is not None:
                        customers_by_session[cust.session] = cust
        except Exception:
            # If database error occurs, continue without customer data
            pass

        carts_with_data = []
        for cart in carts:
            summary = self.get_cart_summary(cart, request)

            # Resolve customer from maps without per-cart queries
            customer = None
            if getattr(cart, "user_id", None):
                customer = customers_by_user.get(cart.user_id)
            elif getattr(cart, "session", None):
                customer = customers_by_session.get(cart.session)

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
