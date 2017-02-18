# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

import lfs.core.fields.thumbs


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='image',
            field=lfs.core.fields.thumbs.ImageWithThumbsField(upload_to=b'images', null=True, verbose_name='Image', sizes=((60, 60), (100, 100), (200, 200), (400, 400)), blank=True),
        ),
    ]
