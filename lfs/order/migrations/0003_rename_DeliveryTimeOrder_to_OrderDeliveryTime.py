# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_remove_table_inheritance_from_order_delivery_time'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DeliveryTimeOrder',
            new_name='OrderDeliveryTime',
        ),
    ]
