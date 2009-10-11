# python imports
from datetime import datetime
from datetime import timedelta

# django imports
from django.core.cache import cache
from django.db.models import Q

# lfs imports
from lfs.catalog.models import Product
from lfs.marketing.models import Topseller
from lfs.order.models import Order
from lfs.order.settings import CLOSED
from lfs.order.models import OrderItem
from django.db import connection

def get_orders(days=14):
    """Returns closed orders which are closed for given amount of days.
    """
    limit = datetime.now() - timedelta(days=days)

    orders = Order.objects.filter(state=CLOSED, state_modified__lte=limit)
    return orders

def get_topseller(limit=5):
    """Returns products with the most sales. Limited by given limit.
    """
    cache_key = "topseller"
    topseller = cache.get(cache_key)
    if topseller is not None:
        return topseller

    # TODO: Check Django 1.1's aggregation
    cursor = connection.cursor()
    cursor.execute("""SELECT product_id, sum(product_amount) as sum
                      FROM order_orderitem
                      GROUP BY product_id
                      ORDER BY sum DESC limit %s""" % (limit*2))

    products = []
    for topseller in cursor.fetchall():
        product = Product.objects.get(pk=topseller[0])
        if product.is_active():
            try:
                products.append(product)
            except Product.DoesNotExist:
                pass

    for explicit_ts in Topseller.objects.all():

        if explicit_ts.product.is_active():
            # Remove explicit_ts if it's already in the object list
            if explicit_ts.product in products:
                products.pop(products.index(explicit_ts.product))

            # Then reinsert the explicit_ts on the given position
            position = explicit_ts.position - 1
            if position < 0:
                position = 0
            products.insert(position, explicit_ts.product)

    products = products[:limit]
    cache.set(cache_key, products)
    return products

def get_topseller_for_category(category, limit=5):
    """Returns products with the most sales withing given category. Limited by
    given limit.
    """
    # TODO: Check Django 1.1's aggregation

    cache_key = "topseller-%s" % category.id
    topseller = cache.get(cache_key)
    if topseller is not None:
        return topseller

    # 1. Get all sub catgegories of passed category
    categories = [category]
    categories.extend(category.get_all_children())
    category_ids = [c.id for c in categories]
    
    # 2. Get all order items with products within these categories.
    #    product__parent__categories is for variants
    f = Q(product__parent__categories__in=category_ids) | \
        Q(product__categories__in=category_ids)
        
    order_items = OrderItem.objects.filter(f)
    
    # 3. Calculate totals per product
    products = {}
    for order_item in order_items:
        if order_item.product.is_active():
            if not products.has_key(order_item.product.id):
                products[order_item.product.id] = 0
            products[order_item.product.id] += order_item.product_amount

    # 4. Sort product ids on values
    products = products.items()
    products.sort(lambda a, b: cmp(b[1], a[1]))

    objects = []
    for product_id, quantity in products[:limit]:
        try:
            objects.append(Product.objects.get(pk=product_id))
        except Product.DoesNotExist:
            pass

    for explicit_ts in Topseller.objects.filter(product__categories__in=category_ids):
        
        if explicit_ts.product.is_active():
            # Remove explicit_ts if it's already in the object list
            if explicit_ts.product in objects:
                objects.pop(objects.index(explicit_ts.product))

            # Then reinsert the explicit_ts on the given position
            position = explicit_ts.position - 1
            if position < 0:
                position = 0
            objects.insert(position, explicit_ts.product)

    objects = objects[:limit]
    cache.set(cache_key, objects)
    return objects