# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '__first__'),
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeaturedProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveSmallIntegerField(default=1, verbose_name='Position')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('product', models.ForeignKey(verbose_name='Product', to='catalog.Product')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='OrderRatingMail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('send_date', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(verbose_name='Order', to='order.Order')),
            ],
        ),
        migrations.CreateModel(
            name='ProductSales',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sales', models.IntegerField(default=0, verbose_name='sales')),
                ('product', models.ForeignKey(verbose_name='Product', to='catalog.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Topseller',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveSmallIntegerField(default=1, verbose_name='Position')),
                ('product', models.ForeignKey(verbose_name='Product', to='catalog.Product')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
    ]
