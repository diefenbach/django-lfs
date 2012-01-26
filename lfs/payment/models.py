from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.template.loader import render_to_string

# django imports
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.payment.settings
from lfs.criteria.models.criteria_objects import CriteriaObjects
from lfs.tax.models import Tax

# other imports
from paypal.standard.ipn.models import PayPalIPN
from paypal.standard.pdt.models import PayPalPDT


class ActivePaymentMethodManager(models.Manager):
    """A manager which return just valid (aka selectable) shipping methods.
    """
    def active(self):
        return super(ActivePaymentMethodManager, self).get_query_set().filter(active=True)


class PaymentMethod(models.Model):
    """Decides how products are paid.

    Instance variables:

    - name
       The name of the payment method. This is displayed to the customer to
       choose the payment method.

    - active
       A flag which decides whether a payment method is displayed to the
       customer or not.

    - description
       A longer description of the payment method. This could be displayed to
       the customer to describe the payment method in detail.

    - note
       This is displayed to the customer within the checkout process and should
       contain a short note about the payment method.

    - priority
       The order in which the payment methods are displayed to the customer.

    - image
       An image of the payment method, which is displayed to customer within
       the checkout process.

    - tax
       The tax of the payment method.

    - price
       The default price of the payment method. This is taken if the payment
       method either has no additional prices or if none of he additional prices
       is valid.

    - module
       This module will be called to process the payment. If it is empty the
       LFS' default one will be used.

    A payment method may have several criteria which decide whether the
    payment method is valid. It is valid if all criteria are true. Only active
    and valid payment methods are provided to the shop customer.
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
    module = models.CharField(_('Payment module'), blank=True, max_length=100)
    type = models.PositiveSmallIntegerField(_('Payment type'), choices=lfs.payment.settings.PAYMENT_METHOD_TYPES_CHOICES, default=lfs.payment.settings.PM_PLAIN)

    criteria_objects = generic.GenericRelation(CriteriaObjects,
        object_id_field="content_id", content_type_field="content_type")

    objects = ActivePaymentMethodManager()

    class Meta:
        ordering = ("priority", )

    def __unicode__(self):
        return self.name


class PaymentMethodPrice(models.Model):
    """An additional price for a payment method.

    Instance variables:

    - payment_method
       The shipping method to which the price belongs to.
    - price
       The actual price, which will be billed to the shop customer
    - priority
       The order in which all prices of the belonging payment method are tested
       for validity. Less comes first.

    A payment method price may have some criteria. Only when all criteria are
    true the price is valid. The first valid price is the actual price of the
    belonging payment method.
    """
    def __unicode__(self):
        return "%s" % self.price

    class Meta:
        ordering = ("priority", )

    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_(u"Payment method"), related_name="prices")
    price = models.FloatField(_(u"Price"), default=0.0)
    priority = models.IntegerField(_(u"Priority"), default=0)
    active = models.BooleanField(_(u"Active"), default=False)

    criteria_objects = generic.GenericRelation(CriteriaObjects,
        object_id_field="content_id", content_type_field="content_type")

    def is_valid(self, request):
        """Returns True if the payment method is valid. This is calculated via
        the attached criteria.
        """
        from lfs.criteria import utils as criteria_utils
        return criteria_utils.is_valid(self, request)

from lfs.order.models import Order


class PayPalOrderTransaction(models.Model):
    order = models.ForeignKey(Order, unique=True)
    ipn = models.ManyToManyField(PayPalIPN)


from listeners import *
