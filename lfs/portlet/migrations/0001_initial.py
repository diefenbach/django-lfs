# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AverageRatingPortlet'
        db.create_table('portlet_averageratingportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('portlet', ['AverageRatingPortlet'])

        # Adding model 'CartPortlet'
        db.create_table('portlet_cartportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('portlet', ['CartPortlet'])

        # Adding model 'CategoriesPortlet'
        db.create_table('portlet_categoriesportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('start_level', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('expand_level', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
        ))
        db.send_create_signal('portlet', ['CategoriesPortlet'])

        # Adding model 'DeliveryTimePortlet'
        db.create_table('portlet_deliverytimeportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('portlet', ['DeliveryTimePortlet'])

        # Adding model 'PagesPortlet'
        db.create_table('portlet_pagesportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('portlet', ['PagesPortlet'])

        # Adding model 'RecentProductsPortlet'
        db.create_table('portlet_recentproductsportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('portlet', ['RecentProductsPortlet'])

        # Adding model 'RelatedProductsPortlet'
        db.create_table('portlet_relatedproductsportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('portlet', ['RelatedProductsPortlet'])

        # Adding model 'TextPortlet'
        db.create_table('portlet_textportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('portlet', ['TextPortlet'])

        # Adding model 'TopsellerPortlet'
        db.create_table('portlet_topsellerportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('limit', self.gf('django.db.models.fields.IntegerField')(default=5)),
        ))
        db.send_create_signal('portlet', ['TopsellerPortlet'])

        # Adding model 'FilterPortlet'
        db.create_table('portlet_filterportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('show_product_filters', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('show_price_filters', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('portlet', ['FilterPortlet'])

        # Adding model 'ForsalePortlet'
        db.create_table('portlet_forsaleportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('limit', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('current_category', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slideshow', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('portlet', ['ForsalePortlet'])

        # Adding model 'FeaturedPortlet'
        db.create_table('portlet_featuredportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('limit', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('current_category', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slideshow', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('portlet', ['FeaturedPortlet'])


    def backwards(self, orm):
        # Deleting model 'AverageRatingPortlet'
        db.delete_table('portlet_averageratingportlet')

        # Deleting model 'CartPortlet'
        db.delete_table('portlet_cartportlet')

        # Deleting model 'CategoriesPortlet'
        db.delete_table('portlet_categoriesportlet')

        # Deleting model 'DeliveryTimePortlet'
        db.delete_table('portlet_deliverytimeportlet')

        # Deleting model 'PagesPortlet'
        db.delete_table('portlet_pagesportlet')

        # Deleting model 'RecentProductsPortlet'
        db.delete_table('portlet_recentproductsportlet')

        # Deleting model 'RelatedProductsPortlet'
        db.delete_table('portlet_relatedproductsportlet')

        # Deleting model 'TextPortlet'
        db.delete_table('portlet_textportlet')

        # Deleting model 'TopsellerPortlet'
        db.delete_table('portlet_topsellerportlet')

        # Deleting model 'FilterPortlet'
        db.delete_table('portlet_filterportlet')

        # Deleting model 'ForsalePortlet'
        db.delete_table('portlet_forsaleportlet')

        # Deleting model 'FeaturedPortlet'
        db.delete_table('portlet_featuredportlet')


    models = {
        'portlet.averageratingportlet': {
            'Meta': {'object_name': 'AverageRatingPortlet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'portlet.cartportlet': {
            'Meta': {'object_name': 'CartPortlet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'portlet.categoriesportlet': {
            'Meta': {'object_name': 'CategoriesPortlet'},
            'expand_level': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_level': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'portlet.deliverytimeportlet': {
            'Meta': {'object_name': 'DeliveryTimePortlet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'portlet.featuredportlet': {
            'Meta': {'object_name': 'FeaturedPortlet'},
            'current_category': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'slideshow': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'portlet.filterportlet': {
            'Meta': {'object_name': 'FilterPortlet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show_price_filters': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_product_filters': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'portlet.forsaleportlet': {
            'Meta': {'object_name': 'ForsalePortlet'},
            'current_category': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'slideshow': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'portlet.pagesportlet': {
            'Meta': {'object_name': 'PagesPortlet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'portlet.recentproductsportlet': {
            'Meta': {'object_name': 'RecentProductsPortlet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'portlet.relatedproductsportlet': {
            'Meta': {'object_name': 'RelatedProductsPortlet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'portlet.textportlet': {
            'Meta': {'object_name': 'TextPortlet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'portlet.topsellerportlet': {
            'Meta': {'object_name': 'TopsellerPortlet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['portlet']