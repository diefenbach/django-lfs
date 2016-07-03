# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voucher', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='voucher',
            name='sums_up',
            field=models.BooleanField(default=True, help_text='Sums up with other discounts/vouchers', verbose_name='Sums up'),
        ),
    ]
