# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ("customer", "0001_initial"),
    )

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."

        for ct in orm['contenttypes.ContentType'].objects.filter(app_label='addresses', model='address'):
            for customer in orm['customer.Customer'].objects.filter(sa_content_type=ct):
                address = orm['addresses.Address'].objects.get(id=customer.sa_object_id)
                address.customer = customer
                address.save()
            for customer in orm['customer.Customer'].objects.filter(ia_content_type=ct):
                address = orm['addresses.Address'].objects.get(id=customer.ia_object_id)
                address.customer = customer
                address.save()


    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        'addresses.address': {
            'Meta': {'object_name': 'Address', '_ormbases': ['addresses.BaseAddress']},
            'baseaddress_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['addresses.BaseAddress']", 'unique': 'True', 'primary_key': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'addresses.baseaddress': {
            'Meta': {'object_name': 'BaseAddress'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Country']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'addresses'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['customer.Customer']"}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'line1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'line2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'addresses'", 'null': 'True', 'to': "orm['order.Order']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
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
        'order.order': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Order'},
            'account_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'bank_identification_code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer_email': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'customer_firstname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'customer_lastname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'depositor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'ia_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_invoice_address'", 'to': "orm['contenttypes.ContentType']"}),
            'ia_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'pay_link': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.PaymentMethod']", 'null': 'True', 'blank': 'True'}),
            'payment_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'payment_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'requested_delivery_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sa_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_shipping_address'", 'to': "orm['contenttypes.ContentType']"}),
            'sa_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'session': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shipping_method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shipping.ShippingMethod']", 'null': 'True', 'blank': 'True'}),
            'shipping_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'shipping_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'state_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'16c3d95d-f400-4730-b7ea-ec08d22aa074'", 'unique': 'True', 'max_length': '50'}),
            'voucher_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'voucher_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'voucher_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
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

    complete_apps = ['customer', 'addresses']
    symmetrical = True
