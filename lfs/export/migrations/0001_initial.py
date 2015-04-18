# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('variants_option', models.PositiveSmallIntegerField(verbose_name='Variant', choices=[(0, '---'), (1, 'Default'), (2, 'Cheapest'), (3, 'All')])),
                ('category', models.ForeignKey(verbose_name='Category', to='catalog.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Export',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('variants_option', models.PositiveSmallIntegerField(default=1, verbose_name='Variants', choices=[(1, 'Default'), (2, 'Cheapest'), (3, 'All')])),
                ('position', models.IntegerField(default=1)),
                ('products', models.ManyToManyField(related_name='exports', verbose_name='Products', to='catalog.Product', blank=True)),
            ],
            options={
                'ordering': ('position', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module', models.CharField(default=b'lfs.export.generic', max_length=100)),
                ('method', models.CharField(default=b'export', max_length=100)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='script',
            unique_together=set([('module', 'method')]),
        ),
        migrations.AddField(
            model_name='export',
            name='script',
            field=models.ForeignKey(verbose_name='Script', to='export.Script'),
        ),
        migrations.AddField(
            model_name='categoryoption',
            name='export',
            field=models.ForeignKey(verbose_name='Export', to='export.Export'),
        ),
    ]
