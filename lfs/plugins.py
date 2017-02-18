# python imports
import math

# django imports
from django import forms
from django.db import models

# lfs imports
import lfs
from lfs.payment.settings import PM_ORDER_IMMEDIATELY  # NOQA
from lfs.payment.settings import PM_ORDER_ACCEPTED  # NOQA
from lfs.payment.settings import PM_MSG_TOP  # NOQA
from lfs.payment.settings import PM_MSG_FORM  # NOQA
from lfs.order.settings import PAID  # NOQA


class OrderNumberGenerator(models.Model):
    """
    Base class from which all order number generators should inherit.

    **Attributes:**

    id
        The unique id of the order number generator.
    """
    id = models.CharField(primary_key=True, max_length=20)

    class Meta:
        abstract = True

    def init(self, request, order):
        """
        Initializes the order number generator. This method is called
        automatically from LFS.
        """
        self.request = request
        self.order = order
        self.user = request.user
        self.customer = lfs.customer.utils.get_customer(request)
        self.cart = lfs.cart.utils.get_cart(request)

    def get_next(self, formatted=True):
        """
        Returns the next order number as string. Derived classes must implement
        this method.

        **Parameters:**

        formatted
            If True the number will be returned within the stored format, which
            is based on Python default string formatting operators, e.g.
            ``%04d``.
        """
        raise NotImplementedError

    def exclude_form_fields(self):
        """
        Returns a list of fields, which are excluded from the model form, see
        also ``get_form``.
        """
        return ("id", )

    def get_form(self, **kwargs):
        """
        Returns the form which is used within the shop preferences management
        interface.

        All parameters are passed to the form.
        """
        class OrderNumberGeneratorForm(forms.ModelForm):
            class Meta:
                model = self
                exclude = self.exclude_form_fields()

        return OrderNumberGeneratorForm(**kwargs)


class PaymentMethodProcessor(object):
    """
    Base class from which all 3rd-party payment method processors should inherit.

    **Attributes:**

    request
        The current request.

    cart
        The current cart. This is only set, when create order time is ACCEPTED.

    order
        The current order. This is only set, when create order time is
        IMMEDIATELY.
    """
    def __init__(self, request, cart=None, order=None):
        self.request = request
        self.cart = cart
        self.order = order

    def process(self):
        """
        Implements the processing of the payment method. Returns a dictionary
        with several status codes, see below.

        **Return Values:**

        This values are returned within a dictionary.

        accepted (mandatory)
            Indicates whether the payment is accepted or not. if this is
            ``False`` the customer keeps on the checkout page and gets
            ``message`` (if given) below. If this is ``True`` the customer will
            be redirected to next_url (if given).

        message (optional)
            This message is displayed on the checkout page, when the order is
            not accepted.

        message_location (optional)
            The location, where the message is displayed.

        next_url (optional)
            The url to which the user is redirect after the payment has been
            processed. if this is not given the customer is redirected to the
            default thank-you page.

        order_state (optional)
            The state in which the order should be set. It's just PAID. If it's
            not given the state keeps in SUBMITTED.
        """
        raise NotImplementedError

    def get_create_order_time(self):
        """
        Returns the time when the order should be created. It is one of:

        PM_ORDER_IMMEDIATELY
            The order is created immediately before the payment is processed.

        PM_ORDER_ACCEPTED
            The order is created when the payment has been processed and
            accepted.
        """
        raise NotImplementedError

    def get_pay_link(self):
        """
        Returns a link to the payment service to pay the current order, which
        is displayed on the thank-you page and the order confirmation mail. In
        this way the customer can pay the order again if something has gone
        wrong.
        """
        return None


