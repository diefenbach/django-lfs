# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CustomerTax'
        db.create_table('customer_tax_customertax', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rate', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('customer_tax', ['CustomerTax'])


    def backwards(self, orm):
        # Deleting model 'CustomerTax'
        db.delete_table('customer_tax_customertax')


    models = {
        'customer_tax.customertax': {
            'Meta': {'object_name': 'CustomerTax'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0'})
        }
    }

    complete_apps = ['customer_tax']