# -*- coding: utf-8 -*-
from copy import deepcopy
import datetime
from django.contrib.contenttypes import generic
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        sa_gfk = generic.GenericForeignKey('sa_content_type', 'sa_object_id')
        sa_gfk.contribute_to_class(orm.Customer, "selected_shipping_address")

        ia_gfk = generic.GenericForeignKey('ia_content_type', 'ia_object_id')
        ia_gfk.contribute_to_class(orm.Customer, "selected_invoice_address")

        for obj in orm.Customer.objects.all():
            ssa = obj.selected_shipping_address
            if ssa:
                address = deepcopy(ssa)
                address.id = None
                address.pk = None
                address.save()
                obj.dsa_object_id = address.id

            sia = obj.selected_invoice_address
            if sia:
                address = deepcopy(sia)
                address.id = None
                address.pk = None
                address.save()
                obj.dia_object_id = address.id
            if ssa or sia:
                obj.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
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
        'customer.bankaccount': {
            'Meta': {'object_name': 'BankAccount'},
            'account_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'bank_identification_code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bank_accounts'", 'null': 'True', 'to': "orm['customer.Customer']"}),
            'depositor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'customer.creditcard': {
            'Meta': {'object_name': 'CreditCard'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'credit_cards'", 'null': 'True', 'to': "orm['customer.Customer']"}),
            'expiration_date_month': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'expiration_date_year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'owner': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        'customer.customer': {
            'Meta': {'object_name': 'Customer'},
            'dia_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'dsa_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'ia_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ia_content_type'", 'to': "orm['contenttypes.ContentType']"}),
            'ia_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sa_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sa_content_type'", 'to': "orm['contenttypes.ContentType']"}),
            'sa_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'selected_bank_account': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'selected_bank_account'", 'null': 'True', 'to': "orm['customer.BankAccount']"}),
            'selected_country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Country']", 'null': 'True', 'blank': 'True'}),
            'selected_credit_card': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'selected_credit_card'", 'null': 'True', 'to': "orm['customer.CreditCard']"}),
            'selected_payment_method': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'selected_payment_method'", 'null': 'True', 'to': "orm['payment.PaymentMethod']"}),
            'selected_shipping_method': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'selected_shipping_method'", 'null': 'True', 'to': "orm['shipping.ShippingMethod']"}),
            'session': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
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

    complete_apps = ['customer']
    symmetrical = True
