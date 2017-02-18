# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations


def separate_order_delivery_times(apps, schema_editor):
    OrderDeliveryTime = apps.get_model("order", "OrderDeliveryTime")
    DeliveryTimeOrder = apps.get_model("order", "DeliveryTimeOrder")

    for old_odt in OrderDeliveryTime.objects.all():
        delivery = old_odt.deliverytime_ptr
        order = old_odt.order
        DeliveryTimeOrder.objects.get_or_create(order=order,
                                                defaults=dict(min=delivery.min,
                                                              max=delivery.max,
                                                              unit=delivery.unit,
                                                              description=delivery.description))
        delivery.delete()


def concat_order_delivery_times(apps, schema_editor):
    OrderDeliveryTime = apps.get_model("order", "OrderDeliveryTime")
    DeliveryTimeOrder = apps.get_model("order", "DeliveryTimeOrder")

    for new_odt in DeliveryTimeOrder.objects.all():
        OrderDeliveryTime.objects.get_or_create(order=new_odt.order,
                                                defaults=dict(min=new_odt.min,
                                                              max=new_odt.max,
                                                              unit=new_odt.unit,
                                                              description=new_odt.description))
        new_odt.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0001_initial'),
        ('core', '0002_auto_20150428_2039'),
        ('catalog', '0002_auto_20150427_2206'),
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryTimeOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min', models.FloatField(verbose_name='Min')),
                ('max', models.FloatField(verbose_name='Max')),
                ('unit', models.PositiveSmallIntegerField(default=2, verbose_name='Unit', choices=[(1, 'hours'), (2, 'days'), (3, 'weeks'), (4, 'months')])),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('order', models.OneToOneField(related_name='delivery_time', verbose_name='Order', to='order.Order')),
            ],
            options={
                'verbose_name': 'Order delivery time',
                'verbose_name_plural': 'Order delivery times',
            },
        ),
        migrations.RunPython(separate_order_delivery_times, concat_order_delivery_times),
        migrations.RemoveField(
            model_name='orderdeliverytime',
            name='deliverytime_ptr',
        ),
        migrations.RemoveField(
            model_name='orderdeliverytime',
            name='order',
        ),
        migrations.DeleteModel(
            name='OrderDeliveryTime',
        ),
    ]
