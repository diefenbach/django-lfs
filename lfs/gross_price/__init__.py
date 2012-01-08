import re

from lfs.price import PriceCalculator
from lfs.catalog.settings import VARIANT
from lfs.catalog.models import ProductPropertyValue


class GrossPriceCalculator(PriceCalculator):
    """
    The value of product.price stored in the database includes tax
    """

    def get_price(self, with_properties=True):
        return self.get_price_gross(with_properties)

    def get_standard_price(self, with_properties=True):
        """Returns always the standard price for the product. Independent
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

    def get_for_sale_price(self, with_properties=True):
        """returns the sale price for the product.
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

    def get_price_gross(self, with_properties=True):
        """Returns the real gross price of the product. This is the base of
        all price and tax calculations.

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
                price = object.parent.get_for_sale_price(self.request, with_properties)
            else:
                price = object.get_for_sale_price(self.request, with_properties)
        else:
            if object.is_variant() and not object.active_price:
                price = object.parent.price
            else:
                price = object.price

            if with_properties and object.is_configurable_product():
                price += object.get_default_properties_price()

        return price

    def get_price_with_unit(self):
        """Returns the formatted gross price of the product
        """
        from lfs.core.templatetags.lfs_tags import currency
        price = currency(self.get_price())

        if self.product.price_unit:
            price += " / " + self.product.price_unit

        return price

    def get_price_net(self, with_properties=True):
        """Returns the real net price of the product. Takes care whether the
        product is for sale.
        """
        return self.product.get_price_gross(self.request, with_properties) - self.product.get_tax(self.request, with_properties)

    def price_includes_tax(self):
        return True

    def get_tax_rate(self):
        """Returns the tax rate of the product.
        """
        if self.product.sub_type == VARIANT:
            if self.product.parent.tax is None:
                return 0.0
            else:
                return self.product.parent.tax.rate
        else:
            if self.product.tax is None:
                return 0.0
            else:
                return self.product.tax.rate

    def get_tax(self, with_properties):
        """Returns the absolute tax of the product.
        """
        tax_rate = self.get_tax_rate()
        return (tax_rate / (tax_rate + 100)) * self.get_price_gross(with_properties)
