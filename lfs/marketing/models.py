# django imports
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext

# lfs imports
from lfs.catalog.models import Product
from lfs.order.models import Order


class Topseller(models.Model):
    """Selected products are in any case among topsellers."""

    product = models.ForeignKey(Product, models.CASCADE, verbose_name=_("Product"))
    position = models.PositiveSmallIntegerField(_("Position"), default=1)

    class Meta:
        ordering = ["position"]
        app_label = "marketing"

    def __str__(self):
        return "%s (%s)" % (self.product.name, self.position)


class ProductSales(models.Model):
    """Stores totals sales per product."""

    product = models.ForeignKey(Product, models.CASCADE, verbose_name=_("Product"))
    sales = models.IntegerField(_("sales"), default=0)

    class Meta:
        app_label = "marketing"


class FeaturedProduct(models.Model):
    """Featured products are manually selected by the shop owner"""

    product = models.ForeignKey(Product, models.CASCADE, verbose_name=_("Product"))
    position = models.PositiveSmallIntegerField(_("Position"), default=1)
    active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ["position"]
        app_label = "marketing"

    def __str__(self):
        return "%s (%s)" % (self.product.name, self.position)


class OrderRatingMail(models.Model):
    """Saves whether and when a rating mail has been send for an order."""

    order = models.ForeignKey(Order, models.CASCADE, verbose_name=_("Order"))
    send_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%s)" % (self.order.id, self.send_date.strftime(gettext("DATE_FORMAT")))

    class Meta:
        app_label = "marketing"
