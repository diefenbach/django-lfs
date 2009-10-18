# django imports
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.catalog.models import Product

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
    amount = models.IntegerField(_(u"Quantity"), blank=True, null=True)
    creation_date = models.DateTimeField(_(u"Creation date"), auto_now_add=True)
    modification_date = models.DateTimeField(_(u"Modification date"), auto_now=True, auto_now_add=True)

    class Meta:
        ordering = ['id']

    def get_price(self):
        """
        """
        return self.get_price_gross()

    def get_price_net(self):
        """Returns the total price of the cart item, which is just the
        multiplication of the product's price and the amount of the product
        within in the cart.
        """
        return self.product.get_price_net() * self.amount

    def get_price_gross(self):
        """Returns the gross price of the product.
        """
        return self.product.get_price_gross() * self.amount

    def get_tax(self):
        """Returns the absolute tax of the product.
        """
        return self.product.get_tax() * self.amount