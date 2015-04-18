# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lfs.core.fields.thumbs


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('short_description', models.TextField(verbose_name='Short description', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('image', lfs.core.fields.thumbs.ImageWithThumbsField(upload_to=b'images', null=True, verbose_name='Image', blank=True)),
                ('position', models.IntegerField(default=1000, verbose_name='Position')),
                ('active_formats', models.BooleanField(default=False, verbose_name='Active formats')),
                ('product_rows', models.IntegerField(default=3, verbose_name='Product rows')),
                ('product_cols', models.IntegerField(default=3, verbose_name='Product cols')),
                ('meta_title', models.CharField(default=b'<name>', max_length=100, verbose_name='Meta title')),
                ('meta_keywords', models.TextField(verbose_name='Meta keywords', blank=True)),
                ('meta_description', models.TextField(verbose_name='Meta description', blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]
