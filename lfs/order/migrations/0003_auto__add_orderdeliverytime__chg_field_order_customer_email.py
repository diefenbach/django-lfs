# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'OrderDeliveryTime'
        db.create_table(u'order_orderdeliverytime', (
            (u'deliverytime_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['catalog.DeliveryTime'], unique=True, primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.OneToOneField')(related_name='delivery_time', unique=True, to=orm['order.Order'])),
        ))
        db.send_create_signal(u'order', ['OrderDeliveryTime'])


        # Changing field 'Order.customer_email'
        db.alter_column(u'order_order', 'customer_email', self.gf('django.db.models.fields.CharField')(max_length=75))

    def backwards(self, orm):
        # Deleting model 'OrderDeliveryTime'
        db.delete_table(u'order_orderdeliverytime')


        # Changing field 'Order.customer_email'
        db.alter_column(u'order_order', 'customer_email', self.gf('django.db.models.fields.CharField')(max_length=50))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'catalog.deliverytime': {
            'Meta': {'ordering': "('min',)", 'object_name': 'DeliveryTime'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max': ('django.db.models.fields.FloatField', [], {}),
            'min': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '2'})
        },
        u'catalog.groupspropertiesrelation': {
            'Meta': {'ordering': "('position',)", 'unique_together': "(('group', 'property'),)", 'object_name': 'GroupsPropertiesRelation'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groupproperties'", 'to': u"orm['catalog.PropertyGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalog.Property']"})
        },
        u'catalog.product': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Product'},
            'accessories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'reverse_accessories'", 'to': u"orm['catalog.Product']", 'through': u"orm['catalog.ProductAccessories']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_accessories': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_base_price': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'active_description': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_dimensions': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_for_sale': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'active_for_sale_price': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_images': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_meta_description': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_meta_keywords': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_meta_title': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_name': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_packing_unit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'active_price': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_price_calculation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_related_products': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_short_description': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_sku': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active_static_block': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'base_price_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'base_price_unit': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'category_variant': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_variant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalog.Product']", 'null': 'True', 'blank': 'True'}),
            'deliverable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'delivery_time': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products_delivery_time'", 'null': 'True', 'to': u"orm['catalog.DeliveryTime']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'effective_price': ('django.db.models.fields.FloatField', [], {'blank': 'True'}),
            'for_sale': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'for_sale_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'height': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'manage_stock_amount': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manual_delivery_time': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['manufacturer.Manufacturer']"}),
            'meta_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'default': "'<name>'", 'max_length': '80', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'order_time': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products_order_time'", 'null': 'True', 'to': u"orm['catalog.DeliveryTime']"}),
            'ordered_at': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'packing_unit': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'packing_unit_unit': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'variants'", 'null': 'True', 'to': u"orm['catalog.Product']"}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price_calculation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'price_calculator': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'price_unit': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'related_products': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'reverse_related_products'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['catalog.Product']"}),
            'short_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'sku_manufacturer': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '80'}),
            'static_block': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products'", 'null': 'True', 'to': u"orm['catalog.StaticBlock']"}),
            'stock_amount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sub_type': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '10'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'product_set'", 'null': 'True', 'to': u"orm['supplier.Supplier']"}),
            'tax': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tax.Tax']", 'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type_of_quantity_field': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'default': "'04c17f22-fe5a-4dcf-83e4-1fe709a9466e'", 'unique': 'True', 'max_length': '50'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'variant_position': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'variants_display_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'weight': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'width': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        u'catalog.productaccessories': {
            'Meta': {'ordering': "('position',)", 'object_name': 'ProductAccessories'},
            'accessory': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'productaccessories_accessory'", 'to': u"orm['catalog.Product']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'productaccessories_product'", 'to': u"orm['catalog.Product']"}),
            'quantity': ('django.db.models.fields.FloatField', [], {'default': '1'})
        },
        u'catalog.productspropertiesrelation': {
            'Meta': {'ordering': "('position',)", 'unique_together': "(('product', 'property'),)", 'object_name': 'ProductsPropertiesRelation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'productsproperties'", 'to': u"orm['catalog.Product']"}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalog.Property']"})
        },
        u'catalog.property': {
            'Meta': {'ordering': "['position']", 'object_name': 'Property'},
            'add_price': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'configurable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'decimal_places': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'display_on_product': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_price': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'filterable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'properties'", 'to': u"orm['catalog.PropertyGroup']", 'through': u"orm['catalog.GroupsPropertiesRelation']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'position': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'properties'", 'to': u"orm['catalog.Product']", 'through': u"orm['catalog.ProductsPropertiesRelation']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'step': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'step_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '2'}),
            'uid': ('django.db.models.fields.CharField', [], {'default': "'00765938-1a50-494f-9545-3145daaaa95c'", 'unique': 'True', 'max_length': '50'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'unit_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'unit_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'unit_step': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'variants': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'catalog.propertygroup': {
            'Meta': {'ordering': "('position',)", 'object_name': 'PropertyGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'property_groups'", 'symmetrical': 'False', 'to': u"orm['catalog.Product']"})
        },
        u'catalog.staticblock': {
            'Meta': {'ordering': "('position',)", 'object_name': 'StaticBlock'},
            'display_files': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'position': ('django.db.models.fields.SmallIntegerField', [], {'default': '1000'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'manufacturer.manufacturer': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Manufacturer'},
            'active_formats': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        },
        u'order.order': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Order'},
            'account_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'bank_identification_code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer_email': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'customer_firstname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'customer_lastname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'depositor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'ia_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_invoice_address'", 'to': u"orm['contenttypes.ContentType']"}),
            'ia_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'pay_link': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payment.PaymentMethod']", 'null': 'True', 'blank': 'True'}),
            'payment_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'payment_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'requested_delivery_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sa_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_shipping_address'", 'to': u"orm['contenttypes.ContentType']"}),
            'sa_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'session': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shipping_method': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shipping.ShippingMethod']", 'null': 'True', 'blank': 'True'}),
            'shipping_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'shipping_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'state_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'cf8ce483-4c86-4af8-8218-17ac85e05152'", 'unique': 'True', 'max_length': '50'}),
            'voucher_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'voucher_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'voucher_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        u'order.orderdeliverytime': {
            'Meta': {'ordering': "('min',)", 'object_name': 'OrderDeliveryTime', '_ormbases': [u'catalog.DeliveryTime']},
            u'deliverytime_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['catalog.DeliveryTime']", 'unique': 'True', 'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'delivery_time'", 'unique': 'True', 'to': u"orm['order.Order']"})
        },
        u'order.orderitem': {
            'Meta': {'object_name': 'OrderItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': u"orm['order.Order']"}),
            'price_gross': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price_net': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalog.Product']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'product_amount': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'product_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'product_price_gross': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'product_price_net': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'product_sku': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'product_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        u'order.orderitempropertyvalue': {
            'Meta': {'object_name': 'OrderItemPropertyValue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': u"orm['order.OrderItem']"}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalog.Property']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'payment.paymentmethod': {
            'Meta': {'ordering': "('priority',)", 'object_name': 'PaymentMethod'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deletable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tax': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tax.Tax']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        u'shipping.shippingmethod': {
            'Meta': {'ordering': "('priority',)", 'object_name': 'ShippingMethod'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'delivery_time': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalog.DeliveryTime']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price_calculator': ('django.db.models.fields.CharField', [], {'default': "'lfs.shipping.GrossShippingMethodPriceCalculator'", 'max_length': '200'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tax': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tax.Tax']", 'null': 'True', 'blank': 'True'})
        },
        u'supplier.supplier': {
            'Meta': {'object_name': 'Supplier'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '80'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'tax.tax': {
            'Meta': {'object_name': 'Tax'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0'})
        }
    }

    complete_apps = ['order']