
from south.db import db
from django.db import models
from lfs.order.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Order.requested_delivery_date'
        db.add_column('order_order', 'requested_delivery_date', orm['order.Order:requested_delivery_date'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Order.requested_delivery_date'
        db.delete_column('order_order', 'requested_delivery_date')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'catalog.deliverytime': {
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max': ('django.db.models.fields.FloatField', [], {}),
            'min': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '2'})
        },
        'catalog.image': {
            'content_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'image'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('ImageWithThumbsField', ['_(u"Image")'], {'null': 'True', 'sizes': '((60,60),(100,100),(200,200),(400,400))', 'blank': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '999'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'catalog.product': {
            'accessories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalog.Product']", 'null': 'True', 'blank': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_accessories': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_description': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_dimensions': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_for_sale': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'active_for_sale_price': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_images': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_meta_description': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_meta_keywords': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_meta_title': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_name': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_price': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_related_products': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_short_description': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'active_sku': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_variant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.Product']", 'null': 'True', 'blank': 'True'}),
            'deliverable': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'delivery_time': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products_delivery_time'", 'null': 'True', 'to': "orm['catalog.DeliveryTime']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'effective_price': ('django.db.models.fields.FloatField', [], {'blank': 'True'}),
            'for_sale': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'for_sale_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'height': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.contrib.contenttypes.generic.GenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['catalog.Image']"}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'manage_stock_amount': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'manual_delivery_time': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'default': "'<name>'", 'max_length': '80', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'order_time': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products_order_time'", 'null': 'True', 'to': "orm['catalog.DeliveryTime']"}),
            'ordered_at': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'variants'", 'null': 'True', 'to': "orm['catalog.Product']"}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'related_products': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['catalog.Product']", 'null': 'True', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '80', 'db_index': 'True'}),
            'stock_amount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sub_type': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '10'}),
            'tax': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tax.Tax']", 'null': 'True', 'blank': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'variant_position': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'variants_display_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'weight': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'width': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.country': {
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'criteria.criteriaobjects': {
            'content_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type'", 'to': "orm['contenttypes.ContentType']"}),
            'criterion_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'criterion_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'criterion'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'default': '999'})
        },
        'order.order': {
            'account_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'bank_identification_code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer_email': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'customer_firstname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'customer_lastname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'depositor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'invoice_company_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'invoice_country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orders_invoice_country'", 'null': 'True', 'to': "orm['core.Country']"}),
            'invoice_firstname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'invoice_lastname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'invoice_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'invoice_state': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'invoice_street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'invoice_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.PaymentMethod']", 'null': 'True', 'blank': 'True'}),
            'payment_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'payment_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'requested_delivery_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'session': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shipping_city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'shipping_company_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'shipping_country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orders_shipping_country'", 'null': 'True', 'to': "orm['core.Country']"}),
            'shipping_firstname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'shipping_lastname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'shipping_method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shipping.ShippingMethod']", 'null': 'True', 'blank': 'True'}),
            'shipping_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'shipping_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'shipping_state': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'shipping_street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shipping_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'shipping_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'state_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'76e67454-c1bc-49d6-9b03-11f7c38fc307'", 'unique': 'True', 'max_length': '50'}),
            'voucher_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'voucher_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'voucher_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'order.orderitem': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['order.Order']"}),
            'price_gross': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price_net': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.Product']", 'null': 'True', 'blank': 'True'}),
            'product_amount': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'product_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'product_price_gross': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'product_price_net': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'product_sku': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'product_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'payment.paymentmethod': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'criteria_objects': ('django.contrib.contenttypes.generic.GenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['criteria.CriteriaObjects']"}),
            'deletable': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tax': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tax.Tax']", 'null': 'True', 'blank': 'True'})
        },
        'shipping.shippingmethod': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'criteria_objects': ('django.contrib.contenttypes.generic.GenericRelation', [], {'object_id_field': "'content_id'", 'to': "orm['criteria.CriteriaObjects']"}),
            'delivery_time': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.DeliveryTime']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tax': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tax.Tax']", 'null': 'True', 'blank': 'True'})
        },
        'tax.tax': {
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0'})
        }
    }
    
    complete_apps = ['order']
