# django imports
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.criteria.base import Criteria
import lfs.payment.settings
from lfs.tax.models import Tax


class ActivePaymentMethodManager(models.Manager):
    """
    A manager which return just valid shipping methods.
    """
    def active(self):
        return super(ActivePaymentMethodManager, self).get_query_set().filter(active=True)


class PaymentMethod(models.Model, Criteria):
    """
    Payment methods are provided to the customer to select the kind of how
    products are paid.

    A payment method may have several criteria which decide whether the payment
    method is valid. It is valid if all criteria are true. Only active and valid
    payment methods are provided to the shop customer.

    **Attributes:**

    name
        The name of the payment method. This is displayed to the customer to
        choose the payment method.

    active
        A flag which decides whether a payment method is displayed to the
        customer or not.

    description
        A longer description of the payment method. This could be displayed to
        the customer to describe the payment method in detail.

    note
        This is displayed to the customer within the checkout process and should
        contain a short note about the payment method.

    priority
        The order in which the payment methods are displayed to the customer.

    image
        An image of the payment method, which is displayed to customer within
        the checkout process.

    tax
        The tax of the payment method.

    price
        The default price of the payment method. This is taken if the payment
        method either has no additional prices or if none of he additional prices
        is valid.

    module
        This module will be called to process the payment. If it is empty the
        LFS' default one will be used.
    """
    active = models.BooleanField(_(u"Active"), default=False)
    priority = models.IntegerField(_(u"Priority"), default=0)
    name = models.CharField(_(u"Name"), max_length=50)
    description = models.TextField(_(u"Description"), blank=True)
    note = models.TextField(_(u"note"), blank=True)
    image = models.ImageField(_(u"Image"), upload_to="images", blank=True, null=True)
    tax = models.ForeignKey(Tax, verbose_name=_(u"Tax"), blank=True, null=True)
    price = models.FloatField(_(u"Price"), default=0.0)
    deletable = models.BooleanField(default=True)
    module = models.CharField(_(u'Module'), blank=True, max_length=100, choices=getattr(settings, "LFS_PAYMENT_METHOD_PROCESSORS", []))
    type = models.PositiveSmallIntegerField(_(u'Type'), choices=lfs.payment.settings.PAYMENT_METHOD_TYPES_CHOICES, default=lfs.payment.settings.PM_PLAIN)
    objects = ActivePaymentMethodManager()

    class Meta:
        ordering = ("priority", )
        app_label = 'payment'

    def __unicode__(self):
        return self.name


class PaymentMethodPrice(models.Model, Criteria):
    """
    An additional price for a payment method.

    A payment method price may have some criteria. Only when all criteria are
    true the price is valid. The first valid price is the actual price of the
    belonging payment method.

    **Attributes:**

    payment_method
        The shipping method to which the price belongs to.

    price
        The actual price, which will be billed to the shop customer

    priority
        The order in which all prices of the belonging payment method are tested
        for validity. Less comes first.
    """
    def __unicode__(self):
        return u"%s" % self.price

    class Meta:
        ordering = ("priority", )
        app_label = 'payment'

    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_(u"Payment method"), related_name="prices")
    price = models.FloatField(_(u"Price"), default=0.0)
    priority = models.IntegerField(_(u"Priority"), default=0)
    active = models.BooleanField(_(u"Active"), default=False)
