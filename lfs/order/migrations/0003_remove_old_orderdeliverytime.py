# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_prepare_new_orderdeliverytime'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdeliverytimeold',
            name='deliverytime_ptr',
        ),
        migrations.RemoveField(
            model_name='orderdeliverytimeold',
            name='order',
        ),
        migrations.DeleteModel(
            name='OrderDeliveryTimeOld',
        ),
    ]
