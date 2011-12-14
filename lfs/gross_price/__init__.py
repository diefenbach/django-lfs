# python imports
import re

# lfs imports
from lfs.catalog.settings import VARIANT
from lfs.catalog.models import ProductPropertyValue
from lfs.plugins import PriceCalculator

# Load logger
import logging
logger = logging.getLogger("default")


class GrossPriceCalculator(PriceCalculator):
    """The value of product.price stored in the database includes tax.
    """
    def get_price_net(self, with_properties=True):
        """See lfs.plugins.PriceCalculator
        """
        # price - **product** tax
        return self.get_price(with_properties) / self._calc_product_tax_rate()

    def get_price_gross(self, with_properties=True):
        """See lfs.plugins.PriceCalculator
        """
        # net price + **customer** tax
        return self.get_price_net(with_properties) * self._calc_customer_tax_rate()

    def get_standard_price_net(self, with_properties=True):
        """See lfs.plugins
        """
        # price - **product** tax
        return self.get_standard_price(with_properties) / self._calc_product_tax_rate()

    def get_standard_price_gross(self, with_properties=True):
        """See lfs.plugins
        """
        # price - **product** tax
        return self.get_standard_price_net(with_properties) * self._calc_customer_tax_rate()

    def get_for_sale_price_net(self, with_properties=True):
        """See lfs.plugins
        """
        # price - **product** tax
        return self.get_for_sale_price(with_properties) / self._calc_product_tax_rate()

    def get_for_sale_price_gross(self, with_properties=True):
        """See lfs.plugins
        """
        # price - **product** tax
        return self.get_for_sale_price_net(with_properties) * self._calc_customer_tax_rate()

    def price_includes_tax(self):
        """See lfs.plugins.PriceCalculator
        """
        return True
