from datetime import datetime, date, time
from typing import Dict, Any, Optional

from django.db.models import Q
from django.utils import timezone

from lfs.order.settings import ORDER_STATES


class OrderFilterService:
    """Service for filtering orders based on various criteria."""

    def filter_orders(self, queryset, filters: Dict[str, Any]):
        """Filter orders based on session filters using half-open intervals.

        - start: interpreted as the start of that day (00:00:00)
        - end: interpreted as exclusive end; if omitted, defaults to start of tomorrow
        """
        if not filters:
            return queryset

        # Apply name filter
        name = filters.get("name", "").strip()
        if name:
            name_filter = Q(customer_lastname__icontains=name) | Q(customer_firstname__icontains=name)
            queryset = queryset.filter(name_filter)

        # Apply state filter
        state_id = filters.get("state")
        if state_id and state_id != "":
            try:
                state_id = int(state_id)
                queryset = queryset.filter(state=state_id)
            except (ValueError, TypeError):
                pass

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
        else:
            # If no end given, use start of tomorrow relative to today
            now = timezone.now()
            tomorrow = (now.replace(hour=0, minute=0, second=0, microsecond=0)) + timezone.timedelta(days=1)
            end_dt = tomorrow

        return queryset.filter(created__range=(start_dt, end_dt))

    def parse_iso_date(self, date_string: str) -> Optional[date]:
        """Parse ISO format date string (YYYY-MM-DD) and return a date."""
        if not date_string or not str(date_string).strip():
            return None

        try:
            return datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError:
            return None

    def format_iso_date(self, date_obj: datetime | date | str) -> str:
        """Format date as ISO format string (YYYY-MM-DD)."""
        if not date_obj:
            return ""

        # If it's already a string, return as is (assuming it's already in ISO format)
        if isinstance(date_obj, str):
            return date_obj

        return date_obj.strftime("%Y-%m-%d")


class OrderDataService:
    """Service for calculating order data and totals."""

    def get_order_summary(self, order):
        """Get summary data for an order including totals and products."""
        total = order.price
        item_count = sum(item.amount for item in order.items.all())
        products = [item.product.get_name() for item in order.items.all() if item.product]

        return {
            "total": total,
            "item_count": item_count,
            "products": products,
        }

    def get_orders_with_data(self, orders):
        """Get list of orders with calculated data."""
        orders_with_data = []

        for order in orders:
            summary = self.get_order_summary(order)

            orders_with_data.append(
                {
                    "order": order,
                    "total": summary["total"],
                    "item_count": summary["item_count"],
                    "products": summary["products"],
                    "customer_name": f"{order.customer_firstname} {order.customer_lastname}".strip(),
                    "state_name": self._get_state_name(order.state),
                }
            )

        return orders_with_data

    def get_order_with_data(self, order):
        """Get a single order enriched with calculated data."""
        if order is None:
            return None
        result = self.get_orders_with_data([order])
        return result[0] if result else None

    def _get_state_name(self, state_id):
        """Get the display name for a state ID."""
        for state_tuple in ORDER_STATES:
            if state_tuple[0] == state_id:
                return str(state_tuple[1])
        return str(state_id)
