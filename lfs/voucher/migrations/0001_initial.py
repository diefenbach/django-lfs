# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tax', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(unique=True, max_length=100)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('effective_from', models.FloatField(default=0.0)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('kind_of', models.PositiveSmallIntegerField(choices=[(0, 'Absolute'), (1, 'Percentage')])),
                ('value', models.FloatField(default=0.0)),
                ('active', models.BooleanField(default=True)),
                ('used_amount', models.PositiveSmallIntegerField(default=0)),
                ('last_used_date', models.DateTimeField(null=True, blank=True)),
                ('limit', models.PositiveSmallIntegerField(default=1, null=True, blank=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('creation_date', 'number'),
            },
        ),
        migrations.CreateModel(
            name='VoucherGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('position', models.PositiveSmallIntegerField(default=10)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='VoucherOptions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number_prefix', models.CharField(default=b'', max_length=20, blank=True)),
                ('number_suffix', models.CharField(default=b'', max_length=20, blank=True)),
                ('number_length', models.IntegerField(default=5, null=True, blank=True)),
                ('number_letters', models.CharField(default=b'ABCDEFGHIJKLMNOPQRSTUVWXYZ', max_length=100, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='voucher',
            name='group',
            field=models.ForeignKey(related_name='vouchers', to='voucher.VoucherGroup'),
        ),
        migrations.AddField(
            model_name='voucher',
            name='tax',
            field=models.ForeignKey(verbose_name='Tax', blank=True, to='tax.Tax', null=True),
        ),
    ]
