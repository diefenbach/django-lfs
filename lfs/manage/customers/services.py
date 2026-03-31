from datetime import datetime, date
from typing import Dict, Any, List, Optional
from django.db.models import QuerySet, Q
from lfs.customer.models import Customer
from lfs.cart.models import Cart
from lfs.order.models import Order

# from lfs.cart.utils import get_cart_price  # Not available in this version
from lfs.shipping.utils import get_selected_shipping_method, get_shipping_costs
from lfs.payment.utils import get_selected_payment_method, get_payment_costs


class CustomerFilterService:
    """Service for handling customer filtering logic."""

    def filter_customers(self, queryset: QuerySet, filters: Dict[str, Any]) -> QuerySet:
        """Apply filters to customer queryset."""
        if filters is None:
            return queryset

        # Filter by name
        name = filters.get("name", "")
        if name:
            f = Q(addresses__lastname__icontains=name)
            f |= Q(addresses__firstname__icontains=name)
            queryset = queryset.filter(f)

        # Filter by date range - use user's date_joined for user-based customers
        # and cart creation_date for session-based customers
        start = filters.get("start")
        end = filters.get("end")

        if start or end:
            # For user-based customers, filter by user.date_joined
            user_q = Q()
            if start:
                # Parse date string using the service method
                if isinstance(start, str):
                    start = self.parse_iso_date(start)
                if start:
                    user_q &= Q(user__date_joined__gte=start)
            if end:
                # Parse date string using the service method
                if isinstance(end, str):
                    end = self.parse_iso_date(end)
                if end:
                    user_q &= Q(user__date_joined__lte=end)

            # For session-based customers, we can't easily filter by creation date
            # since Customer model doesn't have a creation_date field
            # We'll only filter user-based customers for now
            if user_q:
                # Only apply the filter if we have valid date conditions
                queryset = queryset.filter(user_q)

        return queryset

    def get_ordering(self, ordering: str, ordering_order: str = "") -> str:
        """Get proper ordering string for queryset."""
        if ordering == "lastname":
            ordering = "addresses__lastname"
        elif ordering == "firstname":
            ordering = "addresses__firstname"
        elif ordering == "email":
            ordering = "user__email"
        elif ordering == "date_joined":
            ordering = "user__date_joined"
        elif ordering == "creation_date":
            # Customer model doesn't have creation_date field, use id instead
            ordering = "id"

        return f"{ordering_order}{ordering}"

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


class CustomerDataService:
    """Service for handling customer data calculations and enrichment."""

    def get_customers_with_data(self, customers: List[Customer], request) -> List[Dict[str, Any]]:
        """Get list of customers with calculated data."""
        result = []

        # Handle None or empty customers list
        if not customers:
            return result

        for customer in customers:
            if not customer:
                continue
            # Skip customers that don't have either user or session
            if not customer.user and not customer.session:
                continue

            # Build query for orders and cart based on customer type
            if customer.session:
                query = Q(session=customer.session)
            elif customer.user:
                query = Q(user=customer.user)
            else:
                query = Q(pk__in=[])  # Empty query

            try:
                cart = Cart.objects.get(query)
                cart_price = cart.get_price_gross(request, total=True)
            except (Cart.DoesNotExist, Exception):
                cart_price = None

            try:
                orders = Order.objects.filter(query)
                orders_count = len(orders)
            except Exception:
                orders_count = 0

            customer_data = {
                "customer": customer,
                "orders_count": orders_count,
                "cart_price": cart_price,
            }
            result.append(customer_data)

        return result

    def get_customer_with_data(self, customer: Customer, request) -> Dict[str, Any]:
        """Get a single customer enriched with calculated data."""
        if not customer:
            return {
                "customer": None,
                "orders": [],
                "cart": None,
                "cart_price": None,
                "shipping_address": None,
                "invoice_address": None,
            }

        # Build query for orders and cart based on customer type
        if customer.session:
            query = Q(session=customer.session)
        elif customer.user:
            query = Q(user=customer.user)
        else:
            query = Q(pk__in=[])  # Empty query

        try:
            orders = Order.objects.filter(query)
        except Exception:
            orders = []

        try:
            cart = Cart.objects.get(query)
            # Shipping
            try:
                selected_shipping_method = get_selected_shipping_method(request)
                shipping_costs = get_shipping_costs(request, selected_shipping_method)
                shipping_price = shipping_costs.get("price_gross", 0)
            except Exception:
                shipping_price = 0

            # Payment
            try:
                selected_payment_method = get_selected_payment_method(request)
                payment_costs = get_payment_costs(request, selected_payment_method)
                payment_price = payment_costs.get("price_gross", 0)
            except Exception:
                payment_price = 0

            cart_price = cart.get_price_gross(request) + shipping_price + payment_price
        except (Cart.DoesNotExist, Exception):
            cart = None
            cart_price = None

        try:
            if customer.selected_shipping_address:
                shipping_address = customer.selected_shipping_address.as_html(request, "shipping")
            else:
                shipping_address = None
        except Exception:
            shipping_address = None

        try:
            if customer.selected_invoice_address:
                invoice_address = customer.selected_invoice_address.as_html(request, "invoice")
            else:
                invoice_address = None
        except Exception:
            invoice_address = None

        return {
            "customer": customer,
            "orders": orders,
            "cart": cart,
            "cart_price": cart_price,
            "shipping_address": shipping_address,
            "invoice_address": invoice_address,
        }
