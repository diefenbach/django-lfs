# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.catalog.models import Product
import lfs.criteria.utils
from lfs.criteria.base import Criteria
from lfs.discounts.settings import DISCOUNT_TYPE_CHOICES
from lfs.discounts.settings import DISCOUNT_TYPE_ABSOLUTE
from lfs.tax.models import Tax


class Discount(models.Model, Criteria):
    """
    A discount which is given to the customer if several criteria
    fullfilled.

    **Attributes:**

    name
        The name of the discount. This can be displayed to the customer.

    active
        Activate/Deactivate discount

    value
        The value of the discount, can be absolute or percentage dependend on
        the type of the discount.

    type
        The type of the discount. Absolute or percentage.

    tax
        The included tax within the discount.

    sku
        The SKU of the discount.

    sums_up
        Whether discount can be summed up with other discounts/vouchers

    products
        Products that discount applies to

    """
    name = models.CharField(_(u"Name"), max_length=100)
    active = models.BooleanField(_("Active"), default=False)
    value = models.FloatField(_(u"Value"))
    type = models.PositiveSmallIntegerField(_(u"Type"), choices=DISCOUNT_TYPE_CHOICES, default=DISCOUNT_TYPE_ABSOLUTE)
    tax = models.ForeignKey(Tax, verbose_name=_(u"Tax"), blank=True, null=True)
    sku = models.CharField(_(u"SKU"), blank=True, max_length=50)
    sums_up = models.BooleanField(_(u"Sums up"), default=True, help_text=_(u'Sums up with other discounts/vouchers'))
    products = models.ManyToManyField(Product, verbose_name=_(u"Products"), related_name="discounts")

    def __unicode__(self):
        return self.name

    def get_tax(self, request, product=None):
        """Returns the absolute tax of the voucher.
        """
        price_gross = self.get_price_gross(request, product)
        if self.tax:
            return price_gross * (self.tax.rate / (100 + self.tax.rate))
        else:
            if self.type == DISCOUNT_TYPE_ABSOLUTE:
                return 0.0
            else:
                cart = lfs.cart.utils.get_cart(request)
                return cart.get_tax(request) * (self.value / 100)

    def get_price_net(self, request, product=None):
        """Returns the net price of the discount.
        """
        return self.get_price_gross(request, product) - self.get_tax(request, product)

    def get_price_gross(self, request, product=None):
        """Returns the gross price of the discount.
        """
        # if products exists then discount is applied per product
        if self.products.exists():
            cart = lfs.cart.utils.get_cart(request)

            if cart is not None:
                items = cart.get_items()
                total = 0.0
                if items.exists():
                    for item in items.filter(product__in=self.products.all()):
                        if self.type == DISCOUNT_TYPE_ABSOLUTE:
                            total += self.value
                        else:
                            total += item.get_price_gross(request) * (self.value / 100)
                return total

            elif product is not None:
                if self.products.filter(pk=product.pk).exists():
                    return product.get_price_gross(request) * (self.value / 100)

        else:
            if self.type == DISCOUNT_TYPE_ABSOLUTE:
                return self.value

            cart = lfs.cart.utils.get_cart(request)

            if cart is not None:
                return cart.get_price_gross(request) * (self.value / 100)
            elif product is not None:
                return product.get_price_gross(request) * (self.value / 100)

        return 0.0

    def is_valid(self, request, product=None):
        if self.products.exists():
            cart = lfs.cart.utils.get_cart(request)
            items = cart.get_items()
            if not items.filter(product__in=self.products.all()).exists():
                return False
        return super(Discount, self).is_valid(request, product)
