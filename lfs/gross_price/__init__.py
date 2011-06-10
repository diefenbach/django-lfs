from lfs.price import PriceCalculator


class GrossPriceCalculator(PriceCalculator):

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
            price += self._get_default_properties_price(object)

        return price

    def get_for_sale_price(self):
        """returns the sale price for the product.
        """
        object = self.product

        if object.is_product_with_variants() and object.get_default_variant():
            object = object.get_default_variant()

        if object.is_variant() and not object.active_for_sale_price:
            object = object.parent

        return object.for_sale_price

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
                price = object.parent._get_for_sale_price()
            else:
                price = object._get_for_sale_price()
        else:
            if object.is_variant() and not object.active_price:
                price = object.parent.price
            else:
                price = object.price

        if with_properties and object.is_configurable_product():
            price += self._get_default_properties_price(object)

        return price

    def get_price_with_unit(self):
        """Returns the formatted gross price of the product
        """
        from lfs.core.templatetags.lfs_tags import currency
        price = currency(self.product.get_price())

        if self.product.price_unit:
            price += " / " + self.product.price_unit

        return price

    def calculate_price(self, price):
        """Calulates the price by given entered price calculation.
        """
        pc = self.product.price_calculation
        tokens = self.product.price_calculation.split(" ")

        for token in tokens:
            if token.startswith("property"):
                mo = re.match("property\((\d+)\)")
                ppv = ProductPropertyValue.objects.get(product=self.product, property_id=mo.groups()[0])

        try:
            mult = float(self.product.price_calculation)
        except:
            mult = 1

        return mult * price

    def get_price_net(self):
        """Returns the real net price of the product. Takes care whether the
        product is for sale.
        """
        return self.product.get_price_gross() - self.product.get_tax()

