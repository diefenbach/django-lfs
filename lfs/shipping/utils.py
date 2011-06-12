# python imports
from datetime import datetime

# django imports
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

# lfs imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import DeliveryTime
from lfs.catalog.models import Product
from lfs.catalog.settings import DELIVERY_TIME_UNIT_DAYS
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.criteria import utils as criteria_utils
from lfs.customer import utils as customer_utils
from lfs.shipping.models import ShippingMethod


def get_product_delivery_time(request, product_slug, for_cart=False):
    """Returns the delivery time object for the product with given slug.

    If the ``for_cart`` parameter is False, the default delivery time for
    product is calculated. This is at the moment the first valid (iow with the
    hightest priority) shipping method.

    If the ``for_cart parameter`` is True, the delivery time for the product
    within the cart is calculated. This can differ because the shop customer has
    the opportunity to select a shipping method within the cart. If this
    shipping method is valid for the given product this one is taken, if not
    the default one - the default one is the first valid shipping method.
    """
    # TODO: Need a reasonable chaching here
    if for_cart:
        cache_key = "%s-shipping-delivery-time-cart-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, request.user.id)
    else:
        cache_key = "%s-shipping-delivery-time" % settings.CACHE_MIDDLEWARE_KEY_PREFIX

    shippings = None  # cache.get(cache_key)
    if shippings is None:
        shippings = {}

    product_key = "product-%s" % product_slug
    shipping = shippings.get(product_key)
    if shipping is not None:
        return shipping

    product = lfs_get_object_or_404(Product, slug=product_slug)

    # if the product is a product with variants we switch to the default
    # variant to calculate the delivery time. Please note that in this case
    # the default variant is also displayed.
    if product.sub_type == PRODUCT_WITH_VARIANTS:
        variant = product.get_default_variant()
        if variant is not None:
            product = variant

    if product.manual_delivery_time:
        delivery_time = product.delivery_time
    else:
        if for_cart:
            sm = get_selected_shipping_method(request)
            # Within the cart we have to take care of the selected shipping
            # method.
            sms = get_valid_shipping_methods(request, product)
            if sm in sms:
                try:
                    delivery_time = sm.delivery_time
                except AttributeError:
                    delivery_time = None
            else:
                sm = get_default_shipping_method(request)
                try:
                    delivery_time = sm.delivery_time
                except AttributeError:
                    delivery_time = None
        else:
            # For the product we take the standard shipping method, which is the
            # first valid shipping method at the moment.
            try:
                shipping_method = get_first_valid_shipping_method(request, product)
                delivery_time = shipping_method.delivery_time
            except AttributeError:
                delivery_time = None

    # TODO: Define default delivery time for the shop
    if delivery_time is None:
        delivery_time = DeliveryTime(min=1, max=2, unit=DELIVERY_TIME_UNIT_DAYS)

    # Calculate the total delivery time if the product is not on stock.
    if (product.stock_amount <= 0) and (product.order_time):

        # Calculate how much days are left until the product is going to be
        # delivered.
        if product.ordered_at:
            order_delta = datetime.now().date() - product.ordered_at
            order_delta = order_delta.days
        else:
            order_delta = 0

        # Calculate the rest of the origin order time.
        order_time_left = product.order_time.subtract_days(order_delta)

        # Calculate the total delivery time.
        delivery_time += order_time_left
        delivery_time = delivery_time.as_reasonable_unit()

    delivery_time = delivery_time.round()
    shippings[product_key] = delivery_time
    cache.set(cache_key, shippings)

    return delivery_time


def update_to_valid_shipping_method(request, customer, save=False):
    """After this has been called the given customer has a valid shipping
    method in any case.
    """
    valid_sms = get_valid_shipping_methods(request)

    if customer.selected_shipping_method not in valid_sms:
        customer.selected_shipping_method = get_default_shipping_method(request)
        if save:
            customer.save()


def get_valid_shipping_methods(request, product=None):
    """Returns a list of all valid shipping methods for the passed request.
    """
    result = []
    for sm in ShippingMethod.objects.filter(active=True):
        if criteria_utils.is_valid(request, sm, product):
            result.append(sm)
    return result


def get_first_valid_shipping_method(request, product=None):
    """Returns the valid shipping method with the highest priority.
    """
    active_shipping_methods = ShippingMethod.objects.filter(active=True)
    return criteria_utils.get_first_valid(request, active_shipping_methods, product)


def get_default_shipping_method(request):
    """Returns the default shipping method for the passed request.

    At the moment is this the first valid shipping method, but this could be
    made more explicit in future.
    """
    active_shipping_methods = ShippingMethod.objects.filter(active=True)
    return criteria_utils.get_first_valid(request, active_shipping_methods)


def get_selected_shipping_method(request):
    """Returns the selected shipping method for the passed request.

    This could either be an explicitely selected shipping method of the current
    user or the default shipping method.
    """
    customer = customer_utils.get_customer(request)
    if customer and customer.selected_shipping_method:
        return customer.selected_shipping_method
    else:
        return get_default_shipping_method(request)


def get_selected_shipping_country(request):
    """Returns the selected shipping country for the passed request.

    This could either be an explicitely selected country of the current
    user or the default country of the shop.
    """
    customer = customer_utils.get_customer(request)
    if customer:
        if customer.selected_shipping_address:
            return customer.selected_shipping_address.country
        elif customer.selected_country:
            return customer.selected_country

    return lfs.core.utils.get_default_shop().get_default_country()


def get_shipping_costs(request, shipping_method):
    """Returns a dictionary with the shipping price and tax for the passed
    request and shipping method.

    The format of the dictionary is: {"price" : 0.0, "tax" : 0.0}
    """
    if shipping_method is None:
        return {
            "price": 0.0,
            "tax": 0.0
        }

    try:
        tax_rate = shipping_method.tax.rate
    except AttributeError:
        tax_rate = 0.0

    price = criteria_utils.get_first_valid(request,
        shipping_method.prices.all())

    if price is None:
        price = shipping_method.price
        tax = (tax_rate / (tax_rate + 100)) * price

        return {
            "price": price,
            "tax": tax
        }
    else:
        tax = (tax_rate / (tax_rate + 100)) * price.price

        return {
            "price": price.price,
            "tax": tax
        }


def get_delivery_time(request, product):
    """Returns delivery time for given product.
    """
    if product.deliverable == False:
        return {
            "deliverable": False,
            "delivery_time": get_product_delivery_time(request, product.slug)
        }
    else:
        return {
            "deliverable": True,
            "delivery_time": get_product_delivery_time(request, product.slug)
        }
