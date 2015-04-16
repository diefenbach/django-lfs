# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('payment', '__first__'),
        ('shipping', '__first__'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Criterion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_id', models.PositiveIntegerField(verbose_name='Content id')),
                ('sub_type', models.CharField(max_length=100, verbose_name='Sub type', blank=True)),
                ('position', models.PositiveIntegerField(default=999, verbose_name='Position')),
                ('operator', models.PositiveIntegerField(null=True, verbose_name='Operator', blank=True)),
            ],
            options={
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='CartPriceCriterion',
            fields=[
                ('criterion_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='criteria.Criterion')),
                ('value', models.FloatField(default=0.0, verbose_name='Price')),
            ],
            bases=('criteria.criterion',),
        ),
        migrations.CreateModel(
            name='CombinedLengthAndGirthCriterion',
            fields=[
                ('criterion_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='criteria.Criterion')),
                ('value', models.FloatField(default=0.0, verbose_name='CLAG')),
            ],
            bases=('criteria.criterion',),
        ),
        migrations.CreateModel(
            name='CountryCriterion',
            fields=[
                ('criterion_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='criteria.Criterion')),
                ('value', models.ManyToManyField(to='core.Country', verbose_name='Countries')),
            ],
            bases=('criteria.criterion',),
        ),
        migrations.CreateModel(
            name='HeightCriterion',
            fields=[
                ('criterion_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='criteria.Criterion')),
                ('value', models.FloatField(default=0.0, verbose_name='Height')),
            ],
            bases=('criteria.criterion',),
        ),
        migrations.CreateModel(
            name='LengthCriterion',
            fields=[
                ('criterion_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='criteria.Criterion')),
                ('value', models.FloatField(default=0.0, verbose_name='Length')),
            ],
            bases=('criteria.criterion',),
        ),
        migrations.CreateModel(
            name='PaymentMethodCriterion',
            fields=[
                ('criterion_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='criteria.Criterion')),
                ('value', models.ManyToManyField(to='payment.PaymentMethod', verbose_name='Payment methods')),
            ],
            bases=('criteria.criterion',),
        ),
        migrations.CreateModel(
            name='ShippingMethodCriterion',
            fields=[
                ('criterion_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='criteria.Criterion')),
                ('value', models.ManyToManyField(to='shipping.ShippingMethod', verbose_name='Shipping methods')),
            ],
            bases=('criteria.criterion',),
        ),
        migrations.CreateModel(
            name='WeightCriterion',
            fields=[
                ('criterion_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='criteria.Criterion')),
                ('value', models.FloatField(default=0.0, verbose_name='Weight')),
            ],
            bases=('criteria.criterion',),
        ),
        migrations.CreateModel(
            name='WidthCriterion',
            fields=[
                ('criterion_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='criteria.Criterion')),
                ('value', models.FloatField(default=0.0, verbose_name='Width')),
            ],
            bases=('criteria.criterion',),
        ),
        migrations.AddField(
            model_name='criterion',
            name='content_type',
            field=models.ForeignKey(related_name='content_type', verbose_name='Content type', to='contenttypes.ContentType'),
        ),
    ]
