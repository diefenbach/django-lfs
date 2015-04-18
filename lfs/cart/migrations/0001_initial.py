# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session', models.CharField(max_length=100, verbose_name='Session', blank=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='Modification date')),
                ('user', models.ForeignKey(verbose_name='User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.FloatField(null=True, verbose_name='Quantity', blank=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='Modification date')),
                ('cart', models.ForeignKey(verbose_name='Cart', to='cart.Cart')),
                ('product', models.ForeignKey(verbose_name='Product', to='catalog.Product')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='CartItemPropertyValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=100, verbose_name=b'Value', blank=True)),
                ('cart_item', models.ForeignKey(related_name='properties', verbose_name='Cart item', to='cart.CartItem')),
                ('property', models.ForeignKey(verbose_name='Property', to='catalog.Property')),
                ('property_group', models.ForeignKey(verbose_name='Property group', blank=True, to='catalog.PropertyGroup', null=True)),
            ],
        ),
    ]
