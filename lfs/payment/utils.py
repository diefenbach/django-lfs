# python imports
import locale

# django imports
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

# lfs imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop
from lfs.core.signals import order_submitted
from lfs.criteria import utils as criteria_utils
from lfs.customer import utils as customer_utils
from lfs.order.settings import PAID
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import PAYPAL

# other imports
from paypal.standard.conf import POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT


def update_to_valid_payment_method(request, customer, save=False):
    """After this method has been called the given customer has a valid
    payment method.
    """
    valid_sms = get_valid_payment_methods(request)

    if customer.selected_payment_method not in valid_sms:
        customer.selected_payment_method = get_default_payment_method(request)
        if save:
            customer.save()


def get_valid_payment_methods(request):
    """Returns all valid payment methods (aka. selectable) for given request as
    list.
    """
    result = []
    for pm in PaymentMethod.objects.filter(active=True):
        if criteria_utils.is_valid(request, pm):
            result.append(pm)
    return result


def get_default_payment_method(request):
    """Returns the default payment method for given request.
    """
    active_payment_methods = PaymentMethod.objects.filter(active=True)
    return criteria_utils.get_first_valid(request, active_payment_methods)


def get_selected_payment_method(request):
    """Returns the selected payment method for given request. This could either
    be an explicitly selected payment method of the current user or the default
    payment method.
    """
    customer = customer_utils.get_customer(request)
    if customer and customer.selected_payment_method:
        return customer.selected_payment_method
    else:
        return get_default_payment_method(request)


def get_payment_costs(request, payment_method):
    """Returns the payment price and tax for the given request.
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

    price = criteria_utils.get_first_valid(request,
        payment_method.prices.all())

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
    """Processes the payment depending on the selected payment method. Returns
    a dictionary with the success state, the next url and a optional error
    message.
    """
    payment_method = get_selected_payment_method(request)
    shop = lfs.core.utils.get_default_shop()

    if payment_method.module:
        module = lfs.core.utils.import_module(payment_method.module + ".views")
        result = module.process(request)
        if result["accepted"] == True:
            order = lfs.order.utils.add_order(request)
            # TODO: this has to be returned from the module
            order.state = PAID
            order.save()
            order_submitted.send({"order": order, "request": request})
        return result

    elif payment_method.id == PAYPAL:
        order = lfs.order.utils.add_order(request)
        if order:  # if we have no cart then the order will be None
            order_submitted.send({"order": order, "request": request})
            if settings.LFS_PAYPAL_REDIRECT:
                return {
                    "accepted": True,
                    "next-url": order.get_pay_link(),
                }
        return {
            "accepted": True,
            "next-url": reverse("lfs_thank_you"),
        }
    else:
        order = lfs.order.utils.add_order(request)
        order_submitted.send({"order": order, "request": request})
        return {
            "accepted": True,
            "next-url": reverse("lfs_thank_you"),
        }


def get_next_url(payment_method, order):
    """Creates the next url for the passed payment method and order.
    """
    if payment_method.id == PAYPAL:
        return get_paypal_link_for_order(order)
    elif payment_method.module:
        module = lfs.core.utils.import_module.import_module(payment_method + ".views")
        try:
            return module.get_next_url(order)
        except AttributeError:
            return None
    else:
        return None


def get_pay_link(payment_method, order):
    """Creates a pay link for the passed payment_method and order.

    This can be used to display the link within the order mail and/or the
    thank you page after a customer has payed.
    """
    if payment_method.id == PAYPAL:
        return get_paypal_link_for_order(order)
    elif payment_method.module:
        module = lfs.core.utils.import_module(payment_method.module + ".views")
        try:
            return module.get_pay_link(order)
        except AttributeError:
            return ""
    else:
        return ""


def get_paypal_link_for_order(order):
    """Creates paypal link for given order.
    """
    shop = lfs_get_object_or_404(Shop, pk=1)
    current_site = Site.objects.get(id=settings.SITE_ID)
    conv=locale.localeconv()
    default_currency = conv['int_curr_symbol']

    info = {
        "cmd": "_xclick",
        "upload": "1",
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "currency_code": default_currency,
        "notify_url": "http://" + current_site.domain + reverse('paypal-ipn'),
        "return": "http://" + current_site.domain + reverse('paypal-pdt'),
        "first_name": order.invoice_firstname,
        "last_name": order.invoice_lastname,
        "address1": order.invoice_line1,
        "address2": order.invoice_line2,
        "city": order.invoice_city,
        "state": order.invoice_state,
        "zip": order.invoice_code,
        "no_shipping": "1",
        "custom": order.uuid,
        "invoice": order.uuid,
        "item_name": shop.shop_owner,
        "amount": "%.2f" % (order.price - order.tax),
        "tax": "%.2f" % order.tax,
    }

    parameters = "&".join(["%s=%s" % (k, v) for (k, v) in info.items()])
    if getattr(settings, 'PAYPAL_DEBUG', settings.DEBUG):
        url = SANDBOX_POSTBACK_ENDPOINT + "?" + parameters
    else:
        url = POSTBACK_ENDPOINT + "?" + parameters

    return url
