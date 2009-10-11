# python imports
import re

# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.checkout.settings import CHECKOUT_TYPES
from lfs.checkout.settings import CHECKOUT_TYPE_SELECT
from lfs.core.fields.thumbs import ImageWithThumbsField
from lfs.core.settings import ACTION_PLACE_CHOICES
from lfs.core.settings import ACTION_PLACE_TABS
from lfs.catalog.models import StaticBlock

class Country(models.Model):
    """Holds country relevant data for the shop.
    """
    code = models.CharField(_(u"Country code"), max_length=2)
    name = models.CharField(_(u"Name"), max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ("name", )

class Action(models.Model):
    """A action is a link which can be displayed on several parts of the web
    page.

    Instance variables:

    - title
      The title of the menu tab
    - link
      The link to the object
    - active
      If true the tab is displayed.
    - position
      the position of the tab within the menu.
    - parent
      Parent tab to create a tree
    """
    title = models.CharField(_(u"Title"), max_length=40)
    link = models.CharField(_(u"Link"), blank=True, max_length=100)
    active = models.BooleanField(_(u"Active"), default=False)
    place = models.PositiveSmallIntegerField(blank=True, null=True, choices=ACTION_PLACE_CHOICES, default=ACTION_PLACE_TABS)
    position = models.IntegerField(_(u"Position"), default=999)
    parent = models.ForeignKey("self", verbose_name=_(u"Parent"), blank=True, null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering=("position",)

class Shop(models.Model):
    """Holds all shop related information.

    At the moment there must be exactly one shop with id == 1. (This may be
    changed in future to provide multi shops.)

    Instance variables:

    - name
       The name of the shop. This is used for the the title of the HTML pages

    - shop_owner
       The shop owner. This is displayed within several places for instance the
       checkout page

    - from_email
       This e-mail address is used for the from header of all outgoing e-mails

    - notification_emails
       This e-mail addresses are used for incoming notification e-mails, e.g.
       received an order. One e-mail address per line.

    - description
       A description of the shop

    - image
      An image which can be used as default image if a category doesn't have one

    - product_cols, product_rows, category_cols
       Upmost format information, which defines how products and categories are
       displayed within several views. These may be inherited by categories and
       sub categories.

    - google_analytics_id
       Used to generate google analytics tracker code and e-commerce code. the
       id has the format UA-xxxxxxx-xx and is provided by Google.

    - ga_site_tracking
       If selected and the google_analytics_id is given google analytics site
       tracking code is inserted into the HTML source code.

    - ga_ecommerce_tracking
       If selected and the google_analytics_id is given google analytics
       e-commerce tracking code is inserted into the HTML source code.

    - countries
       Selected countries will be offered to the shop customer tho choose for
       shipping and invoice address.

    - default_country
       This country will be used to calculate shipping price if the shop
       customer doesn't have select a country yet.

    - checkout_type
       Decides whether the customer has to login, has not to login or has the
       choice to to login or not to be able to check out.
    """
    name = models.CharField(_(u"Name"), max_length=30)
    shop_owner = models.CharField(_(u"Shop owner"), max_length=100, blank=True)
    from_email = models.EmailField(_(u"From e-mail address"))
    notification_emails  = models.TextField(_(u"Notification email addresses"))

    description = models.TextField(_(u"Description"), blank=True)
    image = ImageWithThumbsField(_(u"Image"), upload_to="images", blank=True, null=True, sizes=((60, 60), (100, 100), (200, 200), (400, 400)))
    static_block = models.ForeignKey(StaticBlock, verbose_name=_(u"Static block"), blank=True, null=True, related_name="shops")

    product_cols = models.IntegerField(_(u"Product cols"), default=3)
    product_rows = models.IntegerField(_(u"Product rows"), default=3)
    category_cols = models.IntegerField(_(u"Category cols"), default=3)
    google_analytics_id = models.CharField(_(u"Google Analytics ID"), blank=True, max_length=20)
    ga_site_tracking = models.BooleanField(_(u"Google Analytics Site Tracking"), default=False)
    ga_ecommerce_tracking = models.BooleanField(_(u"Google Analytics E-Commerce Tracking"), default=False)

    countries = models.ManyToManyField(Country, verbose_name=_(u"Countries"), related_name="shops")
    default_country = models.ForeignKey(Country, verbose_name=_(u"Default country"))
    default_currency = models.CharField(_(u"Default Currency"), max_length=30, default="EUR")

    checkout_type = models.PositiveSmallIntegerField(_(u"Checkout type"), choices=CHECKOUT_TYPES, default=CHECKOUT_TYPE_SELECT)

    class Meta:
        permissions = (("manage_shop", "Manage shop"),)

    def __unicode__(self):
        return self.name

    def get_format_info(self):
        """
        """
        return {
            "product_cols" : self.product_cols,
            "product_rows" : self.product_rows,
            "category_cols" : self.category_cols,
        }

    def get_notification_emails(self):
        """Returns the notification e-mail addresses as list
        """
        adresses = re.split("[\s,]+", self.notification_emails)
        return adresses

    def get_parent_for_portlets(self):
        """Implements contract for django-portlets. Returns always None as there
        is no parent for a shop.
        """
        return None

from monkeys import *