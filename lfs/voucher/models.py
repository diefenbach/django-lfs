# python imports
import datetime

# django imports
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.tax.models import Tax
from lfs.voucher.settings import KIND_OF_CHOICES
from lfs.voucher.settings import ABSOLUTE
from lfs.voucher.settings import PERCENTAGE

class VoucherOptions(models.Model):
    """Stores misc voucher options
    """
    number_prefix = models.CharField(max_length=20, blank=True, default="")
    number_suffix = models.CharField(max_length=20, blank=True, default="")
    number_length = models.IntegerField(blank=True, null=True, default=5)
    number_letters = models.CharField(max_length=10, blank=True, default="ABCDEFGHIJKLMNOPQRSTUVWXYZ")

class VoucherGroup(models.Model):
    """Groups vouchers together.
    """
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now_add=True)
    position = models.PositiveSmallIntegerField(default=10)

    class Meta:
        ordering = ("position", )

class Voucher(models.Model):
    """A voucher.

    Parameters:

        - number
            The unique number of the voucher. This number has to be provided
            by the shop customer within the checkout in order to get the
            credit.

        - group
            The group the voucher belongs to.

        - creator
            The creator of the voucher

        - creation_date
            The date the voucher has been created

        - expiration_date
            The date the voucher is going to expire. After that date the
            voucher can't be used.

        - kind_of
            The kind of the voucher. Absolute or percentage.

        - value
            The value of the the voucher, which is interpreted either as an
            absolute value in the current currency or a percentage quotation.

        - tax
            The tax of the voucher. This is only taken, when the voucher is
            ABSOLUTE. If the voucher is PERCENTAGE the total tax of the
            discount is taken from every single product.

        - active
            Only active vouchers can be redeemed.

        - used
            Indicates whether a voucher has already be used. Every voucher can
            only used one time.

        - used_date
            The date the voucher has been redeemed.
    """
    number = models.CharField(max_length=100, unique=True)
    group = models.ForeignKey(VoucherGroup, related_name="vouchers")
    creator = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    kind_of = models.PositiveSmallIntegerField(choices=KIND_OF_CHOICES)
    value = models.FloatField(default=0.0)
    tax = models.ForeignKey(Tax, verbose_name=_(u"Tax"), blank=True, null=True)
    active = models.BooleanField(default=True)
    used = models.BooleanField(default=False)
    used_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("creation_date", "number")

    def __unicode__(self):
        return self.number

    def get_price_net(self, cart=None):
        """Returns the net price of the voucher.
        """
        if self.kind_of == ABSOLUTE:
            return self.value - self.get_tax()
        else:
            return cart.get_price_net() * (self.value / 100)

    def get_price_gross(self, cart=None):
        """Returns the gross price of the voucher.
        """
        if self.kind_of == ABSOLUTE:
            return self.value
        else:
            return cart.get_price_gross() * (self.value / 100)

    def get_tax(self, cart=None):
        """Returns the absolute tax of the voucher
        """
        if self.kind_of == ABSOLUTE:
            if self.tax:
                return (self.tax.rate / (100 + self.tax.rate)) * self.value
            else:
                return 0.0
        else:
            return cart.get_tax()  * (self.value / 100)

    def mark_as_used(self):
        """Mark voucher as used.
        """
        self.used = True
        self.used_date = datetime.datetime.now()
        self.save()

    def is_absolute(self):
        """Returns True if voucher is absolute.
        """
        return self.kind_of == ABSOLUTE

    def is_percentage(self):
        """Returns True if voucher is percentage.
        """
        return self.kind_of == PERCENTAGE