# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations
import lfs.core.fields.thumbs


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=lfs.core.fields.thumbs.ImageWithThumbsField(upload_to=b'images', null=True, verbose_name='Image', sizes=((60, 60), (100, 100), (200, 200), (300, 300), (400, 400)), blank=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=lfs.core.fields.thumbs.ImageWithThumbsField(upload_to=b'images', null=True, verbose_name='Image', sizes=((60, 60), (100, 100), (200, 200), (300, 300), (400, 400)), blank=True),
        ),
    ]
