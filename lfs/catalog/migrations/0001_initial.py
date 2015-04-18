# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import lfs.core.fields.thumbs
import lfs.catalog.models


class Migration(migrations.Migration):

    dependencies = [
        ('tax', '__first__'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('supplier', '__first__'),
        ('manufacturer', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('show_all_products', models.BooleanField(default=True, verbose_name='Show all products')),
                ('short_description', models.TextField(verbose_name='Short description', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('image', lfs.core.fields.thumbs.ImageWithThumbsField(upload_to=b'images', null=True, verbose_name='Image', blank=True)),
                ('position', models.IntegerField(default=1000, verbose_name='Position')),
                ('exclude_from_navigation', models.BooleanField(default=False, verbose_name='Exclude from navigation')),
                ('template', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Category template', choices=[(0, {b'image': b'/media/lfs/icons/product_default.png', b'name': 'Category with products', b'file': b'lfs/catalog/categories/product/default.html'}), (1, {b'image': b'/media/lfs/icons/category_square.png', b'name': 'Category with subcategories', b'file': b'lfs/catalog/categories/category/default.html'})])),
                ('active_formats', models.BooleanField(default=False, verbose_name='Active formats')),
                ('product_rows', models.IntegerField(default=3, verbose_name='Product rows')),
                ('product_cols', models.IntegerField(default=3, verbose_name='Product cols')),
                ('category_cols', models.IntegerField(default=3, verbose_name='Category cols')),
                ('meta_title', models.CharField(default=b'<name>', max_length=100, verbose_name='Meta title')),
                ('meta_keywords', models.TextField(verbose_name='Meta keywords', blank=True)),
                ('meta_description', models.TextField(verbose_name='Meta description', blank=True)),
                ('level', models.PositiveSmallIntegerField(default=1)),
                ('uid', models.CharField(default=lfs.catalog.models.get_unique_id_str, unique=True, max_length=50, editable=False)),
                ('parent', models.ForeignKey(verbose_name='Parent', blank=True, to='catalog.Category', null=True)),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='DeliveryTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min', models.FloatField(verbose_name='Min')),
                ('max', models.FloatField(verbose_name='Max')),
                ('unit', models.PositiveSmallIntegerField(default=2, verbose_name='Unit', choices=[(1, 'hours'), (2, 'days'), (3, 'weeks'), (4, 'months')])),
                ('description', models.TextField(verbose_name='Description', blank=True)),
            ],
            options={
                'ordering': ('min',),
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, blank=True)),
                ('slug', models.SlugField()),
                ('content_id', models.PositiveIntegerField(null=True, verbose_name='Content id', blank=True)),
                ('position', models.SmallIntegerField(default=999)),
                ('description', models.CharField(max_length=100, blank=True)),
                ('file', models.FileField(upload_to=b'files')),
                ('content_type', models.ForeignKey(related_name='files', verbose_name='Content type', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='FilterStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.FloatField()),
            ],
            options={
                'ordering': ['start'],
            },
        ),
        migrations.CreateModel(
            name='GroupsPropertiesRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=999, verbose_name='Position')),
            ],
            options={
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_id', models.PositiveIntegerField(null=True, verbose_name='Content id', blank=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
                ('image', lfs.core.fields.thumbs.ImageWithThumbsField(upload_to=b'images', null=True, verbose_name='Image', blank=True)),
                ('position', models.PositiveSmallIntegerField(default=999, verbose_name='Position')),
                ('content_type', models.ForeignKey(related_name='image', verbose_name='Content type', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The name of the product.', max_length=80, verbose_name='Name', blank=True)),
                ('slug', models.SlugField(help_text="The unique last part of the Product's URL.", unique=True, max_length=120, verbose_name='Slug')),
                ('sku', models.CharField(help_text='Your unique article number of the product.', max_length=30, verbose_name='SKU', blank=True)),
                ('price', models.FloatField(default=0.0, verbose_name='Price')),
                ('price_calculator', models.CharField(blank=True, max_length=255, null=True, verbose_name='Price calculator', choices=[[b'lfs.gross_price.GrossPriceCalculator', 'Price includes tax'], [b'lfs.net_price.NetPriceCalculator', 'Price excludes tax']])),
                ('effective_price', models.FloatField(verbose_name='Price', blank=True)),
                ('price_unit', models.CharField(blank=True, max_length=20, verbose_name='Price unit', choices=[['l', 'l'], ['m', 'm'], ['qm', 'qm'], ['cm', 'cm'], ['lfm', 'lfm'], ['Package', 'Package'], ['Piece', 'Piece']])),
                ('unit', models.CharField(blank=True, max_length=20, verbose_name='Quantity field unit', choices=[['l', 'l'], ['m', 'm'], ['qm', 'qm'], ['cm', 'cm'], ['lfm', 'lfm'], ['Package', 'Package'], ['Piece', 'Piece']])),
                ('short_description', models.TextField(verbose_name='Short description', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('meta_title', models.CharField(default=b'<name>', max_length=80, verbose_name='Meta title', blank=True)),
                ('meta_keywords', models.TextField(verbose_name='Meta keywords', blank=True)),
                ('meta_description', models.TextField(verbose_name='Meta description', blank=True)),
                ('for_sale', models.BooleanField(default=False, verbose_name='For sale')),
                ('for_sale_price', models.FloatField(default=0.0, verbose_name='For sale price')),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('deliverable', models.BooleanField(default=True, verbose_name='Deliverable')),
                ('manual_delivery_time', models.BooleanField(default=False, verbose_name='Manual delivery time')),
                ('ordered_at', models.DateField(null=True, verbose_name='Ordered at', blank=True)),
                ('manage_stock_amount', models.BooleanField(default=False, verbose_name='Manage stock amount')),
                ('stock_amount', models.FloatField(default=0, verbose_name='Stock amount')),
                ('active_packing_unit', models.PositiveSmallIntegerField(default=0, verbose_name='Active packing')),
                ('packing_unit', models.FloatField(null=True, verbose_name='Amount per packing', blank=True)),
                ('packing_unit_unit', models.CharField(blank=True, max_length=30, verbose_name='Packing unit', choices=[['l', 'l'], ['m', 'm'], ['qm', 'qm'], ['cm', 'cm'], ['lfm', 'lfm'], ['Package', 'Package'], ['Piece', 'Piece']])),
                ('weight', models.FloatField(default=0.0, verbose_name='Weight')),
                ('height', models.FloatField(default=0.0, verbose_name='Height')),
                ('length', models.FloatField(default=0.0, verbose_name='Length')),
                ('width', models.FloatField(default=0.0, verbose_name='Width')),
                ('sub_type', models.CharField(default=b'0', max_length=10, verbose_name='Subtype', choices=[(b'0', 'Standard'), (b'1', 'Product with variants'), (b'2', 'Variant'), (b'3', 'Configurable product')])),
                ('category_variant', models.SmallIntegerField(null=True, verbose_name='Category variant', blank=True)),
                ('variants_display_type', models.IntegerField(default=0, verbose_name='Variants display type', choices=[(0, 'List'), (1, 'Select')])),
                ('variant_position', models.IntegerField(default=999)),
                ('active_name', models.BooleanField(default=False, verbose_name='Active name')),
                ('active_sku', models.BooleanField(default=False, verbose_name='Active SKU')),
                ('active_short_description', models.BooleanField(default=False, verbose_name='Active short description')),
                ('active_static_block', models.BooleanField(default=False, verbose_name='Active static bock')),
                ('active_description', models.BooleanField(default=False, verbose_name='Active description')),
                ('active_price', models.BooleanField(default=False, verbose_name='Active price')),
                ('active_for_sale', models.PositiveSmallIntegerField(default=0, verbose_name='Active for sale', choices=[(0, 'Standard'), (2, 'Yes'), (3, 'No')])),
                ('active_for_sale_price', models.BooleanField(default=False, verbose_name='Active for sale price')),
                ('active_images', models.BooleanField(default=False, verbose_name='Active Images')),
                ('active_related_products', models.BooleanField(default=False, verbose_name='Active related products')),
                ('active_accessories', models.BooleanField(default=False, verbose_name='Active accessories')),
                ('active_meta_title', models.BooleanField(default=False, verbose_name='Active meta title')),
                ('active_meta_description', models.BooleanField(default=False, verbose_name='Active meta description')),
                ('active_meta_keywords', models.BooleanField(default=False, verbose_name='Active meta keywords')),
                ('active_dimensions', models.BooleanField(default=False, verbose_name='Active dimensions')),
                ('template', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Product template', choices=[(0, {b'image': b'/media/lfs/icons/product_default.png', b'name': 'Default', b'file': b'lfs/catalog/products/product_inline.html'})])),
                ('active_price_calculation', models.BooleanField(default=False, verbose_name='Active price calculation')),
                ('price_calculation', models.CharField(max_length=100, verbose_name='Price Calculation', blank=True)),
                ('active_base_price', models.PositiveSmallIntegerField(default=0, verbose_name='Active base price')),
                ('base_price_unit', models.CharField(blank=True, max_length=30, verbose_name='Base price unit', choices=[['l', 'l'], ['m', 'm'], ['qm', 'qm'], ['cm', 'cm'], ['lfm', 'lfm'], ['Package', 'Package'], ['Piece', 'Piece']])),
                ('base_price_amount', models.FloatField(default=0.0, null=True, verbose_name='Base price amount', blank=True)),
                ('sku_manufacturer', models.CharField(max_length=100, verbose_name='SKU Manufacturer', blank=True)),
                ('type_of_quantity_field', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Type of quantity field', choices=[(0, 'Integer'), (1, 'Decimal 0.1'), (2, 'Decimal 0.01')])),
                ('uid', models.CharField(default=lfs.catalog.models.get_unique_id_str, unique=True, max_length=50, editable=False)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ProductAccessories',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=999, verbose_name='Position')),
                ('quantity', models.FloatField(default=1, verbose_name='Quantity')),
                ('accessory', models.ForeignKey(related_name='productaccessories_accessory', verbose_name='Accessory', to='catalog.Product')),
                ('product', models.ForeignKey(related_name='productaccessories_product', verbose_name='Product', to='catalog.Product')),
            ],
            options={
                'ordering': ('position',),
                'verbose_name_plural': 'Product accessories',
            },
        ),
        migrations.CreateModel(
            name='ProductAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('file', models.FileField(max_length=500, upload_to=b'files')),
                ('position', models.IntegerField(default=1, verbose_name='Position')),
                ('product', models.ForeignKey(related_name='attachments', verbose_name='Product', to='catalog.Product')),
            ],
            options={
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='ProductPropertyValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent_id', models.IntegerField(null=True, verbose_name='Parent', blank=True)),
                ('value', models.CharField(max_length=100, verbose_name='Value', blank=True)),
                ('value_as_float', models.FloatField(null=True, verbose_name='Value as float', blank=True)),
                ('type', models.PositiveSmallIntegerField(verbose_name='Type')),
                ('product', models.ForeignKey(related_name='property_values', verbose_name='Product', to='catalog.Product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductsPropertiesRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=999, verbose_name='Position')),
                ('product', models.ForeignKey(related_name='productsproperties', verbose_name='Product', to='catalog.Product')),
            ],
            options={
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('position', models.IntegerField(null=True, verbose_name='Position', blank=True)),
                ('unit', models.CharField(max_length=15, verbose_name='Unit', blank=True)),
                ('display_on_product', models.BooleanField(default=False, verbose_name='Display on product')),
                ('local', models.BooleanField(default=False, verbose_name='Local')),
                ('variants', models.BooleanField(default=False, verbose_name='For Variants')),
                ('filterable', models.BooleanField(default=False, verbose_name='Filterable')),
                ('configurable', models.BooleanField(default=False, verbose_name='Configurable')),
                ('type', models.PositiveSmallIntegerField(default=2, verbose_name='Type', choices=[(1, 'Float field'), (2, 'Text field'), (3, 'Select field')])),
                ('price', models.FloatField(null=True, verbose_name='Price', blank=True)),
                ('display_price', models.BooleanField(default=True, verbose_name='Display price')),
                ('add_price', models.BooleanField(default=True, verbose_name='Add price')),
                ('unit_min', models.FloatField(null=True, verbose_name='Min', blank=True)),
                ('unit_max', models.FloatField(null=True, verbose_name='Max', blank=True)),
                ('unit_step', models.FloatField(null=True, verbose_name='Step', blank=True)),
                ('decimal_places', models.PositiveSmallIntegerField(default=0, verbose_name='Decimal places')),
                ('required', models.BooleanField(default=False, verbose_name='Required')),
                ('step_type', models.PositiveSmallIntegerField(default=1, verbose_name='Step type', choices=[(1, 'Automatic'), (2, 'Fixed step'), (3, 'Manual steps')])),
                ('step', models.IntegerField(null=True, verbose_name='Step', blank=True)),
                ('uid', models.CharField(default=lfs.catalog.models.get_unique_id_str, unique=True, max_length=50, editable=False)),
            ],
            options={
                'ordering': ['position'],
                'verbose_name_plural': 'Properties',
            },
        ),
        migrations.CreateModel(
            name='PropertyGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name', blank=True)),
                ('position', models.IntegerField(default=1000, verbose_name='Position')),
                ('uid', models.CharField(default=lfs.catalog.models.get_unique_id_str, unique=True, max_length=50, editable=False)),
                ('products', models.ManyToManyField(related_name='property_groups', verbose_name='Products', to='catalog.Product')),
            ],
            options={
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='PropertyOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('price', models.FloatField(default=0.0, null=True, verbose_name='Price', blank=True)),
                ('position', models.IntegerField(default=99, verbose_name='Position')),
                ('uid', models.CharField(default=lfs.catalog.models.get_unique_id_str, unique=True, max_length=50, editable=False)),
                ('property', models.ForeignKey(related_name='options', verbose_name='Property', to='catalog.Property')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='StaticBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='Name')),
                ('display_files', models.BooleanField(default=True, verbose_name='Display files')),
                ('html', models.TextField(verbose_name='HTML', blank=True)),
                ('position', models.SmallIntegerField(default=1000, verbose_name='Position')),
            ],
            options={
                'ordering': ('position',),
            },
        ),
        migrations.AddField(
            model_name='property',
            name='groups',
            field=models.ManyToManyField(related_name='properties', verbose_name='Group', to='catalog.PropertyGroup', through='catalog.GroupsPropertiesRelation', blank=True),
        ),
        migrations.AddField(
            model_name='property',
            name='products',
            field=models.ManyToManyField(related_name='properties', verbose_name='Products', to='catalog.Product', through='catalog.ProductsPropertiesRelation', blank=True),
        ),
        migrations.AddField(
            model_name='productspropertiesrelation',
            name='property',
            field=models.ForeignKey(verbose_name='Property', to='catalog.Property'),
        ),
        migrations.AddField(
            model_name='productpropertyvalue',
            name='property',
            field=models.ForeignKey(related_name='property_values', verbose_name='Property', to='catalog.Property'),
        ),
        migrations.AddField(
            model_name='productpropertyvalue',
            name='property_group',
            field=models.ForeignKey(related_name='property_values', verbose_name='Property group', blank=True, to='catalog.PropertyGroup', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='accessories',
            field=models.ManyToManyField(related_name='reverse_accessories', verbose_name='Acessories', to='catalog.Product', through='catalog.ProductAccessories', blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='default_variant',
            field=models.ForeignKey(verbose_name='Default variant', blank=True, to='catalog.Product', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='delivery_time',
            field=models.ForeignKey(related_name='products_delivery_time', verbose_name='Delivery time', blank=True, to='catalog.DeliveryTime', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer',
            field=models.ForeignKey(related_name='products', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Manufacturer', blank=True, to='manufacturer.Manufacturer', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='order_time',
            field=models.ForeignKey(related_name='products_order_time', verbose_name='Order time', blank=True, to='catalog.DeliveryTime', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='parent',
            field=models.ForeignKey(related_name='variants', verbose_name='Parent', blank=True, to='catalog.Product', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='related_products',
            field=models.ManyToManyField(related_name='reverse_related_products', verbose_name='Related products', to='catalog.Product', blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='static_block',
            field=models.ForeignKey(related_name='products', verbose_name='Static block', blank=True, to='catalog.StaticBlock', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='supplier',
            field=models.ForeignKey(related_name='product_set', blank=True, to='supplier.Supplier', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='tax',
            field=models.ForeignKey(verbose_name='Tax', blank=True, to='tax.Tax', null=True),
        ),
        migrations.AddField(
            model_name='groupspropertiesrelation',
            name='group',
            field=models.ForeignKey(related_name='groupproperties', verbose_name='Group', to='catalog.PropertyGroup'),
        ),
        migrations.AddField(
            model_name='groupspropertiesrelation',
            name='property',
            field=models.ForeignKey(verbose_name='Property', to='catalog.Property'),
        ),
        migrations.AddField(
            model_name='filterstep',
            name='property',
            field=models.ForeignKey(related_name='steps', verbose_name='Property', to='catalog.Property'),
        ),
        migrations.AddField(
            model_name='category',
            name='products',
            field=models.ManyToManyField(related_name='categories', verbose_name='Products', to='catalog.Product', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='static_block',
            field=models.ForeignKey(related_name='categories', verbose_name='Static block', blank=True, to='catalog.StaticBlock', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='productspropertiesrelation',
            unique_together=set([('product', 'property')]),
        ),
        migrations.AlterUniqueTogether(
            name='productpropertyvalue',
            unique_together=set([('product', 'property', 'property_group', 'value', 'type')]),
        ),
        migrations.AlterUniqueTogether(
            name='groupspropertiesrelation',
            unique_together=set([('group', 'property')]),
        ),
    ]
