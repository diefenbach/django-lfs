# django imports
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

# lfs imports
from lfs.criteria.base import Criteria
from lfs.catalog.models import DeliveryTime
from lfs.core.utils import import_symbol
from lfs.tax.models import Tax

# Load logger
import logging

logger = logging.getLogger(__name__)


class ActiveShippingMethodManager(models.Manager):
    """
    A manager which return just active shipping methods.
    """

    def active(self):
        return super(ActiveShippingMethodManager, self).get_queryset().filter(active=True)


class ShippingMethod(models.Model, Criteria):
    """
    Decides how bought products are delivered to the customer.

    name
        The name of the shipping method. This is displayed to the customer to
        choose the shipping method.

    description
        A longer description of the shipping method. This could be displayed to
        the customer to describe the shipping method in detail.

    note
        This is displayed to the customer within the checkout process and should
        contain a short note about the shipping method.

    priority
        The order in which the shipping methods are displayed to the customer.

    image
        An image of the shipping method, which is displayed to customer within
        the checkout process.

    active
        A flag which decides whether a shipping method is displayed to the
        customer or not.

    tax
        The tax of the shipping method.

    price
        The default price of the shipping method. This is taken if the shipping
        method either has no additional prices or if none of he additional prices
        is valid.

    criteria
        A shipping method may have several criteria which decide whether the
        shipping method is valid. It is valid if all criteria are true. Only
        active and valid shipping methods are provided to the shop customer.

    delivery_time
       Reference to a delivery_time
    """

    active = models.BooleanField(_("Active"), default=False)
    priority = models.IntegerField(_("Priority"), default=0)
    name = models.CharField(_("Name"), max_length=50)
    description = models.TextField(_("Description"), blank=True)
    note = models.TextField(_("Note"), blank=True)
    image = models.ImageField(_("Image"), upload_to="images", blank=True, null=True)
    tax = models.ForeignKey(Tax, models.SET_NULL, verbose_name=_("Tax"), blank=True, null=True)
    price = models.FloatField(_("Price"), default=0.0)
    delivery_time = models.ForeignKey(
        DeliveryTime, models.SET_NULL, verbose_name=_("Delivery time"), blank=True, null=True
    )
    price_calculator = models.CharField(
        _("Price Calculator"),
        max_length=200,
        choices=settings.LFS_SHIPPING_METHOD_PRICE_CALCULATORS,
        default=settings.LFS_SHIPPING_METHOD_PRICE_CALCULATORS[0][0],
    )

    objects = ActiveShippingMethodManager()

    class Meta:
        ordering = ("priority",)
        app_label = "shipping"

    def __str__(self):
        return self.name

    def get_price(self, request):
        """
        Returns the gross price of the shipping method.
        """
        if self.price_calculator:
            price_class = import_symbol(self.price_calculator)
            return price_class(request, self).get_price()
        else:
            return self.price

    def get_price_gross(self, request):
        """
        Returns the default price of the shipping method.
        """
        if self.price_calculator:
            price_class = import_symbol(self.price_calculator)
            return price_class(request, self).get_price_gross()
        else:
            return self.price

    def get_price_net(self, request):
        """
        Returns the default price of the shipping method.
        """
        if self.price_calculator:
            price_class = import_symbol(self.price_calculator)
            return price_class(request, self).get_price_net()
        else:
            return self.price

    def get_tax(self, request):
        """
        Returns the absolute tax of the shipping method.
        """
        if self.price_calculator:
            price_class = import_symbol(self.price_calculator)
            return price_class(request, self).get_tax()
        else:
            # TODO: this should be tax not tax rate
            return 0.0


class ShippingMethodPrice(models.Model, Criteria):
    """
    An additional price for a shipping method.

    shipping_method
        The shipping method to which the price belongs to.

    price
        The actual price, which will be billed to the shop customer

    priority
        The order in which all prices of the belonging shipping method are
        tested for validity. Less comes first.

    active
        If set to True the shipping price is active. Otherwise it is not active
        and hence not considered with the calculation of the price. Not used at
        the moment within the GUI. Every price is active immediately.
    """

    shipping_method = models.ForeignKey(
        ShippingMethod, models.CASCADE, verbose_name=_("shipping_method"), related_name="prices"
    )
    price = models.FloatField(_("Price"), default=0.0)
    priority = models.IntegerField(_("Priority"), default=0)
    active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ("priority",)
        app_label = "shipping"

    def __str__(self):
        return "%s" % self.price
