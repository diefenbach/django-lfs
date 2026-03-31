# django imports
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum
from lfs.catalog.models import Product, Category
from lfs.marketing.utils import get_orders
from lfs.order.models import Order, OrderItem
from lfs.marketing.models import OrderRatingMail


@permission_required("core.manage_shop")
def dashboard(request, template_name="manage/dashboard/dashboard.html"):
    """Dashboard view showing shop statistics"""
    total_products = Product.objects.count()
    active_products = Product.objects.filter(active=True).count()
    inactive_products = total_products - active_products

    total_categories = Category.objects.count()
    visible_categories = Category.objects.filter(exclude_from_navigation=False).count()
    hidden_categories = total_categories - visible_categories

    total_orders = Order.objects.count()

    # Calculate orders this month (from 1st day of current month)
    now = timezone.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    orders_this_month = Order.objects.filter(created__gte=first_day_of_month).count()

    # Calculate orders this year (from January 1st)
    first_day_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    orders_this_year = Order.objects.filter(created__gte=first_day_of_year).count()

    # Calculate eligible rating mails (orders without rating mail sent)
    orders_with_rating_mail = OrderRatingMail.objects.values_list("order_id", flat=True)
    eligible_rating_mails = get_orders().count() - len(orders_with_rating_mail)

    # Find best selling product
    best_selling_product = None
    best_selling_count = 0

    if total_orders > 0:
        # Get product sales count from order items
        product_sales = (
            OrderItem.objects.values("product")
            .annotate(total_quantity=Sum("product_amount"))
            .order_by("-total_quantity")
        )

        if product_sales.exists():
            best_selling_product_id = product_sales.first()["product"]
            best_selling_count = product_sales.first()["total_quantity"]
            try:
                best_selling_product = Product.objects.get(id=best_selling_product_id)
            except Product.DoesNotExist:
                best_selling_product = None
                best_selling_count = 0

    context = {
        "total_products": total_products,
        "active_products": active_products,
        "inactive_products": inactive_products,
        "total_categories": total_categories,
        "visible_categories": visible_categories,
        "hidden_categories": hidden_categories,
        "total_orders": total_orders,
        "orders_this_month": orders_this_month,
        "orders_this_year": orders_this_year,
        "eligible_rating_mails": eligible_rating_mails,
        "best_selling_product": best_selling_product,
        "best_selling_count": best_selling_count,
    }

    return render(request, template_name, context)
