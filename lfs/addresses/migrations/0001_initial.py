# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '__first__'),
        ('customer', '__first__'),
        ('core', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('firstname', models.CharField(max_length=50, verbose_name='Firstname')),
                ('lastname', models.CharField(max_length=50, verbose_name='Lastname')),
                ('line1', models.CharField(max_length=100, null=True, verbose_name='Line 1', blank=True)),
                ('line2', models.CharField(max_length=100, null=True, verbose_name='Line 2', blank=True)),
                ('zip_code', models.CharField(default='', max_length=10, verbose_name='Zip code')),
                ('city', models.CharField(max_length=50, verbose_name='City')),
                ('state', models.CharField(max_length=50, null=True, verbose_name='State', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='addresses.BaseAddress')),
                ('company_name', models.CharField(max_length=50, null=True, verbose_name='Company name', blank=True)),
                ('phone', models.CharField(max_length=20, null=True, verbose_name='Phone', blank=True)),
                ('email', models.EmailField(max_length=254, null=True, verbose_name='E-Mail', blank=True)),
            ],
            bases=('addresses.baseaddress',),
        ),
        migrations.AddField(
            model_name='baseaddress',
            name='country',
            field=models.ForeignKey(verbose_name='Country', blank=True, to='core.Country', null=True),
        ),
        migrations.AddField(
            model_name='baseaddress',
            name='customer',
            field=models.ForeignKey(related_name='addresses', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Customer', blank=True, to='customer.Customer', null=True),
        ),
        migrations.AddField(
            model_name='baseaddress',
            name='order',
            field=models.ForeignKey(related_name='addresses', verbose_name='Order', blank=True, to='order.Order', null=True),
        ),
    ]
