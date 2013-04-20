# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Manufacturer'
        db.create_table('manufacturer_manufacturer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('short_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('lfs.core.fields.thumbs.ImageWithThumbsField')(blank=True, max_length=100, null=True, sizes=((60, 60), (100, 100), (200, 200), (400, 400)))),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=1000)),
            ('active_formats', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('product_rows', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('product_cols', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('meta_title', self.gf('django.db.models.fields.CharField')(default='<name>', max_length=100)),
            ('meta_keywords', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('meta_description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('manufacturer', ['Manufacturer'])


    def backwards(self, orm):
        # Deleting model 'Manufacturer'
        db.delete_table('manufacturer_manufacturer')


    models = {
        'manufacturer.manufacturer': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Manufacturer'},
            'active_formats': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('lfs.core.fields.thumbs.ImageWithThumbsField', [], {'blank': 'True', 'max_length': '100', 'null': 'True', 'sizes': '((60, 60), (100, 100), (200, 200), (400, 400))'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'default': "'<name>'", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'product_cols': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'product_rows': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'short_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['manufacturer']