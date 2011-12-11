# python imports
import re

# lfs imports
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.settings import VARIANT
from lfs.plugins import PriceCalculator


class NetPriceCalculator(PriceCalculator):
    """The value of product.price stored in the database excludes tax.
    """
    def get_price_net(self, with_properties=True):
        """See lfs.plugins.PriceCalculator
        """
        # stored product price
        return self.get_price(with_properties)

    def get_price_gross(self, with_properties=True):
        """See lfs.plugins.PriceCalculator
        """
        # net price + customer tax
        return self.get_price_net(with_properties) * self._calc_customer_tax_rate()

    def get_standard_price_net(self, with_properties=True):
        """See lfs.plugins.PriceCalculator
        """
        # stored product standard price
        return self.get_standard_price(with_properties)

    def get_standard_price_gross(self, with_properties=True):
        """See lfs.plugins.PriceCalculator
        """
        # net standard price + customer tax
        return self.get_standard_price_net(with_properties) * self._calc_customer_tax_rate()

    def get_for_sale_price_net(self, with_properties=True):
        """See lfs.plugins.PriceCalculator
        """
        # stored for sale product price
        return self.get_for_sale_price(with_properties)

    def get_for_sale_price_gross(self, with_properties=True):
        """See lfs.plugins.PriceCalculator
        """
        # for sale net price + customer tax
        return self.get_for_sale_price_net(with_properties) * self._calc_customer_tax_rate()

    def price_includes_tax(self):
        """See lfs.plugins.PriceCalculator
        """
        return False
