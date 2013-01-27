# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from lfs.catalog.models import DeliveryTime

class Migration(SchemaMigration):
    def forwards(self, orm):
        db.add_column('core_shop', 'delivery_time', models.ForeignKey(DeliveryTime, verbose_name=_(u"Delivery time"), blank=True, null=True))    
    def backwards(self, orm):
    	db.delete_column("core_shop", "delivery_time_id")
