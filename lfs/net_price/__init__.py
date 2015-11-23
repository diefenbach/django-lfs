# lfs imports
from lfs.plugins import PriceCalculator


class NetPriceCalculator(PriceCalculator):
    """
    The value of product.price stored in the database excludes tax, in other
    words, the stored price is the net price of the product.

    See lfs.plugins.PriceCalculator for more information.
    """
    def get_price_net(self, with_properties=True, amount=1):
        return self.get_price(with_properties, amount)

    def get_price_gross(self, with_properties=True, amount=1):
        return self.get_price_net(with_properties, amount) * self._calc_customer_tax_rate()

    def get_standard_price_net(self, with_properties=True, amount=1):
        return self.get_standard_price(with_properties, amount)

    def get_standard_price_gross(self, with_properties=True, amount=1):
        return self.get_standard_price_net(with_properties, amount) * self._calc_customer_tax_rate()

    def get_for_sale_price_net(self, with_properties=True, amount=1):
        return self.get_for_sale_price(with_properties, amount)

    def get_for_sale_price_gross(self, with_properties=True, amount=1):
        return self.get_for_sale_price_net(with_properties, amount) * self._calc_customer_tax_rate()

    def price_includes_tax(self):
        return False
