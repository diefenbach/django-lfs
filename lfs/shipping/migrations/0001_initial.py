# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ("catalog", "0001_initial"),
    )

    def forwards(self, orm):
        # Adding model 'ShippingMethod'
        db.create_table('shipping_shippingmethod', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('tax', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tax.Tax'], null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('delivery_time', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.DeliveryTime'], null=True, blank=True)),
            ('price_calculator', self.gf('django.db.models.fields.CharField')(default='lfs.shipping.GrossShippingMethodPriceCalculator', max_length=200)),
        ))
        db.send_create_signal('shipping', ['ShippingMethod'])

        # Adding model 'ShippingMethodPrice'
        db.create_table('shipping_shippingmethodprice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipping_method', self.gf('django.db.models.fields.related.ForeignKey')(related_name='prices', to=orm['shipping.ShippingMethod'])),
            ('price', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('shipping', ['ShippingMethodPrice'])


    def backwards(self, orm):
        # Deleting model 'ShippingMethod'
        db.delete_table('shipping_shippingmethod')

        # Deleting model 'ShippingMethodPrice'
        db.delete_table('shipping_shippingmethodprice')


    models = {
        'catalog.deliverytime': {
            'Meta': {'ordering': "('min',)", 'object_name': 'DeliveryTime'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max': ('django.db.models.fields.FloatField', [], {}),
            'min': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '2'})
        },
        'shipping.shippingmethod': {
            'Meta': {'ordering': "('priority',)", 'object_name': 'ShippingMethod'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'delivery_time': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.DeliveryTime']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price_calculator': ('django.db.models.fields.CharField', [], {'default': "'lfs.shipping.GrossShippingMethodPriceCalculator'", 'max_length': '200'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tax': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tax.Tax']", 'null': 'True', 'blank': 'True'})
        },
        'shipping.shippingmethodprice': {
            'Meta': {'ordering': "('priority',)", 'object_name': 'ShippingMethodPrice'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'shipping_method': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prices'", 'to': "orm['shipping.ShippingMethod']"})
        },
        'tax.tax': {
            'Meta': {'object_name': 'Tax'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0'})
        }
    }

    complete_apps = ['shipping']