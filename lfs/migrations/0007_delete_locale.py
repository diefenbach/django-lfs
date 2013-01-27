# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from lfs.addresses.models import Address
from lfs.catalog.models import DeliveryTime
from lfs.criteria.models import CartPriceCriterion
from lfs.criteria.models import CombinedLengthAndGirthCriterion
from lfs.criteria.models import CountryCriterion
from lfs.criteria.models import HeightCriterion
from lfs.criteria.models import LengthCriterion
from lfs.criteria.models import WidthCriterion
from lfs.criteria.models import WeightCriterion
from lfs.criteria.models import ShippingMethodCriterion
from lfs.criteria.models import PaymentMethodCriterion
from lfs.customer.models import Customer
from lfs.order.models import Order
class Migration(SchemaMigration):
    def forwards(self, orm):
        db.delete_column("core_shop", "default_locale")

    def backwards(self, orm):
        db.add_column("core_shop", "default_locale", models.PositiveIntegerField(default=0))
