from lfs.plugins import ShippingMethodPriceCalculator


class GrossShippingMethodPriceCalculator(ShippingMethodPriceCalculator):
    """
    ShippingMethodPriceCalculator which considers the entered price as gross
    price.

    See lfs.plugins.ShippingMethodPriceCalculator
    """
    def get_price_net(self):
        """See lfs.plugins.ShippingMethodPriceCalculator.
        """
        price = self.get_price()
        tax_rate = self.get_tax_rate()
        return price / ((100 + tax_rate) / 100)

    def get_price_gross(self):
        """See lfs.plugins.ShippingMethodPriceCalculator.
        """
        return self.get_price()


class NetShippingMethodPriceCalculator(ShippingMethodPriceCalculator):
    """
    ShippingMethodPriceCalculator which considers the entered price as net
    price.
    """
    def get_price_net(self):
        """See lfs.plugins.ShippingMethodPriceCalculator.
        """
        return self.get_price()

    def get_price_gross(self):
        """See lfs.plugins.ShippingMethodPriceCalculator.
        """
        price = self.get_price()
        tax_rate = self.get_tax_rate()
        return price * ((100 + tax_rate) / 100)
