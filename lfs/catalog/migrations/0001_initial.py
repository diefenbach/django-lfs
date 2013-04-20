# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ("supplier", "0001_initial"),
        ("tax", "0001_initial"),
        ("manufacturer", "0001_initial"),
    )

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('catalog_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.Category'], null=True, blank=True)),
            ('show_all_products', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('short_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('lfs.core.fields.thumbs.ImageWithThumbsField')(blank=True, max_length=100, null=True, sizes=((60, 60), (100, 100), (200, 200), (400, 400)))),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=1000)),
            ('exclude_from_navigation', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('static_block', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='categories', null=True, to=orm['catalog.StaticBlock'])),
            ('template', self.gf('django.db.models.fields.PositiveSmallIntegerField')(max_length=400, null=True, blank=True)),
            ('active_formats', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('product_rows', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('product_cols', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('category_cols', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('meta_title', self.gf('django.db.models.fields.CharField')(default='<name>', max_length=100)),
            ('meta_keywords', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('meta_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('level', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('uid', self.gf('django.db.models.fields.CharField')(default='b870c3fb-0cf0-480b-ae58-670316ce281b', unique=True, max_length=50)),
        ))
        db.send_create_signal('catalog', ['Category'])

        # Adding M2M table for field products on 'Category'
        db.create_table('catalog_category_products', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(orm['catalog.category'], null=False)),
            ('product', models.ForeignKey(orm['catalog.product'], null=False))
        ))
        db.create_unique('catalog_category_products', ['category_id', 'product_id'])

        # Adding model 'Product'
        db.create_table('catalog_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=80)),
            ('sku', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('price', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('price_calculator', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('effective_price', self.gf('django.db.models.fields.FloatField')(blank=True)),
            ('price_unit', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('short_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('meta_title', self.gf('django.db.models.fields.CharField')(default='<name>', max_length=80, blank=True)),
            ('meta_keywords', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('meta_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('for_sale', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('for_sale_price', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('supplier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['supplier.Supplier'], null=True, blank=True)),
            ('deliverable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('manual_delivery_time', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('delivery_time', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='products_delivery_time', null=True, to=orm['catalog.DeliveryTime'])),
            ('order_time', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='products_order_time', null=True, to=orm['catalog.DeliveryTime'])),
            ('ordered_at', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('manage_stock_amount', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('stock_amount', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('active_packing_unit', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('packing_unit', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('packing_unit_unit', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('static_block', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='products', null=True, to=orm['catalog.StaticBlock'])),
            ('weight', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('height', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('length', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('width', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('tax', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tax.Tax'], null=True, blank=True)),
            ('sub_type', self.gf('django.db.models.fields.CharField')(default='0', max_length=10)),
            ('default_variant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.Product'], null=True, blank=True)),
            ('category_variant', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('variants_display_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('variant_position', self.gf('django.db.models.fields.IntegerField')(default=999)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='variants', null=True, to=orm['catalog.Product'])),
            ('active_name', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_sku', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_short_description', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_static_block', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_description', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_price', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_for_sale', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('active_for_sale_price', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_images', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_related_products', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_accessories', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_meta_title', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_meta_description', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_meta_keywords', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active_dimensions', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('template', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('active_price_calculation', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('price_calculation', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('active_base_price', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('base_price_unit', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('base_price_amount', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('sku_manufacturer', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('manufacturer', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='products', null=True, to=orm['manufacturer.Manufacturer'])),
            ('type_of_quantity_field', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(default='cf3cfe03-8587-42b7-b539-373b820046e4', unique=True, max_length=50)),
        ))
        db.send_create_signal('catalog', ['Product'])

        # Adding M2M table for field related_products on 'Product'
        db.create_table('catalog_product_related_products', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_product', models.ForeignKey(orm['catalog.product'], null=False)),
            ('to_product', models.ForeignKey(orm['catalog.product'], null=False))
        ))
        db.create_unique('catalog_product_related_products', ['from_product_id', 'to_product_id'])

        # Adding model 'ProductAccessories'
        db.create_table('catalog_productaccessories', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='productaccessories_product', to=orm['catalog.Product'])),
            ('accessory', self.gf('django.db.models.fields.related.ForeignKey')(related_name='productaccessories_accessory', to=orm['catalog.Product'])),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=999)),
            ('quantity', self.gf('django.db.models.fields.FloatField')(default=1)),
        ))
        db.send_create_signal('catalog', ['ProductAccessories'])

        # Adding model 'PropertyGroup'
        db.create_table('catalog_propertygroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('catalog', ['PropertyGroup'])

        # Adding M2M table for field products on 'PropertyGroup'
        db.create_table('catalog_propertygroup_products', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('propertygroup', models.ForeignKey(orm['catalog.propertygroup'], null=False)),
            ('product', models.ForeignKey(orm['catalog.product'], null=False))
        ))
        db.create_unique('catalog_propertygroup_products', ['propertygroup_id', 'product_id'])

        # Adding model 'Property'
        db.create_table('catalog_property', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('position', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=15, blank=True)),
            ('display_on_product', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('local', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('filterable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('display_no_results', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('configurable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=2)),
            ('price', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('display_price', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('add_price', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('unit_min', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('unit_max', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('unit_step', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('decimal_places', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('step_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('step', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(default='78ef0456-a083-40d9-8a36-cc16ba6360a5', unique=True, max_length=50)),
        ))
        db.send_create_signal('catalog', ['Property'])

        # Adding model 'FilterStep'
        db.create_table('catalog_filterstep', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(related_name='steps', to=orm['catalog.Property'])),
            ('start', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('catalog', ['FilterStep'])

        # Adding model 'GroupsPropertiesRelation'
        db.create_table('catalog_groupspropertiesrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='groupproperties', to=orm['catalog.PropertyGroup'])),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.Property'])),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=999)),
        ))
        db.send_create_signal('catalog', ['GroupsPropertiesRelation'])

        # Adding unique constraint on 'GroupsPropertiesRelation', fields ['group', 'property']
        db.create_unique('catalog_groupspropertiesrelation', ['group_id', 'property_id'])

        # Adding model 'ProductsPropertiesRelation'
        db.create_table('catalog_productspropertiesrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='productsproperties', to=orm['catalog.Product'])),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.Property'])),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=999)),
        ))
        db.send_create_signal('catalog', ['ProductsPropertiesRelation'])

        # Adding unique constraint on 'ProductsPropertiesRelation', fields ['product', 'property']
        db.create_unique('catalog_productspropertiesrelation', ['product_id', 'property_id'])

        # Adding model 'PropertyOption'
        db.create_table('catalog_propertyoption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(related_name='options', to=orm['catalog.Property'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('price', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=99)),
            ('uid', self.gf('django.db.models.fields.CharField')(default='04c97a37-e155-4740-9934-74d6b1907eb5', unique=True, max_length=50)),
        ))
        db.send_create_signal('catalog', ['PropertyOption'])

        # Adding model 'ProductPropertyValue'
        db.create_table('catalog_productpropertyvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='property_values', to=orm['catalog.Product'])),
            ('parent_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(related_name='property_values', to=orm['catalog.Property'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('value_as_float', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal('catalog', ['ProductPropertyValue'])

        # Adding unique constraint on 'ProductPropertyValue', fields ['product', 'property', 'value', 'type']
        db.create_unique('catalog_productpropertyvalue', ['product_id', 'property_id', 'value', 'type'])

        # Adding model 'Image'
        db.create_table('catalog_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='image', null=True, to=orm['contenttypes.ContentType'])),
            ('content_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('image', self.gf('lfs.core.fields.thumbs.ImageWithThumbsField')(blank=True, max_length=100, null=True, sizes=((60, 60), (100, 100), (200, 200), (300, 300), (400, 400)))),
            ('position', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=999)),
        ))
        db.send_create_signal('catalog', ['Image'])

        # Adding model 'File'
        db.create_table('catalog_file', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='files', null=True, to=orm['contenttypes.ContentType'])),
            ('content_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('position', self.gf('django.db.models.fields.SmallIntegerField')(default=999)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('catalog', ['File'])

        # Adding model 'StaticBlock'
        db.create_table('catalog_staticblock', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('display_files', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('position', self.gf('django.db.models.fields.SmallIntegerField')(default=1000)),
        ))
        db.send_create_signal('catalog', ['StaticBlock'])

        # Adding model 'DeliveryTime'
        db.create_table('catalog_deliverytime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('min', self.gf('django.db.models.fields.FloatField')()),
            ('max', self.gf('django.db.models.fields.FloatField')()),
            ('unit', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=2)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('catalog', ['DeliveryTime'])

        # Adding model 'ProductAttachment'
        db.create_table('catalog_productattachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['catalog.Product'])),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('catalog', ['ProductAttachment'])


    def backwards(self, orm):
        # Removing unique constraint on 'ProductPropertyValue', fields ['product', 'property', 'value', 'type']
        db.delete_unique('catalog_productpropertyvalue', ['product_id', 'property_id', 'value', 'type'])

        # Removing unique constraint on 'ProductsPropertiesRelation', fields ['product', 'property']
        db.delete_unique('catalog_productspropertiesrelation', ['product_id', 'property_id'])

        # Removing unique constraint on 'GroupsPropertiesRelation', fields ['group', 'property']
        db.delete_unique('catalog_groupspropertiesrelation', ['group_id', 'property_id'])

        # Deleting model 'Category'
        db.delete_table('catalog_category')

        # Removing M2M table for field products on 'Category'
        db.delete_table('catalog_category_products')

        # Deleting model 'Product'
        db.delete_table('catalog_product')

        # Removing M2M table for field related_products on 'Product'
        db.delete_table('catalog_product_related_products')

        # Deleting model 'ProductAccessories'
        db.delete_table('catalog_productaccessories')

        # Deleting model 'PropertyGroup'
        db.delete_table('catalog_propertygroup')

        # Removing M2M table for field products on 'PropertyGroup'
        db.delete_table('catalog_propertygroup_products')

        # Deleting model 'Property'
        db.delete_table('catalog_property')

        # Deleting model 'FilterStep'
        db.delete_table('catalog_filterstep')

        # Deleting model 'GroupsPropertiesRelation'
        db.delete_table('catalog_groupspropertiesrelation')

        # Deleting model 'ProductsPropertiesRelation'
        db.delete_table('catalog_productspropertiesrelation')

        # Deleting model 'PropertyOption'
        db.delete_table('catalog_propertyoption')

        # Deleting model 'ProductPropertyValue'
        db.delete_table('catalog_productpropertyvalue')

        # Deleting model 'Image'
        db.delete_table('catalog_image')

        # Deleting model 'File'
        db.delete_table('catalog_file')

        # Deleting model 'StaticBlock'
        db.delete_table('catalog_staticblock')

        # Deleting model 'DeliveryTime'
        db.delete_table('catalog_deliverytime')

        # Deleting model 'ProductAttachment'
        db.delete_table('catalog_productattachment')


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
        'catalog.category': {
            'Meta': {'ordering': "('position',)", 'object_name': 'Category'},
            'active_formats': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category_cols': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'exclude_from_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('lfs.core.fields.thumbs.ImageWithThumbsField', [], {'blank': 'True', 'max_length': '100', 'null': 'True', 'sizes': '((60, 60), (100, 100), (200, 200), (400, 400))'}),
            'level': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'default': "'<name>'", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.Category']", 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'product_cols': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'product_rows': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'categories'", 'blank': 'True', 'to': "orm['catalog.Product']"}),
            'short_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'show_all_products': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'static_block': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'categories'", 'null': 'True', 'to': "orm['catalog.StaticBlock']"}),
            'template': ('django.db.models.fields.PositiveSmallIntegerField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'default': "'0efb7bd1-afaf-4a05-8aa1-f0660388a53f'", 'unique': 'True', 'max_length': '50'})
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
        'catalog.filterstep': {
            'Meta': {'ordering': "['start']", 'object_name': 'FilterStep'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'steps'", 'to': "orm['catalog.Property']"}),
            'start': ('django.db.models.fields.FloatField', [], {})
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
            'uid': ('django.db.models.fields.CharField', [], {'default': "'c3c4f61d-7698-4881-b253-8886ea142650'", 'unique': 'True', 'max_length': '50'}),
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
        'catalog.productattachment': {
            'Meta': {'ordering': "('position',)", 'object_name': 'ProductAttachment'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['catalog.Product']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'catalog.productpropertyvalue': {
            'Meta': {'unique_together': "(('product', 'property', 'value', 'type'),)", 'object_name': 'ProductPropertyValue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'property_values'", 'to': "orm['catalog.Product']"}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'property_values'", 'to': "orm['catalog.Property']"}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'value_as_float': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
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
            'uid': ('django.db.models.fields.CharField', [], {'default': "'7f8d5f20-eccf-47e7-80a0-3b316bcea88b'", 'unique': 'True', 'max_length': '50'}),
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
        'catalog.propertyoption': {
            'Meta': {'ordering': "['position']", 'object_name': 'PropertyOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '99'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'options'", 'to': "orm['catalog.Property']"}),
            'uid': ('django.db.models.fields.CharField', [], {'default': "'e4f4854e-4b74-49e0-a4b1-2d230e1ce28f'", 'unique': 'True', 'max_length': '50'})
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

    complete_apps = ['catalog']