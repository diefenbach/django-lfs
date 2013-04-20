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
        # Adding model 'Country'
        db.create_table('core_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('core', ['Country'])

        # Adding model 'ActionGroup'
        db.create_table('core_actiongroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, blank=True)),
        ))
        db.send_create_signal('core', ['ActionGroup'])

        # Adding model 'Action'
        db.create_table('core_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='actions', to=orm['core.ActionGroup'])),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=999)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Action'], null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Action'])

        # Adding model 'Shop'
        db.create_table('core_shop', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('shop_owner', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('from_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('notification_emails', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('lfs.core.fields.thumbs.ImageWithThumbsField')(blank=True, max_length=100, null=True, sizes=((60, 60), (100, 100), (200, 200), (400, 400)))),
            ('static_block', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shops', null=True, to=orm['catalog.StaticBlock'])),
            ('product_cols', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('product_rows', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('category_cols', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('delivery_time', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.DeliveryTime'], null=True, blank=True)),
            ('google_analytics_id', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('ga_site_tracking', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ga_ecommerce_tracking', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('default_country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Country'])),
            ('use_international_currency_code', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('price_calculator', self.gf('django.db.models.fields.CharField')(default='lfs.gross_price.GrossPriceCalculator', max_length=255)),
            ('checkout_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('confirm_toc', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('meta_title', self.gf('django.db.models.fields.CharField')(default='<name>', max_length=80, blank=True)),
            ('meta_keywords', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('meta_description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('core', ['Shop'])

        # Adding M2M table for field invoice_countries on 'Shop'
        db.create_table('core_shop_invoice_countries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('shop', models.ForeignKey(orm['core.shop'], null=False)),
            ('country', models.ForeignKey(orm['core.country'], null=False))
        ))
        db.create_unique('core_shop_invoice_countries', ['shop_id', 'country_id'])

        # Adding M2M table for field shipping_countries on 'Shop'
        db.create_table('core_shop_shipping_countries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('shop', models.ForeignKey(orm['core.shop'], null=False)),
            ('country', models.ForeignKey(orm['core.country'], null=False))
        ))
        db.create_unique('core_shop_shipping_countries', ['shop_id', 'country_id'])

        # Adding model 'Application'
        db.create_table('core_application', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
        ))
        db.send_create_signal('core', ['Application'])


    def backwards(self, orm):
        # Deleting model 'Country'
        db.delete_table('core_country')

        # Deleting model 'ActionGroup'
        db.delete_table('core_actiongroup')

        # Deleting model 'Action'
        db.delete_table('core_action')

        # Deleting model 'Shop'
        db.delete_table('core_shop')

        # Removing M2M table for field invoice_countries on 'Shop'
        db.delete_table('core_shop_invoice_countries')

        # Removing M2M table for field shipping_countries on 'Shop'
        db.delete_table('core_shop_shipping_countries')

        # Deleting model 'Application'
        db.delete_table('core_application')


    models = {
        'catalog.deliverytime': {
            'Meta': {'ordering': "('min',)", 'object_name': 'DeliveryTime'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max': ('django.db.models.fields.FloatField', [], {}),
            'min': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '2'})
        },
        'catalog.file': {
            'Meta': {'ordering': "('position',)", 'object_name': 'File'},
            'content_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'files'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.SmallIntegerField', [], {'default': '999'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'catalog.staticblock': {
            'Meta': {'ordering': "('position',)", 'object_name': 'StaticBlock'},
            'display_files': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'position': ('django.db.models.fields.SmallIntegerField', [], {'default': '1000'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.action': {
            'Meta': {'ordering': "('position',)", 'object_name': 'Action'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': "orm['core.ActionGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Action']", 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'core.actiongroup': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ActionGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'blank': 'True'})
        },
        'core.application': {
            'Meta': {'object_name': 'Application'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'core.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.shop': {
            'Meta': {'object_name': 'Shop'},
            'category_cols': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'checkout_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'confirm_toc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default_country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Country']"}),
            'delivery_time': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.DeliveryTime']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'from_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'ga_ecommerce_tracking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ga_site_tracking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'google_analytics_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('lfs.core.fields.thumbs.ImageWithThumbsField', [], {'blank': 'True', 'max_length': '100', 'null': 'True', 'sizes': '((60, 60), (100, 100), (200, 200), (400, 400))'}),
            'invoice_countries': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'invoice'", 'symmetrical': 'False', 'to': "orm['core.Country']"}),
            'meta_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'default': "'<name>'", 'max_length': '80', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'notification_emails': ('django.db.models.fields.TextField', [], {}),
            'price_calculator': ('django.db.models.fields.CharField', [], {'default': "'lfs.gross_price.GrossPriceCalculator'", 'max_length': '255'}),
            'product_cols': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'product_rows': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'shipping_countries': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'shipping'", 'symmetrical': 'False', 'to': "orm['core.Country']"}),
            'shop_owner': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'static_block': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shops'", 'null': 'True', 'to': "orm['catalog.StaticBlock']"}),
            'use_international_currency_code': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['core']