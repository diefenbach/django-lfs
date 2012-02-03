# django imports
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.criteria.utils
from lfs.discounts.settings import DISCOUNT_TYPE_CHOICES
from lfs.discounts.settings import DISCOUNT_TYPE_ABSOLUTE
from lfs.discounts.settings import DISCOUNT_TYPE_PERCENTAGE
from lfs.payment.models import CriteriaObjects
from lfs.tax.models import Tax


class Discount(models.Model):
    """A discount which is given to the customer if several criteria
    fullfilled.

    **Attributes:**

    name
        The name of the discount. This can be displayed to the customer.

    value
        The value of the discount, can be absolute or percentage dependend on
        the type of the discount.

    type
        The type of the discount. Absolute or percentage.

    tax
        The included tax within the discount.

    sku
        The SKU of the discount.

    criteria_objects
        Criteria which must all valid to make the discount happen.

    """
    name = models.CharField(_(u"Name"), max_length=100)
    value = models.FloatField(_(u"Value"))
    type = models.PositiveSmallIntegerField(_(u"Type"), choices=DISCOUNT_TYPE_CHOICES, default=DISCOUNT_TYPE_ABSOLUTE)
    tax = models.ForeignKey(Tax, verbose_name=_(u"Tax"), blank=True, null=True)
    sku = models.CharField(_(u"SKU"), blank=True, max_length=50)
    criteria_objects = generic.GenericRelation(CriteriaObjects,
        object_id_field="content_id", content_type_field="content_type")

    def __unicode__(self):
        return self.name

    def is_valid(self, request, product=None):
        """The shipping method is valid if it has no criteria or if all assigned
        criteria are true.

        If product is given the product is tested otherwise the whole cart.
        """
        return lfs.criteria.utils.is_valid(request, self, product)

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
        if self.type == DISCOUNT_TYPE_ABSOLUTE:
            return self.value

        cart = lfs.cart.utils.get_cart(request)

        if cart is not None:
            return cart.get_price_gross(request) * (self.value / 100)
        elif product is not None:
            return product.get_price_gross(request) * (self.value / 100)

        return 0.0
