from django.core.urlresolvers import reverse

from lfs.core.signals import order_submitted
from lfs.criteria import utils as criteria_utils
from lfs.customer import utils as customer_utils
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import PM_ORDER_IMMEDIATELY
from lfs.payment.settings import PM_ORDER_ACCEPTED

import logging
logger = logging.getLogger(__name__)


def update_to_valid_payment_method(request, customer, save=False):
    """
    After this method has been called the given customer has a valid payment
    method.
    """
    valid_sms = get_valid_payment_methods(request)

    if customer.selected_payment_method not in valid_sms:
        customer.selected_payment_method = get_default_payment_method(request)
        if save:
            customer.save()


def get_valid_payment_methods(request):
    """
    Returns all valid payment methods (aka. selectable) for given request as
    list.
    """
    result = []
    for pm in PaymentMethod.objects.filter(active=True):
        if pm.is_valid(request):
            result.append(pm)
    return result


def get_default_payment_method(request):
    """
    Returns the default payment method for given request.
    """
    active_payment_methods = PaymentMethod.objects.filter(active=True)
    return criteria_utils.get_first_valid(request, active_payment_methods)


def get_selected_payment_method(request):
    """
    Returns the selected payment method for given request. This could either
    be an explicitly selected payment method of the current user or the default
    payment method.
    """
    customer = customer_utils.get_customer(request)
    if customer and customer.selected_payment_method:
        return customer.selected_payment_method
    else:
        return get_default_payment_method(request)


def get_payment_costs(request, payment_method):
    """
    Returns the payment price and tax for the given request.
    """
    if payment_method is None:
        return {
            "price": 0.0,
            "tax": 0.0
        }

    try:
        tax_rate = payment_method.tax.rate
    except AttributeError:
        tax_rate = 0.0

    price = criteria_utils.get_first_valid(request, payment_method.prices.all())
    # TODO: this assumes that payment price is given as gross price, we have to add payment processor here
    if price is None:
        price = payment_method.price
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


def process_payment(request):
    """
    Processes the payment depending on the selected payment method. Returns a
    dictionary with the success state, the next url and a optional error
    message.
    """
    from lfs.core.utils import import_symbol
    from lfs.order.utils import add_order
    from lfs.cart.utils import get_cart
    payment_method = get_selected_payment_method(request)

    if payment_method.module:
        payment_class = import_symbol(payment_method.module)
        payment_instance = payment_class(request)

        create_order_time = payment_instance.get_create_order_time()
        if create_order_time == PM_ORDER_IMMEDIATELY:
            order = add_order(request)
            if order is None:
                return {'accepted': True, 'next_url': reverse("lfs_shop_view")}
            payment_instance.order = order
            result = payment_instance.process()
            if result.get("order_state"):
                order.state = result.get("order_state")
                order.save()
            order_submitted.send(sender=order, request=request)
        else:
            cart = get_cart(request)
            payment_instance.cart = cart
            result = payment_instance.process()

        if result["accepted"]:
            if create_order_time == PM_ORDER_ACCEPTED:
                order = add_order(request)
                if result.get("order_state"):
                    order.state = result.get("order_state")
                    order.save()
                order_submitted.send(sender=order, request=request)
        return result
    else:
        order = add_order(request)
        order_submitted.send(sender=order, request=request)
        return {
            "accepted": True,
            "next_url": reverse("lfs_thank_you"),
        }


# DEPRECATED 0.8
def get_pay_link(request, payment_method, order):
    """
    Creates a pay link for the passed payment_method and order.

    This can be used to display the link within the order mail and/or the
    thank you page after a customer has payed.
    """
    from lfs.core.utils import import_symbol
    logger.info("Decprecated: lfs.payment.utils.get_pay_link: this function is deprecated. Please use Order.get_pay_link instead.")

    if payment_method.module:
        payment_class = import_symbol(payment_method.module)
        payment_instance = payment_class(request=request, order=order)
        try:
            return payment_instance.get_pay_link()
        except AttributeError:
            return ""
    else:
        return ""
