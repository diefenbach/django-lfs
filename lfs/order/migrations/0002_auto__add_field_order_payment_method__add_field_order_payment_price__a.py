# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ("payment", "0001_initial"),
    )

    def forwards(self, orm):
        # Adding field 'Order.payment_method'
        db.add_column('order_order', 'payment_method',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.PaymentMethod'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Order.payment_price'
        db.add_column('order_order', 'payment_price',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)

        # Adding field 'Order.payment_tax'
        db.add_column('order_order', 'payment_tax',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Order.payment_method'
        db.delete_column('order_order', 'payment_method_id')

        # Deleting field 'Order.payment_price'
        db.delete_column('order_order', 'payment_price')

        # Deleting field 'Order.payment_tax'
        db.delete_column('order_order', 'payment_tax')


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
        'catalog.groupspropertiesrelation': {
            'Meta': {'ordering': "('position',)", 'unique_together': "(('group', 'property'),)", 'object_name': 'GroupsPropertiesRelation'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groupproperties'", 'to': "orm['catalog.PropertyGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.Property']"})
        },
        'catalog.image': {
            'Meta': {'ordering': "('position',)", 'object_name': 'Image'},
            'content_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'image'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('lfs.core.fields.thumbs.ImageWithThumbsField', [], {'blank': 'True', 'max_length': '100', 'null': 'True', 'sizes': '((60, 60), (100, 100), (200, 200), (300, 300), (400, 400))'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '999'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'catalog.product': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Product'},
            'accessories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'reverse_accessories'", 'to': "orm['catalog.Product']", 'through': "orm['catalog.ProductAccessories']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
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
            'default_variant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.Product']", 'null': 'True', 'blank': 'True'}),
            'deliverable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'delivery_time': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products_delivery_time'", 'null': 'True', 'to': "orm['catalog.DeliveryTime']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'effective_price': ('django.db.models.fields.FloatField', [], {'blank': 'True'}),
            'for_sale': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'for_sale_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'height': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'manage_stock_amount': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manual_delivery_time': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['manufacturer.Manufacturer']"}),
            'meta_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'default': "'<name>'", 'max_length': '80', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'order_time': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products_order_time'", 'null': 'True', 'to': "orm['catalog.DeliveryTime']"}),
            'ordered_at': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'packing_unit': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'packing_unit_unit': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'variants'", 'null': 'True', 'to': "orm['catalog.Product']"}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price_calculation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'price_calculator': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'price_unit': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'related_products': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'reverse_related_products'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['catalog.Product']"}),
            'short_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'sku_manufacturer': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '80'}),
            'static_block': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products'", 'null': 'True', 'to': "orm['catalog.StaticBlock']"}),
            'stock_amount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sub_type': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '10'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['supplier.Supplier']", 'null': 'True', 'blank': 'True'}),
            'tax': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tax.Tax']", 'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type_of_quantity_field': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'default': "'cb59daf2-1cc9-4ba2-a934-25c344a1b12d'", 'unique': 'True', 'max_length': '50'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'variant_position': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'variants_display_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'weight': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'width': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'catalog.productaccessories': {
            'Meta': {'ordering': "('position',)", 'object_name': 'ProductAccessories'},
            'accessory': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'productaccessories_accessory'", 'to': "orm['catalog.Product']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'productaccessories_product'", 'to': "orm['catalog.Product']"}),
            'quantity': ('django.db.models.fields.FloatField', [], {'default': '1'})
        },
        'catalog.productspropertiesrelation': {
            'Meta': {'ordering': "('position',)", 'unique_together': "(('product', 'property'),)", 'object_name': 'ProductsPropertiesRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'productsproperties'", 'to': "orm['catalog.Product']"}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.Property']"})
        },
        'catalog.property': {
            'Meta': {'ordering': "['position']", 'object_name': 'Property'},
            'add_price': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'configurable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'decimal_places': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'display_no_results': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_on_product': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'display_price': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'filterable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'properties'", 'to': "orm['catalog.PropertyGroup']", 'through': "orm['catalog.GroupsPropertiesRelation']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'position': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'properties'", 'to': "orm['catalog.Product']", 'through': "orm['catalog.ProductsPropertiesRelation']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'step': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'step_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '2'}),
            'uid': ('django.db.models.fields.CharField', [], {'default': "'c9fb0c31-0cb2-4b62-ae8b-5ddf61ffb863'", 'unique': 'True', 'max_length': '50'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'unit_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'unit_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'unit_step': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'catalog.propertygroup': {
            'Meta': {'ordering': "('name',)", 'object_name': 'PropertyGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'property_groups'", 'symmetrical': 'False', 'to': "orm['catalog.Product']"})
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
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'53332611-888f-444f-b93a-68fd84ece8ff'", 'unique': 'True', 'max_length': '50'}),
            'voucher_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'voucher_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'voucher_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'order.orderitem': {
            'Meta': {'object_name': 'OrderItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['order.Order']"}),
            'price_gross': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price_net': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.Product']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'product_amount': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'product_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'product_price_gross': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'product_price_net': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'product_sku': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'product_tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'order.orderitempropertyvalue': {
            'Meta': {'object_name': 'OrderItemPropertyValue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': "orm['order.OrderItem']"}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.Property']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
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
        'supplier.supplier': {
            'Meta': {'object_name': 'Supplier'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '80'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'tax.tax': {
            'Meta': {'object_name': 'Tax'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0'})
        }
    }

    complete_apps = ['order']