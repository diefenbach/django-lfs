# django imports
from django.db import models

# lfs imports
import lfs


class PriceCalculator(object):
    """
    This is the base class that pricing calculators must inherit from.
    """
    def __init__(self, request, product, **kwargs):
        self.request = request
        self.product = product

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
        raise NotImplementedError

    def get_price(self, with_properties=True):
        """
        Returns the real price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.
        """
        raise NotImplementedError

    def get_for_sale_price(self):
        """
        Returns the sale price for the product.
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

    def get_price_with_unit(self):
        """
        Returns the formatted gross price of the product.
        """
        raise NotImplementedError

    def get_price_net(self, with_properties=True):
        """
        Returns the net price of the product.
        """
        raise NotImplementedError

    def price_includes_tax(self):
        """
        Returns True if stored price includes tax. False if not.
        """
        raise NotImplementedError

    def get_tax_rate(self):
        """
        Returns the tax rate of the product.
        """
        raise NotImplementedError

    def get_tax(self):
        """
        Returns the absolute tax of the product.
        """
        raise NotImplementedError


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
