# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import lfs.order.models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '__first__'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '__first__'),
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(max_length=30)),
                ('session', models.CharField(max_length=100, verbose_name='Session', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('state', models.PositiveSmallIntegerField(default=0, verbose_name='State', choices=[(0, 'Submitted'), (1, 'Paid'), (7, 'Prepared'), (2, 'Sent'), (3, 'Closed'), (4, 'Canceled'), (5, 'Payment Failed'), (6, 'Payment Flagged')])),
                ('state_modified', models.DateTimeField(auto_now_add=True, verbose_name='State modified')),
                ('price', models.FloatField(default=0.0, verbose_name='Price')),
                ('tax', models.FloatField(default=0.0, verbose_name='Tax')),
                ('customer_firstname', models.CharField(max_length=50, verbose_name='firstname')),
                ('customer_lastname', models.CharField(max_length=50, verbose_name='lastname')),
                ('customer_email', models.CharField(max_length=75, verbose_name='email')),
                ('sa_object_id', models.PositiveIntegerField()),
                ('ia_object_id', models.PositiveIntegerField()),
                ('shipping_price', models.FloatField(default=0.0, verbose_name='Shipping Price')),
                ('shipping_tax', models.FloatField(default=0.0, verbose_name='Shipping Tax')),
                ('payment_price', models.FloatField(default=0.0, verbose_name='Payment Price')),
                ('payment_tax', models.FloatField(default=0.0, verbose_name='Payment Tax')),
                ('account_number', models.CharField(max_length=30, verbose_name='Account number', blank=True)),
                ('bank_identification_code', models.CharField(max_length=30, verbose_name='Bank identication code', blank=True)),
                ('bank_name', models.CharField(max_length=100, verbose_name='Bank name', blank=True)),
                ('depositor', models.CharField(max_length=100, verbose_name='Depositor', blank=True)),
                ('voucher_number', models.CharField(max_length=100, verbose_name='Voucher number', blank=True)),
                ('voucher_price', models.FloatField(default=0.0, verbose_name='Voucher value')),
                ('voucher_tax', models.FloatField(default=0.0, verbose_name='Voucher tax')),
                ('message', models.TextField(verbose_name='Message', blank=True)),
                ('pay_link', models.TextField(verbose_name='pay_link', blank=True)),
                ('uuid', models.CharField(default=lfs.order.models.get_unique_id_str, unique=True, max_length=50, editable=False)),
                ('requested_delivery_date', models.DateTimeField(null=True, verbose_name='Delivery Date', blank=True)),
                ('ia_content_type', models.ForeignKey(related_name='order_invoice_address', to='contenttypes.ContentType')),
                ('payment_method', models.ForeignKey(verbose_name='Payment Method', blank=True, to='payment.PaymentMethod', null=True)),
                ('sa_content_type', models.ForeignKey(related_name='order_shipping_address', to='contenttypes.ContentType')),
                ('shipping_method', models.ForeignKey(verbose_name='Shipping Method', blank=True, to='shipping.ShippingMethod', null=True)),
                ('user', models.ForeignKey(verbose_name='User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='OrderDeliveryTime',
            fields=[
                ('deliverytime_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='catalog.DeliveryTime')),
                ('order', models.OneToOneField(related_name='delivery_time', verbose_name='Order', to='order.Order')),
            ],
            options={
                'verbose_name': 'Order delivery time',
                'verbose_name_plural': 'Order delivery times',
            },
            bases=('catalog.deliverytime',),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price_net', models.FloatField(default=0.0, verbose_name='Price net')),
                ('price_gross', models.FloatField(default=0.0, verbose_name='Price gross')),
                ('tax', models.FloatField(default=0.0, verbose_name='Tax')),
                ('product_amount', models.FloatField(null=True, verbose_name='Product quantity', blank=True)),
                ('product_sku', models.CharField(max_length=100, verbose_name='Product SKU', blank=True)),
                ('product_name', models.CharField(max_length=100, verbose_name='Product name', blank=True)),
                ('product_price_net', models.FloatField(default=0.0, verbose_name='Product price net')),
                ('product_price_gross', models.FloatField(default=0.0, verbose_name='Product price gross')),
                ('product_tax', models.FloatField(default=0.0, verbose_name='Product tax')),
                ('order', models.ForeignKey(related_name='items', to='order.Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='catalog.Product', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItemPropertyValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=100, verbose_name=b'Value', blank=True)),
                ('order_item', models.ForeignKey(related_name='properties', verbose_name='Order item', to='order.OrderItem')),
                ('property', models.ForeignKey(verbose_name='Property', to='catalog.Property')),
            ],
        ),
    ]
