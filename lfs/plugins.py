# django imports
from django.db import models

# lfs imports
import lfs


class OrderNumberGenerator(models.Model):
    """This is the base class that order generator calculators should inherit
    from.

    **Attributes**:

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
        Returns the next order number. Order number generators must
        implement this method.

        **Parameters:**

        formatted
            If True the number will be returned within the stored format.

        **Return value**
            An order number which must be a character string.
        """
        raise NotImplementedError


class PriceCalculator(object):
    """
    This is the base class that pricing calculators must inherit from.
    """
    def __init__(self, request, product, **kwargs):
        self.request = request
        self.product = product

    def get_price(self, with_properties=True):
        """
        Returns the stored price of the product without any tax calculations.
        It takes variants, properties and sale prices into account, though.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.
        """
        object = self.product

        if object.is_product_with_variants() and object.get_default_variant():
            object = object.get_default_variant()

        if object.get_for_sale():
            if object.is_variant() and not object.active_for_sale_price:
                price = object.parent.get_for_sale_price(self.request)
            else:
                price = object.get_for_sale_price(self.request)
        else:
            if object.is_variant() and not object.active_price:
                price = object.parent.price
            else:
                price = object.price

        if with_properties and object.is_configurable_product():
            price += object.get_default_properties_price()

        return price

    def get_price_net(self, with_properties=True):
        """
        Returns the net price of the product.
        """
        raise NotImplementedError

    def get_price_gross(self, with_properties=True):
        """
        Returns the real gross price of the product. This is the base of
        all price and tax calculations.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.
        """
        raise NotImplementedError

    def get_standard_price(self, with_properties=True):
        """
        Returns always the standard price for the product. Independent
        whether the product is for sale or not. If you want the real price of
        the product use get_price instead.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.
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

    def get_standard_price_net(self, with_properties):
        """
        Returns always the standard net price for the product. Independent
        whether the product is for sale or not. If you want the real net price
        of the product use get_price_net instead.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.
        """
        raise NotImplementedError

    def get_standard_price_gross(self, with_properties):
        """
        Returns always the gros standard price for the product. Independent
        whether the product is for sale or not. If you want the real gross
        price of the product use get_price_gross instead.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.
        """
        raise NotImplementedError

    def get_for_sale_price(self, with_properties):
        """
        Returns the sale price for the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.
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

    def get_for_sale_price_net(self, with_properties):
        """
        Returns the sale net price for the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.
        """
        raise NotImplementedError

    def get_for_sale_price_gross(self, with_properties):
        """
        Returns the sale net price for the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.
        """
        raise NotImplementedError

    def get_customer_tax_rate(self):
        """
        Returns the tax rate for the current customer and product.
        """
        from lfs.customer_tax.utils import get_customer_tax_rate
        return get_customer_tax_rate(self.request, self.product)

    def get_customer_tax(self, with_properties=True):
        """
        Returns the calculated tax for the current customer and product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the taxes of the default properties are added to the price.
        """
        return self.get_price_gross(with_properties) - self.get_price_net(with_properties)

    def get_product_tax_rate(self):
        """
        Returns the stored tax rate of the product. If the product is a
        variant it returns the parent's tax rate.
        """
        if self.product.is_variant():
            obj = self.product.parent
        else:
            obj = self.product

        try:
            return obj.tax.rate
        except AttributeError:
            return 0.0

    def get_product_tax(self):
        """
        Returns the calculated tax for the current product independent of the
        customer.
        """
        return self.get_price(with_properties) - self.get_price(with_properties)

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
