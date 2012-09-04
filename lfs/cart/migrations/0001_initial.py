# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cart'
        db.create_table('cart_cart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('session', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('cart', ['Cart'])

        # Adding model 'CartItem'
        db.create_table('cart_cartitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cart.Cart'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.Product'])),
            ('amount', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('cart', ['CartItem'])

        # Adding model 'CartItemPropertyValue'
        db.create_table('cart_cartitempropertyvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cart_item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='properties', to=orm['cart.CartItem'])),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.Property'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('cart', ['CartItemPropertyValue'])


    def backwards(self, orm):
        # Deleting model 'Cart'
        db.delete_table('cart_cart')

        # Deleting model 'CartItem'
        db.delete_table('cart_cartitem')

        # Deleting model 'CartItemPropertyValue'
        db.delete_table('cart_cartitempropertyvalue')


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
        'cart.cart': {
            'Meta': {'object_name': 'Cart'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'session': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'cart.cartitem': {
            'Meta': {'ordering': "['id']", 'object_name': 'CartItem'},
            'amount': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'cart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cart.Cart']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.Product']"})
        },
        'cart.cartitempropertyvalue': {
            'Meta': {'object_name': 'CartItemPropertyValue'},
            'cart_item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': "orm['cart.CartItem']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.Property']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
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
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products'", 'null': 'True', 'to': "orm['manufacturer.Manufacturer']"}),
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
            'uid': ('django.db.models.fields.CharField', [], {'default': "'03b3bfbe-d913-48c2-a884-2ad6d1c2e7c0'", 'unique': 'True', 'max_length': '50'}),
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
            'uid': ('django.db.models.fields.CharField', [], {'default': "'cb33a13e-f618-45cb-a8f9-44327372d036'", 'unique': 'True', 'max_length': '50'}),
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

    complete_apps = ['cart']