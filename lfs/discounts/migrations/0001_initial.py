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
            name='Discount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('value', models.FloatField(verbose_name='Value')),
                ('type', models.PositiveSmallIntegerField(default=0, verbose_name='Type', choices=[(0, 'Absolute'), (1, 'Percentage')])),
                ('sku', models.CharField(max_length=50, verbose_name='SKU', blank=True)),
                ('products', models.ManyToManyField(related_name='discounts', verbose_name='Products', to='catalog.Product')),
                ('tax', models.ForeignKey(verbose_name='Tax', blank=True, to='tax.Tax', null=True)),
            ],
            bases=(models.Model, lfs.criteria.base.Criteria),
        ),
    ]
