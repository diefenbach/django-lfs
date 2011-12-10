# python imports
import re

# lfs imports
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.settings import VARIANT
from lfs.plugins import PriceCalculator


class NetPriceCalculator(PriceCalculator):
    """The value of product.price stored in the database excludes tax.
    """
    def get_price(self, with_properties=True):
        """See lfs.plugins.
        """
        return self.get_price_net(with_properties)

    def get_standard_price(self, with_properties=True):
        """See lfs.plugins.
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

    def get_for_sale_price(self):
        """See lfs.plugins.
        """
        object = self.product

        if object.is_product_with_variants() and object.get_default_variant():
            object = object.get_default_variant()

        if object.is_variant() and not object.active_for_sale_price:
            object = object.parent

        return object.for_sale_price

    def get_price_gross(self, with_properties=True):
        """See lfs.plugins.
        """
        return self.product.get_price_net(with_properties) + self.product.get_tax(self.request)

    def get_price_with_unit(self):
        """See lfs.plugins.
        """
        from lfs.core.templatetags.lfs_tags import currency
        price = currency(self.get_price())

        if self.product.price_unit:
            price += " / " + self.product.price_unit

        return price

    def get_price_net(self, with_properties=True):
        """See lfs.plugins.
        """
        object = self.product
        price = object.price

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

    def price_includes_tax(self):
        """See lfs.plugins.
        """
        return False

    def get_tax_rate(self):
        """See lfs.plugins.
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

    def get_tax(self):
        """See lfs.plugins.
        """
        tax_rate = self.get_tax_rate()
        return (tax_rate / 100) * self.get_price_net(self.request)
