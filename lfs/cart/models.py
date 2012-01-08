# python imports
import re

# django imports
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.catalog.utils
from lfs.catalog.models import Product
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption

# Load logger
import logging
logger = logging.getLogger("default")


class Cart(models.Model):
    """
    A cart is a container for products which are supposed to be bought by a
    shop customer.

    **Attributes**

    user
       The user to which the cart belongs to

    session
       The session to which the cart belongs to

    creation_date
        The creation date of the cart

    modification_date
        The modification date of the cart

    A cart can be assigned either to the current logged in User (in case
    the shop user is logged in) or to the current session (in case the shop
    user is not logged in).

    A cart is only created if it needs to, i.e. when the shop user adds
    something to the cart.
    """
    user = models.ForeignKey(User, verbose_name=_(u"User"), blank=True, null=True)
    session = models.CharField(_(u"Session"), blank=True, max_length=100)
    creation_date = models.DateTimeField(_(u"Creation date"), auto_now_add=True)
    modification_date = models.DateTimeField(_(u"Modification date"), auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return "%s, %s" % (self.user, self.session)

    # DDD
    @property
    def amount_of_items(self):
        """
        Returns the amount of items of the cart.

        This method is DEPRECATED.
        """
        logger.info("Decprecated: lfs.cart.models.Cart: the property 'amount_of_items' is deprecated. Please use 'get_amount_of_items'.")
        return self.get_amount_of_items()

    # DDD
    def items(self):
        """
        Returns the items of the cart.

        This method is DEPRECATED.
        """
        logger.info("Decprecated: lfs.cart.models.Cart: the method 'items' is deprecated. Please use 'get_items'.")
        return self.get_items()

    # DDD
    def get_name(self):
        """
        Returns a name for the cart.

        This method is DEPRECATED.
        """
        logger.info("Decprecated: lfs.cart.models.Cart: the method 'get_name' is deprecated. (There is no replacement as this method makes no sense at all.)")
        cart_name = ""
        for cart_item in self.items.all():
            if cart_name.product is not None:
                cart_name = cart_name + cart_name.product.get_name() + ", "

        cart_name.strip(', ')
        return cart_name

    def add(self, product, properties=None, amount=1):
        """
        Adds passed product to the cart.

        **Parameters**

        product
            The product which is added.

        properties
            The properties which have been selected by the shop customer
            for the product.

        Returns the newly created cart item.
        """
        if product.is_configurable_product():
            cart_item = self.get_item(product, properties)
            if cart_item:
                cart_item.amount += amount
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(cart=self, product=product, amount=amount)
                if properties:
                    for property_id, value in properties.items():
                        try:
                            Property.objects.get(pk=property_id)
                        except Property.DoesNotExist:
                            pass
                        else:
                            CartItemPropertyValue.objects.create(cart_item=cart_item, property_id=property_id, value=value)
        else:
            try:
                cart_item = CartItem.objects.get(cart=self, product=product)
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(cart=self, product=product, amount=amount)
            else:
                cart_item.amount += amount
                cart_item.save()

        return cart_item

    def get_amount_of_items(self):
        """
        Returns the amount of items of the cart.
        """
        amount = 0
        for item in self.get_items():
            amount += item.amount
        return amount

    def get_item(self, product, properties):
        """
        Returns the item for passed product and properties or None if there
        is none.
        """
        for item in CartItem.objects.filter(cart=self, product=product):
            item_props = {}
            for pv in item.properties.all():
                item_props[unicode(pv.property.id)] = pv.value

            if item_props == properties:
                return item

        return None

    def get_items(self):
        """
        Returns the items of the cart.
        """
        cache_key = "%s-cart-items-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        items = cache.get(cache_key)
        if items is None:
            items = CartItem.objects.filter(cart=self)
            cache.set(cache_key, items)
        return items

    def get_delivery_time(self, request):
        """
        Returns the delivery time object with the maximal delivery time of all
        products within the cart. Takes the selected shipping method into account.
        """
        import lfs.shipping.utils
        max_delivery_time = None
        for item in self.get_items():
            delivery_time = lfs.shipping.utils.get_product_delivery_time(request, item.product.slug, for_cart=True)
            if (max_delivery_time is None) or (delivery_time.as_hours() > max_delivery_time.as_hours()):
                max_delivery_time = delivery_time
        return max_delivery_time

    def get_price_gross(self, request, total=False):
        """Returns the total gross price of all items.
        """
        price = 0
        for item in self.get_items():
            price += item.get_price_gross(request)
        return price

    def get_price_net(self, request):
        """Returns the total net price of all items.
        """
        price = 0
        for item in self.get_items():
            price += item.get_price_net(request)

        return price

    def get_tax(self, request):
        """Returns the total tax of all items
        """
        tax = 0
        for item in self.get_items():
            tax += item.get_tax(request)

        return tax


class CartItem(models.Model):
    """
    A cart item belongs to a cart. It stores the product and the amount of the
    product which has been taken into the cart.

    **Attributes**

    cart
        The cart the cart item belongs to.

    product
        A reference to a product which is supposed to be bought.

    amount
       Amount of the product which is supposed to be bought.

    creation_date
        The creation date of the cart item.

    modification_date
        The modification date of the cart item.
    """
    cart = models.ForeignKey(Cart, verbose_name=_(u"Cart"))
    product = models.ForeignKey(Product, verbose_name=_(u"Product"))
    amount = models.FloatField(_(u"Quantity"), blank=True, null=True)
    creation_date = models.DateTimeField(_(u"Creation date"), auto_now_add=True)
    modification_date = models.DateTimeField(_(u"Modification date"), auto_now=True, auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return "Product: %s, Quantity: %f, Cart: %s" % (self.product, self.amount, self.cart)

    # DDD
    def get_price(self, request):
        """
        Convenient method to return the gross price of the product.
        """
        logger.info("Decprecated: lfs.cart.models.CartItem: the method 'get_price' is deprecated. Please use the methods 'get_price_gross' and 'get_price_net'.")
        return self.get_price_gross(request)

    def get_price_net(self, request):
        """
        Returns the total price of the cart item, which is just the multiplication
        of the product's price and the amount of the product within in the cart.
        """
        return self.get_price_gross(request) - self.get_tax(request)

    def get_price_gross(self, request):
        """
        Returns the gross item price.
        """
        return self.get_product_price_gross(request) * self.amount

    def get_product_price_gross(self, request):
        """
        Returns the product item price. Based on selected properties, etc.
        """
        if not self.product.is_configurable_product():
            price = self.product.get_price_gross(request)
        else:
            if self.product.active_price_calculation:
                try:
                    price = self.get_calculated_price(request)
                except:
                    price = self.product.get_price_gross(request)
            else:
                price = self.product.get_price_gross(request, with_properties=False)
                for property in self.properties.all():
                    if property.property.is_select_field:
                        try:
                            option = PropertyOption.objects.get(pk=int(float(property.value)))
                        except (PropertyOption.DoesNotExist, AttributeError, ValueError):
                            pass
                        else:
                            try:
                                option_price = float(option.price)
                            except (TypeError, ValueError):
                                pass
                            else:
                                if not self.product.price_includes_tax():
                                    option_price = option_price * ((100 + self.product.get_tax_rate(request)) / 100)
                                price += option_price
        return price

    def get_calculated_price(self, request):
        """
        Returns the calculated gross price of the product based on property
        values and the price calculation field of the product.
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

    def get_tax(self, request):
        """
        Returns the absolute tax of the item.
        """
        rate = self.product.get_tax_rate(request)
        return self.get_price_gross(request) * (rate / (rate + 100))

    def get_properties(self):
        """
        Returns properties of the cart item. Resolves option names for select
        fields.
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
                "name": property.name,
                "title": property.title,
                "unit": property.unit,
                "display_price": property.display_price,
                "value": value,
                "price": price,
            })

        return properties


class CartItemPropertyValue(models.Model):
    """
    Stores a value for a property and item.

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
    property = models.ForeignKey(Property, verbose_name=_(u"Property"))
    value = models.CharField("Value", blank=True, max_length=100)
