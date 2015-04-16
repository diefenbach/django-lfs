# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '__first__'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '__first__'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account_number', models.CharField(max_length=30, verbose_name='Account number', blank=True)),
                ('bank_identification_code', models.CharField(max_length=30, verbose_name='Bank identification code', blank=True)),
                ('bank_name', models.CharField(max_length=100, verbose_name='Bank name', blank=True)),
                ('depositor', models.CharField(max_length=100, verbose_name='Depositor', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CreditCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=30, verbose_name='Type', blank=True)),
                ('owner', models.CharField(max_length=100, verbose_name='Owner', blank=True)),
                ('number', models.CharField(max_length=30, verbose_name='Number', blank=True)),
                ('expiration_date_month', models.IntegerField(null=True, verbose_name='Expiration date month', blank=True)),
                ('expiration_date_year', models.IntegerField(null=True, verbose_name='Expiration date year', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session', models.CharField(max_length=100, blank=True)),
                ('sa_object_id', models.PositiveIntegerField()),
                ('dsa_object_id', models.PositiveIntegerField()),
                ('ia_object_id', models.PositiveIntegerField()),
                ('dia_object_id', models.PositiveIntegerField()),
                ('ia_content_type', models.ForeignKey(related_name='ia_content_type', to='contenttypes.ContentType')),
                ('sa_content_type', models.ForeignKey(related_name='sa_content_type', to='contenttypes.ContentType')),
                ('selected_bank_account', models.ForeignKey(related_name='selected_bank_account', verbose_name='Bank account', blank=True, to='customer.BankAccount', null=True)),
                ('selected_country', models.ForeignKey(verbose_name='Selected country', blank=True, to='core.Country', null=True)),
                ('selected_credit_card', models.ForeignKey(related_name='selected_credit_card', verbose_name='Credit card', blank=True, to='customer.CreditCard', null=True)),
                ('selected_payment_method', models.ForeignKey(related_name='selected_payment_method', verbose_name='Selected payment method', blank=True, to='payment.PaymentMethod', null=True)),
                ('selected_shipping_method', models.ForeignKey(related_name='selected_shipping_method', verbose_name='Selected shipping method', blank=True, to='shipping.ShippingMethod', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='creditcard',
            name='customer',
            field=models.ForeignKey(related_name='credit_cards', verbose_name='Customer', blank=True, to='customer.Customer', null=True),
        ),
        migrations.AddField(
            model_name='bankaccount',
            name='customer',
            field=models.ForeignKey(related_name='bank_accounts', verbose_name='Customer', blank=True, to='customer.Customer', null=True),
        ),
    ]
