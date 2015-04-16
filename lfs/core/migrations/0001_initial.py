# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lfs.core.fields.thumbs


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('title', models.CharField(max_length=40, verbose_name='Title')),
                ('link', models.CharField(max_length=100, verbose_name='Link', blank=True)),
                ('position', models.IntegerField(default=999, verbose_name='Position')),
            ],
            options={
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='ActionGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name', blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=10, verbose_name='Version', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=2, verbose_name='Country code')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='Name')),
                ('shop_owner', models.CharField(max_length=100, verbose_name='Shop owner', blank=True)),
                ('from_email', models.EmailField(max_length=254, verbose_name='From e-mail address')),
                ('notification_emails', models.TextField(verbose_name='Notification email addresses')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('image', lfs.core.fields.thumbs.ImageWithThumbsField(upload_to=b'images', null=True, verbose_name='Image', blank=True)),
                ('product_cols', models.IntegerField(default=1, verbose_name='Product cols')),
                ('product_rows', models.IntegerField(default=10, verbose_name='Product rows')),
                ('category_cols', models.IntegerField(default=1, verbose_name='Category cols')),
                ('google_analytics_id', models.CharField(max_length=20, verbose_name='Google Analytics ID', blank=True)),
                ('ga_site_tracking', models.BooleanField(default=False, verbose_name='Google Analytics Site Tracking')),
                ('ga_ecommerce_tracking', models.BooleanField(default=False, verbose_name='Google Analytics E-Commerce Tracking')),
                ('use_international_currency_code', models.BooleanField(default=False, verbose_name='Use international currency codes')),
                ('price_calculator', models.CharField(default=b'lfs.gross_price.GrossPriceCalculator', max_length=255, verbose_name='Price calculator', choices=[[b'lfs.gross_price.GrossPriceCalculator', 'Price includes tax'], [b'lfs.net_price.NetPriceCalculator', 'Price excludes tax']])),
                ('checkout_type', models.PositiveSmallIntegerField(default=0, verbose_name='Checkout type', choices=[(0, 'Anonymous and Authenticated'), (1, 'Anonymous only'), (2, 'Authenticated only')])),
                ('confirm_toc', models.BooleanField(default=False, verbose_name='Confirm TOC')),
                ('meta_title', models.CharField(default=b'<name>', max_length=80, verbose_name='Meta title', blank=True)),
                ('meta_keywords', models.TextField(verbose_name='Meta keywords', blank=True)),
                ('meta_description', models.TextField(verbose_name='Meta description', blank=True)),
                ('default_country', models.ForeignKey(verbose_name='Default shipping country', to='core.Country')),
                ('delivery_time', models.ForeignKey(verbose_name='Delivery time', blank=True, to='catalog.DeliveryTime', null=True)),
                ('invoice_countries', models.ManyToManyField(related_name='invoice', verbose_name='Invoice countries', to='core.Country')),
                ('shipping_countries', models.ManyToManyField(related_name='shipping', verbose_name='Shipping countries', to='core.Country')),
                ('static_block', models.ForeignKey(related_name='shops', verbose_name='Static block', blank=True, to='catalog.StaticBlock', null=True)),
            ],
            options={
                'permissions': (('manage_shop', 'Manage shop'),),
            },
        ),
        migrations.AddField(
            model_name='action',
            name='group',
            field=models.ForeignKey(related_name='actions', verbose_name='Group', to='core.ActionGroup'),
        ),
        migrations.AddField(
            model_name='action',
            name='parent',
            field=models.ForeignKey(verbose_name='Parent', blank=True, to='core.Action', null=True),
        ),
    ]
