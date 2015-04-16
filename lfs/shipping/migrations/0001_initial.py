# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lfs.criteria.base


class Migration(migrations.Migration):

    dependencies = [
        ('tax', '__first__'),
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShippingMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('priority', models.IntegerField(default=0, verbose_name='Priority')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('note', models.TextField(verbose_name='Note', blank=True)),
                ('image', models.ImageField(upload_to=b'images', null=True, verbose_name='Image', blank=True)),
                ('price', models.FloatField(default=0.0, verbose_name='Price')),
                ('price_calculator', models.CharField(default=b'lfs.shipping.GrossShippingMethodPriceCalculator', max_length=200, verbose_name='Price Calculator', choices=[[b'lfs.shipping.GrossShippingMethodPriceCalculator', 'Price includes tax'], [b'lfs.shipping.NetShippingMethodPriceCalculator', 'Price excludes tax']])),
                ('delivery_time', models.ForeignKey(verbose_name='Delivery time', blank=True, to='catalog.DeliveryTime', null=True)),
                ('tax', models.ForeignKey(verbose_name='Tax', blank=True, to='tax.Tax', null=True)),
            ],
            options={
                'ordering': ('priority',),
            },
            bases=(models.Model, lfs.criteria.base.Criteria),
        ),
        migrations.CreateModel(
            name='ShippingMethodPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.FloatField(default=0.0, verbose_name='Price')),
                ('priority', models.IntegerField(default=0, verbose_name='Priority')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('shipping_method', models.ForeignKey(related_name='prices', verbose_name='shipping_method', to='shipping.ShippingMethod')),
            ],
            options={
                'ordering': ('priority',),
            },
            bases=(models.Model, lfs.criteria.base.Criteria),
        ),
    ]
