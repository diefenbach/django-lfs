import re
import locale
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lfs.catalog.models import Product, PropertyGroup
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption


logger = logging.getLogger(__name__)


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
    modification_date = models.DateTimeField(_(u"Modification date"), auto_now=True)

    def __unicode__(self):
        return u"%s, %s" % (self.user, self.session)

    def add(self, product, properties_dict=None, amount=1):
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
            cart_item = self.get_item(product, properties_dict)
            if cart_item:
                cart_item.amount += amount
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(cart=self, product=product, amount=amount)
                if properties_dict:
                    for key, item in properties_dict.items():
                        property_id = item['property_id']
                        property_group_id = item['property_group_id'] if item['property_group_id'] != '0' else None
                        value = item['value']
                        try:
                            Property.objects.get(pk=property_id)
                        except Property.DoesNotExist:
                            pass
                        else:
                            CartItemPropertyValue.objects.create(cart_item=cart_item,
                                                                 property_group_id=property_group_id,
                                                                 property_id=property_id,
                                                                 value=value)
        else:
            try:
                cart_item = CartItem.objects.get(cart=self, product=product)
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(cart=self, product=product, amount=amount)
            else:
                cart_item.amount += float(amount)
                cart_item.save()

        cache_key = "%s-cart-items-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        cache.delete(cache_key)

        return cart_item

    def get_amount_of_items(self):
        """
        Returns the amount of items of the cart.
        """
        amount = 0
        for item in self.get_items():
            amount += item.amount
        return amount

    def get_item(self, product, properties_dict):
        """
        Returns the item for passed product and properties or None if there
        is none.
        """
        properties_dict_keys = ['{0}_{1}_{2}'.format(item['property_group_id'],
                                                     item['property_id'],
                                                     item['value']) for item in properties_dict.values()]
        properties_dict_keys = sorted(properties_dict_keys)
        properties_dict_key = '-'.join(properties_dict_keys)
        for item in CartItem.objects.filter(cart=self, product=product):
            item_props = []
            for pv in item.properties.all():
                property_group_id = pv.property_group_id if pv.property_group_id else '0'
                key = '{0}_{1}_{2}'.format(property_group_id, pv.property_id, pv.value)
                item_props.append(key)
            item_props = sorted(item_props)
            item_props_key = '-'.join(item_props)
            if item_props_key == properties_dict_key:
                return item

        return None

    def get_items(self):
        """
        Returns the items of the cart.
        """
        self._update_product_amounts()
        cache_key = "%s-cart-items-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        items = cache.get(cache_key)
        if items is None:
            items = CartItem.objects.select_related().filter(cart=self, product__active=True)
            # items = CartItem.objects.filter(cart=self)
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
            delivery_time = lfs.shipping.utils.get_product_delivery_time(request, item.product, for_cart=True)
            if (max_delivery_time is None) or (delivery_time.as_hours() > max_delivery_time.as_hours()):
                max_delivery_time = delivery_time
        return max_delivery_time

    def get_price_gross(self, request, total=False):
        """
        Returns the total gross price of all items.
        """
        price = 0
        for item in self.get_items():
            price += item.get_price_gross(request)
        return price

    def get_price_net(self, request):
        """
        Returns the total net price of all items.
        """
        price = 0
        for item in self.get_items():
            price += item.get_price_net(request)

        return price

    def get_tax(self, request):
        """
        Returns the total tax of all items
        """
        tax = 0
        for item in self.get_items():
            tax += item.get_tax(request)

        return tax

    def _update_product_amounts(self):
        items = CartItem.objects.select_related('product').filter(cart=self,
                                                                  product__active=True,
                                                                  product__manage_stock_amount=True)
        updated = False
        for item in items:
            if item.amount > item.product.stock_amount and not item.product.order_time:
                if item.product.stock_amount == 0:
                    item.delete()
                else:
                    item.amount = item.product.stock_amount
                    item.save()
                updated = True
        if updated:
            cache_key = "%s-cart-items-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
            cache.delete(cache_key)

    class Meta:
        app_label = 'cart'


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
    modification_date = models.DateTimeField(_(u"Modification date"), auto_now=True)

    class Meta:
        ordering = ['id']
        app_label = 'cart'

    def __unicode__(self):
        return u"Product: %(product)s, Quantity: %(amount)f, Cart: %(cart)s" % {'product': self.product,
                                                                                'amount': self.amount,
                                                                                'cart': self.cart}

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
            price = self.product.get_price_gross(request, amount=self.amount)
        else:
            if self.product.active_price_calculation:
                try:
                    price = self.get_calculated_price(request)
                except:
                    price = self.product.get_price_gross(request, amount=self.amount)
            else:
                price = self.product.get_price_gross(request, with_properties=False, amount=self.amount)
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
                                if not self.product.price_includes_tax(request):
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
                    value = float(ppv.value)
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
        for prop_dict in self.product.get_properties():
            prop = prop_dict['property']
            property_group = prop_dict['property_group']
            price = ""

            try:
                cipv = CartItemPropertyValue.objects.get(cart_item=self,
                                                         property=prop,
                                                         property_group=property_group)
            except CartItemPropertyValue.DoesNotExist:
                continue

            if prop.is_select_field:
                try:
                    option = PropertyOption.objects.get(pk=int(float(cipv.value)))
                except (PropertyOption.DoesNotExist, ValueError):
                    value = cipv.value
                    price = 0.0
                else:
                    value = option.name
                    price = option.price

            elif prop.is_number_field:
                format_string = "%%.%sf" % prop.decimal_places
                try:
                    value = format_string % float(cipv.value)
                except ValueError:
                    value = locale.format("%.2f", float(cipv.value))
            else:
                value = cipv.value

            properties.append({
                "name": prop.name,
                "title": prop.title,
                "unit": prop.unit,
                "display_price": prop.display_price,
                "value": value,
                "price": price,
                "obj": prop,
                "property_group": property_group,
                "property_group_name": property_group.name
            })

        properties = sorted(properties, key=lambda x: '{0}-{1}'.format(x['property_group_name'], x['obj'].position))
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
    property_group = models.ForeignKey(PropertyGroup, verbose_name=_(u'Property group'), null=True, blank=True)
    value = models.CharField("Value", blank=True, max_length=100)

    class Meta:
        app_label = 'cart'
