# django imports
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lfs.payment.models import CriteriaObjects
from lfs.catalog.models import DeliveryTime

from lfs.tax.models import Tax


class ActiveShippingMethodManager(models.Manager):
    """A manager which return just active shipping methods.
    """
    def active(self):
        return super(ActiveShippingMethodManager, self).get_query_set().filter(active=True)


class ShippingMethod(models.Model):
    """Decides how bought products are delivered to the customer.

    Instance variables:

    - name
       The name of the shipping method. This is displayed to the customer to
       choose the shipping method.
    - description
       A longer description of the shipping method. This could be displayed to
       the customer to describe the shipping method in detail.
    - note
       This is displayed to the customer within the checkout process and should
       contain a short note about the shipping method.
    - priority
       The order in which the shipping methods are displayed to the customer.
    - image
       An image of the shipping method, which is displayed to customer within
       the checkout process.
    - active
       A flag which decides whether a shipping method is displayed to the
       customer or not.
    - tax
       The tax of the shipping method.
    - price
       The default price of the shipping method. This is taken if the shipping
       method either has no additional prices or if none of he additional prices
       is valid.
    - criteria_objects
       A shipping method may have several criteria which decide whether the
       shipping method is valid. It is valid if all criteria are true. Only
       active and valid shipping methods are provided to the shop customer.

    - delivery_time
       Reference to a delivery_time
    """
    active = models.BooleanField(_(u"Active"), default=False)
    priority = models.IntegerField(_(u"Priority"), default=0)
    name = models.CharField(_(u"Name"), max_length=50)
    description = models.TextField(_(u"Description"), blank=True)
    note = models.TextField(_(u"Note"), blank=True)
    image = models.ImageField(_(u"Image"), upload_to="images", blank=True, null=True)
    tax = models.ForeignKey(Tax, verbose_name=_(u"Tax"), blank=True, null=True)
    price = models.FloatField(_(u"Price"), default=0.0)
    delivery_time = models.ForeignKey(DeliveryTime, verbose_name=_(u"Delivery time"), blank=True, null=True)

    criteria_objects = generic.GenericRelation(CriteriaObjects,
        object_id_field="content_id", content_type_field="content_type")

    objects = ActiveShippingMethodManager()

    class Meta:
        ordering = ("priority", )

    def __unicode__(self):
        return self.name

    def is_valid(self, request, product=None):
        """The shipping method is valid if it has no criteria or if all assigned
        criteria are true.

        If product is given the product is tested otherwise the whole cart.
        """
        from lfs.criteria import utils as criteria_utils
        return criteria_utils.is_valid(self, request, product)


class ShippingMethodPrice(models.Model):
    """An additional price for a shipping method.

    Instance variables:

    - shipping_method
       The shipping method to which the price belongs to.
    - price
       The actual price, which will be billed to the shop customer
    - priority
       The order in which all prices of the belonging shipping method are tested
       for validity. Less comes first.
    - active
       If set to True the shipping price is active. Otherwise it is not active
       and hence not considered with the calculation of the price. Not used at
       the moment within the GUI. Every price is active immediately.
    - criteria_objects
       A shipping method price may have some criteria. Only when all criteria
       are true the price is valid. The first valid price is the actual price of
       the belonging shipping method.
    """

    shipping_method = models.ForeignKey(ShippingMethod, verbose_name=_(u"shipping_method"), related_name="prices")
    price = models.FloatField(_(u"Price"), default=0.0)
    priority = models.IntegerField(_(u"Priority"), default=0)

    # NOTE: At the moment the active attribute is not used within the GUI.
    # We set it to True by default so every added shipping price is active immediately
    active = models.BooleanField(_(u"Active"), default=True)

    criteria_objects = generic.GenericRelation(CriteriaObjects,
        object_id_field="content_id", content_type_field="content_type")

    class Meta:
        ordering = ("priority", )

    def __unicode__(self):
        return "%s" % self.price

    def is_valid(self, request, product=None):
        """The shipping price is valid if it has no criteria or if all assigned
        criteria are true.

        If product is given the product is tested otherwise the whole cart.
        """
        return criteria_utils.is_valid(self, request, product)
