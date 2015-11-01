# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def separate_order_delivery_times(apps, schema_editor):
    OrderDeliveryTimeOld = apps.get_model("order", "OrderDeliveryTimeOld")
    OrderDeliveryTime = apps.get_model("order", "OrderDeliveryTime")

    for old_odt in OrderDeliveryTimeOld.objects.all():
        delivery = old_odt.deliverytime_ptr
        order = old_odt.order
        OrderDeliveryTime.objects.get_or_create(order=order,
                                                defaults=dict(min=delivery.min,
                                                              max=delivery.max,
                                                              unit=delivery.unit,
                                                              description=delivery.description))
        delivery.delete()


def concat_order_delivery_times(apps, schema_editor):
    OrderDeliveryTimeOld = apps.get_model("order", "OrderDeliveryTimeOld")
    OrderDeliveryTime = apps.get_model("order", "OrderDeliveryTime")

    for new_odt in OrderDeliveryTime.objects.all():
        OrderDeliveryTimeOld.objects.get_or_create(order=new_odt.order,
                                                   defaults=dict(min=new_odt.min,
                                                                 max=new_odt.max,
                                                                 unit=new_odt.unit,
                                                                 description=new_odt.description))
        new_odt.delete()


class Migration(migrations.Migration):
    """ The point of this migration (and subsequent one) is to replace existing OrderDeliveryTime model with new one
        that doesn't use table inheritance as it causes all OrderDeliveryTime objects to be shown in management
        panel Delivery Times
    """
    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel('OrderDeliveryTime', 'OrderDeliveryTimeOld'),
        migrations.CreateModel(
            name='OrderDeliveryTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min', models.FloatField(verbose_name='Min')),
                ('max', models.FloatField(verbose_name='Max')),
                ('unit', models.PositiveSmallIntegerField(default=2, verbose_name='Unit', choices=[(1, 'hours'), (2, 'days'), (3, 'weeks'), (4, 'months')])),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('order', models.OneToOneField(related_name='delivery_time', verbose_name='Order', to='order.Order')),
            ],
            options={
                'ordering': ('min',),
            },
        ),
        migrations.RunPython(separate_order_delivery_times, concat_order_delivery_times),
    ]
