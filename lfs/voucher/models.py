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
from lfs.voucher.settings import MESSAGES


class VoucherOptions(models.Model):
    """Stores misc voucher options
    """
    number_prefix = models.CharField(max_length=20, blank=True, default="")
    number_suffix = models.CharField(max_length=20, blank=True, default="")
    number_length = models.IntegerField(blank=True, null=True, default=5)
    number_letters = models.CharField(max_length=100, blank=True, default="ABCDEFGHIJKLMNOPQRSTUVWXYZ")


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

        - start_date
            The date the voucher is going be valid. Before that date the
            voucher can't be used.

        - end_date
            The date the voucher is going to expire. After that date the
            voucher can't be used.

        - effective_from
            The cart price the voucher is from that the voucher is valid.

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

        - The quanity of how often the voucher can be used. Let it empty
          the voucher can be used unlimited.
    """
    number = models.CharField(max_length=100, unique=True)
    group = models.ForeignKey(VoucherGroup, related_name="vouchers")
    creator = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(blank=True, null=True)
    effective_from = models.FloatField(default=0.0)
    end_date = models.DateField(blank=True, null=True)
    kind_of = models.PositiveSmallIntegerField(choices=KIND_OF_CHOICES)
    value = models.FloatField(default=0.0)
    tax = models.ForeignKey(Tax, verbose_name=_(u"Tax"), blank=True, null=True)
    active = models.BooleanField(default=True)
    used_amount = models.PositiveSmallIntegerField(default=0)
    last_used_date = models.DateTimeField(blank=True, null=True)
    limit = models.PositiveSmallIntegerField(blank=True, null=True, default=1)

    class Meta:
        ordering = ("creation_date", "number")

    def __unicode__(self):
        return self.number

    def get_price_net(self, request, cart=None):
        """Returns the net price of the voucher.
        """
        if self.kind_of == ABSOLUTE:
            return self.value - self.get_tax(request)
        else:
            return cart.get_price_net(request) * (self.value / 100)

    def get_price_gross(self, request, cart=None):
        """Returns the gross price of the voucher.
        """
        if self.kind_of == ABSOLUTE:
            return self.value
        else:
            return cart.get_price_gross(request) * (self.value / 100)

    def get_tax(self, request, cart=None):
        """Returns the absolute tax of the voucher
        """
        if self.kind_of == ABSOLUTE:
            if self.tax:
                return (self.tax.rate / (100 + self.tax.rate)) * self.value
            else:
                return 0.0
        else:
            return cart.get_tax(request) * (self.value / 100)

    def mark_as_used(self):
        """Mark voucher as used.
        """
        self.used_amount += 1
        self.last_used_date = datetime.datetime.now()
        self.save()

    def is_effective(self, request, cart):
        """Returns True if the voucher is effective.
        """
        if self.active == False:
            return (False, MESSAGES[1])
        if (self.limit > 0) and (self.used_amount >= self.limit):
            return (False, MESSAGES[2])
        if self.start_date > datetime.date.today():
            return (False, MESSAGES[3])
        if self.end_date < datetime.date.today():
            return (False, MESSAGES[4])
        if self.effective_from > cart.get_price_gross(request):
            return (False, MESSAGES[5])

        return (True, MESSAGES[0])

    def is_absolute(self):
        """Returns True if voucher is absolute.
        """
        return self.kind_of == ABSOLUTE

    def is_percentage(self):
        """Returns True if voucher is percentage.
        """
        return self.kind_of == PERCENTAGE
