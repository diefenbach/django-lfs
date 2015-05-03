# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext

# lfs imports
from lfs.catalog.models import Product
from lfs.order.models import Order


class Topseller(models.Model):
    """Selected products are in any case among topsellers.
    """
    product = models.ForeignKey(Product, verbose_name=_(u"Product"))
    position = models.PositiveSmallIntegerField(_(u"Position"), default=1)

    class Meta:
        ordering = ["position"]
        app_label = 'marketing'

    def __unicode__(self):
        return u"%s (%s)" % (self.product.name, self.position)


class ProductSales(models.Model):
    """Stores totals sales per product.
    """
    product = models.ForeignKey(Product, verbose_name=_(u"Product"))
    sales = models.IntegerField(_(u"sales"), default=0)

    class Meta:
        app_label = 'marketing'


class FeaturedProduct(models.Model):
    """Featured products are manually selected by the shop owner
    """
    product = models.ForeignKey(Product, verbose_name=_(u"Product"))
    position = models.PositiveSmallIntegerField(_(u"Position"), default=1)
    active = models.BooleanField(_(u"Active"), default=True)

    class Meta:
        ordering = ["position"]
        app_label = 'marketing'

    def __unicode__(self):
        return u"%s (%s)" % (self.product.name, self.position)


class OrderRatingMail(models.Model):
    """Saves whether and when a rating mail has been send for an order.
    """
    order = models.ForeignKey(Order, verbose_name=_(u"Order"))
    send_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"%s (%s)" % (self.order.id, self.send_date.strftime(ugettext('DATE_FORMAT')))

    class Meta:
        app_label = 'marketing'
