# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.template.defaultfilters import slugify
from lfs.manufacturer.models import Manufacturer
from lfs.core.fields.thumbs import ImageWithThumbsField

class Migration(SchemaMigration):
    no_dry_run = True
    def forwards(self, orm):
        # Manufacturers
        # Adding field 'Manufacturer.position'
        db.add_column('manufacturer_manufacturer', 'position', models.IntegerField(default=1000), keep_default=False)
        
        # Adding field 'Manufacturer.short_description'
        db.add_column('manufacturer_manufacturer', 'short_description', models.TextField(default='', blank=True), keep_default=False)
        
        # Adding field 'Manufacturer.description'
        db.add_column('manufacturer_manufacturer', 'description', models.TextField(default='', blank=True), keep_default=False)
        
        # Adding field 'Manufacturer.image'
        db.add_column('manufacturer_manufacturer', 'image', ImageWithThumbsField(blank=True, max_length=100, null=True, sizes=((60, 60), (100, 100), (200, 200), (400, 400))), keep_default=False)
        
        # Adding field 'Manufacturer.meta_title'
        db.add_column('manufacturer_manufacturer', 'meta_title', models.CharField(default='<name>', max_length=100), keep_default=False)
        
        # Adding field 'Manufacturer.meta_keywords'
        db.add_column('manufacturer_manufacturer', 'meta_keywords', models.TextField(default='', blank=True), keep_default=False)
        
        # Adding field 'Manufacturer.meta_description'
        db.add_column('manufacturer_manufacturer', 'meta_description', models.TextField(default='', blank=True), keep_default=False)
        
        # Adding field 'Manufacturer.slug'
        db.add_column('manufacturer_manufacturer', 'slug', models.SlugField(default='', max_length=50, db_index=True, null=True), keep_default=False)
        
        # Adding field 'Manufacturer.active_formats'
        db.add_column('manufacturer_manufacturer', 'active_formats', models.fields.BooleanField(default=False), keep_default=False)
        
        # Adding field 'Manufacturer.product_rows'
        db.add_column('manufacturer_manufacturer', 'product_rows', models.fields.IntegerField(default=3), keep_default=False)
        
        # Adding field 'Manufacturer.product_cols'
        db.add_column('manufacturer_manufacturer', 'product_cols', models.fields.IntegerField(default=3), keep_default=False)
        
        for i, manufacturer in enumerate(Manufacturer.objects.all()):
            manufacturer.slug = slugify(manufacturer.name)
            manufacturer.position = (i + 1) * 10
            manufacturer.save()
        
        # Set field 'Manufacturer.slug' to not null
        db.alter_column('manufacturer_manufacturer', 'slug', models.SlugField(unique=True, max_length=50))
    
    def backwards(self, orm):
        db.delete_column('manufacturer_manufacturer', 'position')
        db.delete_column('manufacturer_manufacturer', 'short_description')
        db.delete_column('manufacturer_manufacturer', 'description')
        db.delete_column('manufacturer_manufacturer', 'image')
        db.delete_column('manufacturer_manufacturer', 'meta_title')
        db.delete_column('manufacturer_manufacturer', 'meta_keywords')
        db.delete_column('manufacturer_manufacturer', 'meta_description')
        db.delete_column('manufacturer_manufacturer', 'slug')
        db.delete_column('manufacturer_manufacturer', 'active_formats')
        db.delete_column('manufacturer_manufacturer', 'product_rows')
        db.delete_column('manufacturer_manufacturer', 'product_cols')
        
