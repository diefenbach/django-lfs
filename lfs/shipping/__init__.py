# lfs imports
from lfs.plugins import ShippingMethodPriceCalculator


class GrossShippingPriceCalculator(ShippingMethodPriceCalculator):
    """
    ShippingMethodPriceCalculator which considers the entered pirce as gross
    price.

    See lfs.plugins.ShippingMethodPriceCalculator
    """
    def get_price_net(self):
        """See lfs.plugins.ShippingMethodPriceCalculator.
        """
        return self.self.shipping_method.price / ((100 + self.self.shipping_method.tax.rate) / 100)

    def get_price_gross(self):
        """See lfs.plugins.ShippingMethodPriceCalculator.
        """
        return self.shipping_method.price


class NetShippingPriceCalculator(ShippingMethodPriceCalculator):
    """
    ShippingMethodPriceCalculator which considers the entered pirce as net
    price.
    """
    def get_price_net(self):
        """See lfs.plugins.ShippingMethodPriceCalculator.
        """
        return self.self.shipping_method.price

    def get_price_gross(self):
        """See lfs.plugins.ShippingMethodPriceCalculator.
        """
        return self.shipping_method.price * ((100 + self.shipping_method.tax.rate) / 100)