class PriceCalculator(object):
    """
    This is the base class that pricing calculators must inherit from.

    **Attributes:**

    product
        The product for which the price is calculated.

    request
        The current request.
    """
    def __init__(self, request, product, **kwargs):
        self.request = request
        self.product = product

    def get_effective_price(self, amount=1):
        """ Effective price is used for sorting and filtering.
            Usually it is same as value from get_price but in some cases it might differ (eg. if we add eco tax to
            product price)

        **Parameters:**

        amount
            The amount of products for which the price is calculated.
        """
        return self.get_price(amount)

    def get_price(self, with_properties=True, amount=1):
        """
        Returns the stored price of the product without any tax calculations.
        It takes variants, properties and sale prices into account, though.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        object = self.product

        if object.is_product_with_variants() and object.get_default_variant():
            object = object.get_default_variant()

        if object.get_for_sale():
            if object.is_variant() and not object.active_for_sale_price:
                price = object.parent.get_for_sale_price(self.request, with_properties)
            else:
                price = object.get_for_sale_price(self.request, with_properties)
        else:
            if object.is_variant() and not object.active_price:
                price = object.parent.price
            else:
                price = object.price

        return price

    def get_price_net(self, with_properties=True, amount=1):
        """
        Returns the net price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        raise NotImplementedError

    def get_price_gross(self, with_properties=True, amount=1):
        """
        Returns the real gross price of the product. This is the base of
        all price and tax calculations.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        raise NotImplementedError

    def get_standard_price(self, with_properties=True, amount=1):
        """
        Returns always the stored standard price for the product. Independent
        whether the product is for sale or not. If you want the real price of
        the product use ``get_price`` instead.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        object = self.product

        if object.is_product_with_variants() and object.get_default_variant():
            object = object.get_default_variant()

        if object.is_variant() and not object.active_price:
            object = object.parent

        price = object.price
        if with_properties and object.is_configurable_product():
            price += object.get_default_properties_price()

        return price

    def get_standard_price_net(self, with_properties=True, amount=1):
        """
        Returns always the standard net price for the product. Independent
        whether the product is for sale or not. If you want the real net price
        of the product use ``get_price_net`` instead.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        raise NotImplementedError

    def get_standard_price_gross(self, with_properties=True, amount=1):
        """
        Returns always the gross standard price for the product. Independent
        whether the product is for sale or not. If you want the real gross
        price of the product use ``get_price_gross`` instead.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        raise NotImplementedError

    def get_for_sale_price(self, with_properties=True, amount=1):
        """
        Returns the sale price for the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        object = self.product

        if object.is_product_with_variants() and object.get_default_variant():
            object = object.get_default_variant()

        if object.is_variant() and not object.active_for_sale_price:
            object = object.parent

        price = object.for_sale_price
        if with_properties and object.is_configurable_product():
            price += object.get_default_properties_price()

        return price

    def get_for_sale_price_net(self, with_properties=True, amount=1):
        """
        Returns the sale net price for the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        raise NotImplementedError

    def get_for_sale_price_gross(self, with_properties=True, amount=1):
        """
        Returns the sale net price for the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        raise NotImplementedError

    def get_base_price(self, with_properties=True, amount=1):
        """
        Returns the base price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        try:
            return self.get_price(with_properties, amount) / self.product.get_base_price_amount()
        except (TypeError, ZeroDivisionError):
            return 0.0

    def get_base_price_net(self, with_properties=True, amount=1):
        """
        Returns the net base price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        try:
            return self.get_price_net(with_properties, amount) / self.product.get_base_price_amount()
        except (TypeError, ZeroDivisionError):
            return 0.0

    def get_base_price_gross(self, with_properties=True, amount=1):
        """
        Returns the gross base price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        try:
            return self.get_price_gross(with_properties, amount) / self.product.get_base_price_amount()
        except (TypeError, ZeroDivisionError):
            return 0.0

    def get_base_packing_price(self, with_properties=True, amount=1):
        """
        Returns the base packing price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        return self.get_price(with_properties, amount) * self._calc_packing_amount()

    def get_base_packing_price_net(self, with_properties=True, amount=1):
        """
        Returns the base packing net price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        return self.get_price_net(with_properties, amount) * self._calc_packing_amount()

    def get_base_packing_price_gross(self, with_properties=True, amount=1):
        """
        Returns the base packing gross price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

        amount
            The amount of products for which the price is calculated.
        """
        return self.get_price_gross(with_properties, amount) * self._calc_packing_amount()

    def get_customer_tax_rate(self):
        """
        Returns the tax rate for the current customer and product.
        """
        from lfs.customer_tax.utils import get_customer_tax_rate
        return get_customer_tax_rate(self.request, self.product)

    def get_customer_tax(self, with_properties=True, amount=1):
        """
        Returns the calculated tax for the current customer and product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the taxes of the default properties are added to the price.

        amount
            The amount of products for which the tax is calculated.
        """
        return self.get_price_gross(with_properties, amount) - self.get_price_net(with_properties, amount)

    def get_product_tax_rate(self):
        """
        Returns the stored tax rate of the product. If the product is a variant
        it returns the parent's tax rate.
        """
        from django.core.cache import cache
        if self.product.is_variant():
            obj = self.product.parent
        else:
            obj = self.product

        if obj.tax_id:
            cache_key = u'tax_rate_{}'.format(obj.tax_id)
            tax_rate = cache.get(cache_key)
            if tax_rate is None:
                tax_rate = obj.tax.rate
                cache.set(cache_key, tax_rate)
            return tax_rate
        return 0.0

    def get_product_tax(self, with_properties=True):
        """
        Returns the calculated tax for the current product independent of the
        customer.
        """
        raise NotImplementedError

    def price_includes_tax(self):
        """
        Returns True if stored price includes tax. False if not.
        """
        raise NotImplementedError

    def _calc_product_tax_rate(self):
        """
        Returns the default tax rate for the product.
        """
        tax_rate = self.get_product_tax_rate()
        return ((tax_rate + 100.0) / 100.0)

    def _calc_customer_tax_rate(self):
        """
        Returns the tax rate for the current customer.
        """
        return (self.get_customer_tax_rate() + 100.0) / 100.0

    def _calc_packing_amount(self):
        packing_amount, packing_unit = self.product.get_packing_info()
        if not packing_amount:
            return 1
        packs = math.ceil(1 / packing_amount)

        return packs * packing_amount


