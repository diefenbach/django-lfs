# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AverageRatingPortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CartPortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CategoriesPortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
                ('start_level', models.PositiveSmallIntegerField(default=1)),
                ('expand_level', models.PositiveSmallIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryTimePortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FeaturedPortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
                ('limit', models.IntegerField(default=5, verbose_name='Limit')),
                ('current_category', models.BooleanField(default=False, verbose_name='Use current category')),
                ('slideshow', models.BooleanField(default=False, verbose_name='Slideshow')),
            ],
        ),
        migrations.CreateModel(
            name='FilterPortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
                ('show_product_filters', models.BooleanField(default=True, verbose_name='Show product filters')),
                ('show_price_filters', models.BooleanField(default=True, verbose_name='Show price filters')),
                ('show_manufacturer_filters', models.BooleanField(default=False, verbose_name='Show manufacturer filters')),
            ],
        ),
        migrations.CreateModel(
            name='ForsalePortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
                ('limit', models.IntegerField(default=5, verbose_name='Limit')),
                ('current_category', models.BooleanField(default=False, verbose_name='Use current category')),
                ('slideshow', models.BooleanField(default=False, verbose_name='Slideshow')),
            ],
        ),
        migrations.CreateModel(
            name='LatestPortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
                ('limit', models.IntegerField(default=5, verbose_name='Limit')),
                ('current_category', models.BooleanField(default=False, verbose_name='Use current category')),
                ('slideshow', models.BooleanField(default=False, verbose_name='Slideshow')),
            ],
        ),
        migrations.CreateModel(
            name='PagesPortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecentProductsPortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RelatedProductsPortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TextPortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
                ('text', models.TextField(verbose_name='Text', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TopsellerPortlet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title', blank=True)),
                ('limit', models.IntegerField(default=5)),
            ],
        ),
    ]
