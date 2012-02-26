# python imports
from datetime import datetime
from datetime import timedelta

# django imports
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q

# lfs imports
from lfs.catalog.models import Product
from lfs.marketing.models import Topseller
from lfs.marketing.models import ProductSales
from lfs.order.models import Order
from lfs.order.settings import CLOSED
from lfs.order.models import OrderItem
from django.db import connection


def calculate_product_sales():
    """Calculates and saves total product sales.
    """
    ProductSales.objects.all().delete()

    products = {}
    for order_item in OrderItem.objects.all():
        if order_item.product.is_variant():
            product = order_item.product.parent
            if product is None:
                continue
        else:
            product = order_item.product

        if product.id not in products:
            products[product.id] = [product, 0]
        products[product.id][1] += order_item.product_amount

    for product_id, data in products.items():
        product, created = ProductSales.objects.get_or_create(product=data[0])
        product.sales = data[1]
        product.save()


def get_orders(days=14):
    """Returns closed orders which are closed for given amount of days.
    """
    limit = datetime.now() - timedelta(days=days)

    orders = Order.objects.filter(state=CLOSED, state_modified__lte=limit)
    return orders


def get_topseller(limit=5):
    """Returns products with the most sales. Limited by given limit.
    """
    cache_key = "%s-topseller" % settings.CACHE_MIDDLEWARE_KEY_PREFIX
    topseller = cache.get(cache_key)
    if topseller is not None:
        return topseller

    # TODO: Check Django 1.1's aggregation
    cursor = connection.cursor()
    cursor.execute("""SELECT product_id, sum(product_amount) as sum
                      FROM order_orderitem
                      where product_id is not null
                      GROUP BY product_id
                      ORDER BY sum DESC limit %s""" % (limit * 2))

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

    cache_key = "%s-topseller-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, category.id)
    topseller = cache.get(cache_key)
    if topseller is not None:
        return topseller

    # 1. Get all sub catgegories of passed category
    categories = [category]
    categories.extend(category.get_all_children())
    category_ids = [c.id for c in categories]

    # Get all the most saled products for this categories
    pss = ProductSales.objects.filter(product__categories__in=category_ids).order_by("-sales")[:limit]

    objects = [ps.product for ps in pss]
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

    cache.set(cache_key, objects)
    return objects[:limit]
