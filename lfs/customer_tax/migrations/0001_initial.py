# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lfs.criteria.base


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerTax',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rate', models.FloatField(default=0, verbose_name='Rate')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
            ],
            bases=(models.Model, lfs.criteria.base.Criteria),
        ),
    ]