class ShippingMethodPriceCalculator(object):
    """
    Base class from which all 3rd-party shipping method prices should inherit.

    **Attributes:**

    request
        The current request.

    shipping_method
        The shipping method for which the price is calculated.
    """
    def __init__(self, request, shipping_method):
        self.shipping_method = shipping_method
        self.request = request

    def get_tax_rate(self):
        from lfs.criteria.utils import get_first_valid
        from lfs.customer_tax.models import CustomerTax
        from django.core.cache import cache

        customer_tax = get_first_valid(self.request, CustomerTax.objects.all(), self.shipping_method)
        if customer_tax:
            return customer_tax.rate

        cache_key = 'shipping_method_tax_{}'.format(self.shipping_method.pk)
        tax_rate = cache.get(cache_key)
        if tax_rate is None:
            if self.shipping_method.tax_id is None:
                tax_rate = 0
            else:
                tax_rate = self.shipping_method.tax.rate
            cache.set(cache_key, tax_rate, 60)
        return tax_rate

    def get_price(self):
        """
        Returns the stored price without any calculations.
        """
        from lfs.criteria import utils as criteria_utils
        price = criteria_utils.get_first_valid(self.request,
                                               self.shipping_method.prices.all())
        if price:
            return price.price
        return self.shipping_method.price

    def get_price_net(self):
        """
        Returns the net price of the shipping method.
        """
        raise NotImplementedError

    def get_price_gross(self):
        """
        Returns the gross price of the shipping method.
        """
        raise NotImplementedError

    def get_tax(self):
        """
        Returns the total tax of the shipping method.
        """
        return self.get_price_gross() - self.get_price_net()
