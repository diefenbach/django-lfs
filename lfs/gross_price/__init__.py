from lfs.price import PriceCalculator


class GrossPriceCalculator(PriceCalculator):

    def get_price_net(self):
        """Returns the real net price of the product. Takes care whether the
        product is for sale.
        """
        return self.product.get_price_gross() - self.product.get_tax()
