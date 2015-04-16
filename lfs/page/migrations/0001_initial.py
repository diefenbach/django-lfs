# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('slug', models.SlugField(unique=True, max_length=100, verbose_name='Slug')),
                ('position', models.IntegerField(default=999, verbose_name='Position')),
                ('exclude_from_navigation', models.BooleanField(default=False, verbose_name='Exclude from navigation')),
                ('short_text', models.TextField(verbose_name='Short text', blank=True)),
                ('body', models.TextField(verbose_name='Text', blank=True)),
                ('file', models.FileField(upload_to=b'files', verbose_name='File', blank=True)),
                ('meta_title', models.CharField(default=b'<title>', max_length=80, verbose_name='Meta title', blank=True)),
                ('meta_keywords', models.TextField(verbose_name='Meta keywords', blank=True)),
                ('meta_description', models.TextField(verbose_name='Meta description', blank=True)),
            ],
            options={
                'ordering': ('position',),
            },
        ),
    ]
