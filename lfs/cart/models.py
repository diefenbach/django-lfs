import re

# django imports
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.catalog.utils
from lfs.catalog.models import Product
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption

class Cart(models.Model):
    """A cart is a container for products which are supposed to be bought by a
    shop customer.

    Instance variables:

    - user
       The user to which the cart belongs to
    - session
       The session to which the cart belongs to

    A cart can be assigned either to the current logged in User (in case
    the shop user is logged in) or to the current session (in case the shop user
    is not logged in).

    A cart is only created if it needs to. When the shop user adds something to
    the cart.
    """
    user = models.ForeignKey(User, verbose_name=_(u"User"), blank=True, null=True)
    session = models.CharField(_(u"Session"), blank=True, max_length=100)
    creation_date = models.DateTimeField(_(u"Creation date"), auto_now_add=True)
    modification_date = models.DateTimeField(_(u"Modification date"), auto_now=True, auto_now_add=True)

    def items(self):
        """Returns the items of the cart.
        """
        cache_key = "cart-items-%s" % self.id
        items = cache.get(cache_key)
        if items is None:
            items = CartItem.objects.filter(cart=self)
            cache.set(cache_key, items)
        return items

    @property
    def amount_of_items(self):
        """Returns the amount of items of the cart.
        """
        amount = 0
        for item in self.items():
            amount += item.amount
        return amount

    def get_name(self):
        cart_name = ""
        for cart_item in self.items.all():
            if cart_name.product is not None:
                cart_name = cart_name + cart_name.product.get_name() + ", "

        cart_name.strip(', ')
        return cart_name

    def get_price_gross(self):
        """Returns the total gross price of all items.
        """
        price = 0
        for item in self.items():
            price += item.get_price_gross()

        return price

    def get_price_net(self):
        """Returns the total net price of all items.
        """
        price = 0
        for item in self.items():
            price += item.get_price_net()

        return price

    def get_tax(self):
        """Returns the total tax of all items
        """
        tax = 0
        for item in self.items():
            tax += item.get_tax()

        return tax

    def get_item(self, product, properties):
        """Returns the item for passed product and properties or None if there
        is none.
        """
        for item in CartItem.objects.filter(cart=self, product=product):
            item_props = {}
            for pv in item.properties.all():
                item_props[unicode(pv.property.id)] = pv.value

            if item_props == properties:
                return item

        return None

class CartItem(models.Model):
    """A cart item belongs to a cart. It stores the product and the amount of
    the product which has been taken into the cart.

    Instance variables:

    - product
       A reference to a product which is supposed to be bought
    - amount
       Amount of the product which is supposed to be bought.
    """
    cart = models.ForeignKey(Cart, verbose_name=_(u"Cart"))
    product = models.ForeignKey(Product, verbose_name=_(u"Product"))
    amount = models.FloatField(_(u"Quantity"), blank=True, null=True)
    creation_date = models.DateTimeField(_(u"Creation date"), auto_now_add=True)
    modification_date = models.DateTimeField(_(u"Modification date"), auto_now=True, auto_now_add=True)

    class Meta:
        ordering = ['id']

    def get_price(self):
        """Convenient method to return the gross price of the product.
        """
        return self.get_price_gross()

    def get_price_net(self):
        """Returns the total price of the cart item, which is just the
        multiplication of the product's price and the amount of the product
        within in the cart.
        """
        return self.product.get_price_net() * self.amount

    def get_price_gross(self, standard=False):
        """Returns the gross price of the product.
        """
        if not self.product.is_configurable_product():
            price = self.product.get_price_gross()

            if self.product.active_packing_unit:
                amount = lfs.catalog.utils.calculate_real_amount(self.product, self.amount)
                return self.product.get_price_gross() * amount
        else:
            if self.product.active_price_calculation:
                try:
                    price = self.get_calculated_price()
                except:
                    price = self.product.get_price_gross()
            else:
                price = self.product.get_price_gross()
                for property in self.properties.all():
                    if property.property.is_select_field:
                        try:
                            option = PropertyOption.objects.get(pk=int(float(property.value)))
                        except (PropertyOption.DoesNotExist, AttributeError):
                            pass
                        else:
                            price += option.price
                            
        return price * self.amount

    def get_calculated_price(self):
        """Returns the calculated gross price of the product.
        """
        pc = self.product.price_calculation
        tokens = self.product.price_calculation.split(" ")

        for token in tokens:
            if token.startswith("property"):
                mo = re.match("property\((\d+)\)", token)
                ppv = self.properties.filter(property__id=mo.groups()[0])[0]
                if ppv.property.is_select_field:
                    po = PropertyOption.objects.get(pk=ppv.value)
                    value = po.price
                else:
                    value = ppv.value
                pc = pc.replace(token, str(value))
            elif token.startswith("number"):
                mo = re.match("number\((\d+)\)", token)
                pc = pc.replace(token, mo.groups()[0])
            elif token.startswith("product"):
                mo = re.match("product\((.+)\)", token)
                value = getattr(self.product, mo.groups()[0])
                pc = pc.replace(token, str(value))

        return eval(pc)

    def get_tax(self):
        """Returns the absolute tax of the item.
        """
        rate = self.product.get_tax_rate()
        return self.get_price_gross() * (rate / (rate + 100))

    def get_properties(self):
        """Returns properties of the cart item. Resolves option names for
        select fields.
        """
        properties = []
        for property in self.product.get_properties():
            try:
                cipv = CartItemPropertyValue.objects.get(cart_item=self, property=property)
            except CartItemPropertyValue.DoesNotExist:
                continue

            if property.is_select_field:
                try:
                    option = PropertyOption.objects.get(pk=int(float(cipv.value)))
                except (PropertyOption.DoesNotExist, ValueError):
                    value = cipv.value
                    price = 0.0
                else:
                    value = option.name
                    price = option.price
                
            else:                
                format_string = "%%.%sf" % property.decimal_places
                try:
                    value = format_string % float(cipv.value)
                except ValueError:
                    value = "%.2f" % float(cipv.value)

                price = ""

            properties.append({
                "name" : property.name,
                "title" : property.title,
                "unit" : property.unit,
                "display_price" : property.display_price,
                "value" : value,
                "price" : price
            })

        return properties

class CartItemPropertyValue(models.Model):
    """Stores a value for a property and item.

    **Attributes**

    cart_item
        The cart item - and in this way the product - for which the value
        should be stored.

    property
        The property for which the value should be stored.

    value
        The value which is stored.
    """
    cart_item = models.ForeignKey(CartItem, verbose_name=_(u"Cart item"), related_name="properties")
    property = models.ForeignKey(Property, verbose_name = _(u"Property"))
    value = models.CharField("Value", blank=True, max_length=100)