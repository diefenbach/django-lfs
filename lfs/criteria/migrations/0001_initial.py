# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ("payment", "0001_initial"),
        ("shipping", "0001_initial"),
    )
    
    def forwards(self, orm):
        # Adding model 'Criterion'
        db.create_table('criteria_criterion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='content_type', to=orm['contenttypes.ContentType'])),
            ('content_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('sub_type', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('position', self.gf('django.db.models.fields.PositiveIntegerField')(default=999)),
            ('operator', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('criteria', ['Criterion'])

        # Adding model 'CartPriceCriterion'
        db.create_table('criteria_cartpricecriterion', (
            ('criterion_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['criteria.Criterion'], unique=True, primary_key=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal('criteria', ['CartPriceCriterion'])

        # Adding model 'CombinedLengthAndGirthCriterion'
        db.create_table('criteria_combinedlengthandgirthcriterion', (
            ('criterion_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['criteria.Criterion'], unique=True, primary_key=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal('criteria', ['CombinedLengthAndGirthCriterion'])

        # Adding model 'CountryCriterion'
        db.create_table('criteria_countrycriterion', (
            ('criterion_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['criteria.Criterion'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('criteria', ['CountryCriterion'])

        # Adding M2M table for field value on 'CountryCriterion'
        db.create_table('criteria_countrycriterion_value', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('countrycriterion', models.ForeignKey(orm['criteria.countrycriterion'], null=False)),
            ('country', models.ForeignKey(orm['core.country'], null=False))
        ))
        db.create_unique('criteria_countrycriterion_value', ['countrycriterion_id', 'country_id'])

        # Adding model 'HeightCriterion'
        db.create_table('criteria_heightcriterion', (
            ('criterion_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['criteria.Criterion'], unique=True, primary_key=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal('criteria', ['HeightCriterion'])

        # Adding model 'LengthCriterion'
        db.create_table('criteria_lengthcriterion', (
            ('criterion_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['criteria.Criterion'], unique=True, primary_key=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal('criteria', ['LengthCriterion'])

        # Adding model 'PaymentMethodCriterion'
        db.create_table('criteria_paymentmethodcriterion', (
            ('criterion_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['criteria.Criterion'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('criteria', ['PaymentMethodCriterion'])

        # Adding M2M table for field value on 'PaymentMethodCriterion'
        db.create_table('criteria_paymentmethodcriterion_value', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('paymentmethodcriterion', models.ForeignKey(orm['criteria.paymentmethodcriterion'], null=False)),
            ('paymentmethod', models.ForeignKey(orm['payment.paymentmethod'], null=False))
        ))
        db.create_unique('criteria_paymentmethodcriterion_value', ['paymentmethodcriterion_id', 'paymentmethod_id'])

        # Adding model 'ShippingMethodCriterion'
        db.create_table('criteria_shippingmethodcriterion', (
            ('criterion_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['criteria.Criterion'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('criteria', ['ShippingMethodCriterion'])

        # Adding M2M table for field value on 'ShippingMethodCriterion'
        db.create_table('criteria_shippingmethodcriterion_value', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('shippingmethodcriterion', models.ForeignKey(orm['criteria.shippingmethodcriterion'], null=False)),
            ('shippingmethod', models.ForeignKey(orm['shipping.shippingmethod'], null=False))
        ))
        db.create_unique('criteria_shippingmethodcriterion_value', ['shippingmethodcriterion_id', 'shippingmethod_id'])

        # Adding model 'WeightCriterion'
        db.create_table('criteria_weightcriterion', (
            ('criterion_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['criteria.Criterion'], unique=True, primary_key=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal('criteria', ['WeightCriterion'])

        # Adding model 'WidthCriterion'
        db.create_table('criteria_widthcriterion', (
            ('criterion_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['criteria.Criterion'], unique=True, primary_key=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal('criteria', ['WidthCriterion'])


    def backwards(self, orm):
        # Deleting model 'Criterion'
        db.delete_table('criteria_criterion')

        # Deleting model 'CartPriceCriterion'
        db.delete_table('criteria_cartpricecriterion')

        # Deleting model 'CombinedLengthAndGirthCriterion'
        db.delete_table('criteria_combinedlengthandgirthcriterion')

        # Deleting model 'CountryCriterion'
        db.delete_table('criteria_countrycriterion')

        # Removing M2M table for field value on 'CountryCriterion'
        db.delete_table('criteria_countrycriterion_value')

        # Deleting model 'HeightCriterion'
        db.delete_table('criteria_heightcriterion')

        # Deleting model 'LengthCriterion'
        db.delete_table('criteria_lengthcriterion')

        # Deleting model 'PaymentMethodCriterion'
        db.delete_table('criteria_paymentmethodcriterion')

        # Removing M2M table for field value on 'PaymentMethodCriterion'
        db.delete_table('criteria_paymentmethodcriterion_value')

        # Deleting model 'ShippingMethodCriterion'
        db.delete_table('criteria_shippingmethodcriterion')

        # Removing M2M table for field value on 'ShippingMethodCriterion'
        db.delete_table('criteria_shippingmethodcriterion_value')

        # Deleting model 'WeightCriterion'
        db.delete_table('criteria_weightcriterion')

        # Deleting model 'WidthCriterion'
        db.delete_table('criteria_widthcriterion')


    models = {
        'catalog.deliverytime': {
            'Meta': {'ordering': "('min',)", 'object_name': 'DeliveryTime'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max': ('django.db.models.fields.FloatField', [], {}),
            'min': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '2'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'criteria.cartpricecriterion': {
            'Meta': {'ordering': "('position',)", 'object_name': 'CartPriceCriterion', '_ormbases': ['criteria.Criterion']},
            'criterion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['criteria.Criterion']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'criteria.combinedlengthandgirthcriterion': {
            'Meta': {'ordering': "('position',)", 'object_name': 'CombinedLengthAndGirthCriterion', '_ormbases': ['criteria.Criterion']},
            'criterion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['criteria.Criterion']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'criteria.countrycriterion': {
            'Meta': {'ordering': "('position',)", 'object_name': 'CountryCriterion', '_ormbases': ['criteria.Criterion']},
            'criterion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['criteria.Criterion']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Country']", 'symmetrical': 'False'})
        },
        'criteria.criterion': {
            'Meta': {'ordering': "('position',)", 'object_name': 'Criterion'},
            'content_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operator': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'default': '999'}),
            'sub_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'criteria.heightcriterion': {
            'Meta': {'ordering': "('position',)", 'object_name': 'HeightCriterion', '_ormbases': ['criteria.Criterion']},
            'criterion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['criteria.Criterion']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'criteria.lengthcriterion': {
            'Meta': {'ordering': "('position',)", 'object_name': 'LengthCriterion', '_ormbases': ['criteria.Criterion']},
            'criterion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['criteria.Criterion']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'criteria.paymentmethodcriterion': {
            'Meta': {'ordering': "('position',)", 'object_name': 'PaymentMethodCriterion', '_ormbases': ['criteria.Criterion']},
            'criterion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['criteria.Criterion']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['payment.PaymentMethod']", 'symmetrical': 'False'})
        },
        'criteria.shippingmethodcriterion': {
            'Meta': {'ordering': "('position',)", 'object_name': 'ShippingMethodCriterion', '_ormbases': ['criteria.Criterion']},
            'criterion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['criteria.Criterion']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['shipping.ShippingMethod']", 'symmetrical': 'False'})
        },
        'criteria.weightcriterion': {
            'Meta': {'ordering': "('position',)", 'object_name': 'WeightCriterion', '_ormbases': ['criteria.Criterion']},
            'criterion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['criteria.Criterion']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'criteria.widthcriterion': {
            'Meta': {'ordering': "('position',)", 'object_name': 'WidthCriterion', '_ormbases': ['criteria.Criterion']},
            'criterion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['criteria.Criterion']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'payment.paymentmethod': {
            'Meta': {'ordering': "('priority',)", 'object_name': 'PaymentMethod'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deletable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tax': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tax.Tax']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
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
        'tax.tax': {
            'Meta': {'object_name': 'Tax'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0'})
        }
    }

    complete_apps = ['criteria']