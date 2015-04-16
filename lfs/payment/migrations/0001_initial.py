# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lfs.criteria.base


class Migration(migrations.Migration):

    dependencies = [
        ('tax', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('priority', models.IntegerField(default=0, verbose_name='Priority')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('note', models.TextField(verbose_name='note', blank=True)),
                ('image', models.ImageField(upload_to=b'images', null=True, verbose_name='Image', blank=True)),
                ('price', models.FloatField(default=0.0, verbose_name='Price')),
                ('deletable', models.BooleanField(default=True)),
                ('module', models.CharField(blank=True, max_length=100, verbose_name='Module', choices=[[b'lfs_paypal.PayPalProcessor', 'PayPal']])),
                ('type', models.PositiveSmallIntegerField(default=0, verbose_name='Type', choices=[(0, 'Plain'), (1, 'Bank'), (2, 'Credit Card')])),
                ('tax', models.ForeignKey(verbose_name='Tax', blank=True, to='tax.Tax', null=True)),
            ],
            options={
                'ordering': ('priority',),
            },
            bases=(models.Model, lfs.criteria.base.Criteria),
        ),
        migrations.CreateModel(
            name='PaymentMethodPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.FloatField(default=0.0, verbose_name='Price')),
                ('priority', models.IntegerField(default=0, verbose_name='Priority')),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('payment_method', models.ForeignKey(related_name='prices', verbose_name='Payment method', to='payment.PaymentMethod')),
            ],
            options={
                'ordering': ('priority',),
            },
            bases=(models.Model, lfs.criteria.base.Criteria),
        ),
    ]
