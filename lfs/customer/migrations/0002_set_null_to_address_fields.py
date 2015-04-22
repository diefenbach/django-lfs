# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='dia_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='dsa_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='ia_content_type',
            field=models.ForeignKey(related_name='ia_content_type', to='contenttypes.ContentType', null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='ia_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='sa_content_type',
            field=models.ForeignKey(related_name='sa_content_type', to='contenttypes.ContentType', null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='sa_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
