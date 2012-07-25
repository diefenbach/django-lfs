# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.db import connection
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from lfs.addresses.models import Address
from lfs.catalog.models import DeliveryTime
from lfs.criteria.models import CartPriceCriterion
from lfs.criteria.models import CombinedLengthAndGirthCriterion
from lfs.criteria.models import CountryCriterion
from lfs.criteria.models import HeightCriterion
from lfs.criteria.models import LengthCriterion
from lfs.criteria.models import WidthCriterion
from lfs.criteria.models import WeightCriterion
from lfs.criteria.models import ShippingMethodCriterion
from lfs.criteria.models import PaymentMethodCriterion
from lfs.customer.models import Customer
from lfs.order.models import Order
from django.db import transaction


class Migration(SchemaMigration):
    no_dry_run = True
    def forwards(self, orm):
        cursor1 = connection.cursor()
        cursor2 = connection.cursor()
        cursor3 = connection.cursor()
        cursor4 = connection.cursor()
        
        db.add_column("criteria_cartpricecriterion", "criterion_ptr_id", models.IntegerField(null=True))
        db.add_column("criteria_combinedlengthandgirthcriterion", "criterion_ptr_id", models.IntegerField(null=True))
        db.add_column("criteria_heightcriterion", "criterion_ptr_id", models.IntegerField(null=True))
        db.add_column("criteria_lengthcriterion", "criterion_ptr_id", models.IntegerField(null=True))
        db.add_column("criteria_widthcriterion", "criterion_ptr_id", models.IntegerField(null=True))
        db.add_column("criteria_weightcriterion", "criterion_ptr_id", models.IntegerField(null=True))
        db.add_column("criteria_countrycriterion", "criterion_ptr_id", models.IntegerField(null=True))
        db.add_column("criteria_shippingmethodcriterion", "criterion_ptr_id", models.IntegerField(null=True))
        db.add_column("criteria_paymentmethodcriterion", "criterion_ptr_id", models.IntegerField(null=True))
        
        # CartPriceCriterion
        db.add_column("criteria_cartpricecriterion", "value", models.FloatField(default=0.0))
        db.alter_column('criteria_cartpricecriterion', 'price', models.FloatField(default=0.0))
        
        cursor1.execute("""SELECT id FROM criteria_cartpricecriterion""")
        old_criteria = ", ".join([str(row[0]) for row in cursor1.fetchall()])
        
        content_type = ContentType.objects.get_for_model(CartPriceCriterion)
        cursor2.execute("""SELECT id, operator, price FROM criteria_cartpricecriterion""")
        for row in cursor2.fetchall():
            cursor3.execute("""Select content_type_id, content_id, position FROM criteria_criteriaobjects WHERE criterion_type_id=%s and criterion_id=%s""" % (content_type.id, row[0]))
            criterion_object = cursor3.fetchone()
            CartPriceCriterion.objects.create(operator=row[1], value=row[2], content_type_id=criterion_object[0], content_id=criterion_object[1], position=criterion_object[2])
        if old_criteria:
            cursor1.execute("""DELETE FROM criteria_cartpricecriterion WHERE id in (%s)""" % old_criteria)
        transaction.commit_unless_managed()
        
        db.delete_column("criteria_cartpricecriterion", "price")
        
        # CombinedLengthAndGirthCriterion
        db.add_column("criteria_combinedlengthandgirthcriterion", "value", models.FloatField(default=0.0))
        db.alter_column('criteria_combinedlengthandgirthcriterion', 'clag', models.FloatField(default=0.0))
        
        cursor1.execute("""SELECT id FROM criteria_combinedlengthandgirthcriterion""")
        old_criteria = ", ".join([str(row[0]) for row in cursor1.fetchall()])
        
        content_type = ContentType.objects.get_for_model(CombinedLengthAndGirthCriterion)
        cursor2.execute("""SELECT id, operator, clag FROM criteria_combinedlengthandgirthcriterion""")
        for row in cursor2.fetchall():
            cursor3.execute("""Select content_type_id, content_id, position FROM criteria_criteriaobjects WHERE criterion_type_id=%s and criterion_id=%s""" % (content_type.id, row[0]))
            criterion_object = cursor3.fetchone()
            CombinedLengthAndGirthCriterion.objects.create(operator=row[1], value=row[2], content_type_id=criterion_object[0], content_id=criterion_object[1], position=criterion_object[2])
        if old_criteria:
            cursor1.execute("""DELETE FROM criteria_combinedlengthandgirthcriterion WHERE id in (%s)""" % old_criteria)
        transaction.commit_unless_managed()
        
        # HeightCriterion
        db.add_column("criteria_heightcriterion", "value", models.FloatField(default=0.0))
        db.alter_column('criteria_heightcriterion', 'height', models.FloatField(default=0.0))
        
        cursor1.execute("""SELECT id FROM criteria_heightcriterion""")
        old_criteria = ", ".join([str(row[0]) for row in cursor1.fetchall()])
        
        content_type = ContentType.objects.get_for_model(HeightCriterion)
        cursor2.execute("""SELECT id, operator, height FROM criteria_heightcriterion""")
        for row in cursor2.fetchall():
            cursor3.execute("""Select content_type_id, content_id, position FROM criteria_criteriaobjects WHERE criterion_type_id=%s and criterion_id=%s""" % (content_type.id, row[0]))
            criterion_object = cursor3.fetchone()
            HeightCriterion.objects.create(operator=row[1], value=row[2], content_type_id=criterion_object[0], content_id=criterion_object[1], position=criterion_object[2])
        
        if old_criteria:
            cursor1.execute("""DELETE FROM criteria_heightcriterion WHERE id in (%s)""" % old_criteria)
        transaction.commit_unless_managed()
        db.delete_column("criteria_heightcriterion", "height")
        
        # LengthCriterion
        db.add_column("criteria_lengthcriterion", "value", models.FloatField(default=0.0))
        db.alter_column('criteria_lengthcriterion', 'length', models.FloatField(default=0.0))
        
        cursor1.execute("""SELECT id FROM criteria_lengthcriterion""")
        old_criteria = ", ".join([str(row[0]) for row in cursor1.fetchall()])
        
        content_type = ContentType.objects.get_for_model(LengthCriterion)
        cursor2.execute("""SELECT id, operator, length FROM criteria_lengthcriterion""")
        for row in cursor2.fetchall():
            cursor3.execute("""Select content_type_id, content_id, position FROM criteria_criteriaobjects WHERE criterion_type_id=%s and criterion_id=%s""" % (content_type.id, row[0]))
            criterion_object = cursor3.fetchone()
            LengthCriterion.objects.create(operator=row[1], value=row[2], content_type_id=criterion_object[0], content_id=criterion_object[1], position=criterion_object[2])
        
        if old_criteria:
            cursor1.execute("""DELETE FROM criteria_lengthcriterion WHERE id in (%s)""" % old_criteria)
        transaction.commit_unless_managed()
        
        db.delete_column("criteria_lengthcriterion", "length")
        
        # WidthCriterion
        db.add_column("criteria_widthcriterion", "value", models.FloatField(default=0.0))
        db.alter_column('criteria_widthcriterion', 'width', models.FloatField(default=0.0))
        
        cursor1.execute("""SELECT id FROM criteria_widthcriterion""")
        old_criteria = ", ".join([str(row[0]) for row in cursor1.fetchall()])
        
        content_type = ContentType.objects.get_for_model(WidthCriterion)
        cursor2.execute("""SELECT id, operator, width FROM criteria_widthcriterion""")
        for row in cursor2.fetchall():
            cursor3.execute("""Select content_type_id, content_id, position FROM criteria_criteriaobjects WHERE criterion_type_id=%s and criterion_id=%s""" % (content_type.id, row[0]))
            criterion_object = cursor3.fetchone()
            WidthCriterion.objects.create(operator=row[1], value=row[2], content_type_id=criterion_object[0], content_id=criterion_object[1], position=criterion_object[2])
        
        if old_criteria:
            cursor1.execute("""DELETE FROM criteria_widthcriterion WHERE id in (%s)""" % old_criteria)
        transaction.commit_unless_managed()
        
        db.delete_column("criteria_widthcriterion", "width")
        
        # WeightCriterion
        db.add_column("criteria_weightcriterion", "value", models.FloatField(default=0.0))
        db.alter_column('criteria_weightcriterion', 'weight', models.FloatField(default=0.0))
        
        cursor1.execute("""SELECT id FROM criteria_weightcriterion""")
        old_criteria = ", ".join([str(row[0]) for row in cursor1.fetchall()])
        
        content_type = ContentType.objects.get_for_model(WeightCriterion)
        cursor2.execute("""SELECT id, operator, weight FROM criteria_weightcriterion""")
        for row in cursor2.fetchall():
            cursor3.execute("""Select content_type_id, content_id, position FROM criteria_criteriaobjects WHERE criterion_type_id=%s and criterion_id=%s""" % (content_type.id, row[0]))
            criterion_object = cursor3.fetchone()
            WeightCriterion.objects.create(operator=row[1], value=row[2], content_type_id=criterion_object[0], content_id=criterion_object[1], position=criterion_object[2])
        
        if old_criteria:
            cursor1.execute("""DELETE FROM criteria_weightcriterion WHERE id in (%s)""" % old_criteria)
        transaction.commit_unless_managed()
        
        db.delete_column("criteria_weightcriterion", "weight")
        
        # CountryCriterion
        from lfs.core.models import Country
        db.create_table('criteria_countrycriterion_value', (
            ('id', models.AutoField(primary_key=True)),
            ('countrycriterion', models.ForeignKey(CountryCriterion)),
            ('country', models.ForeignKey(Country)),
        ))
        
        cursor1.execute("""SELECT id FROM criteria_countrycriterion""")
        old_criteria = ", ".join([str(row[0]) for row in cursor1.fetchall()])
        
        content_type = ContentType.objects.get_for_model(CountryCriterion)
        cursor2.execute("""SELECT id, operator FROM criteria_countrycriterion""")
        for row in cursor2.fetchall():
            cursor3.execute("""Select content_type_id, content_id, position FROM criteria_criteriaobjects WHERE criterion_type_id=%s and criterion_id=%s""" % (content_type.id, row[0]))
            criterion_object = cursor3.fetchone()
            cc = CountryCriterion.objects.create(operator=row[1], content_type_id=criterion_object[0], content_id=criterion_object[1], position=criterion_object[2])
        
            cursor4.execute("""Select country_id FROM criteria_countrycriterion_countries WHERE id=%s""" %  row[0])
            for row_2 in cursor4.fetchall():
                cc.value.add(row_2[0])
        
        if old_criteria:
            cursor1.execute("""DELETE FROM criteria_countrycriterion WHERE id in (%s)""" % old_criteria)
        transaction.commit_unless_managed()
        
        db.delete_table("criteria_countrycriterion_countries")
        
        # PaymentMethodCriterion
        from lfs.payment.models import PaymentMethod
        db.create_table('criteria_paymentmethodcriterion_value', (
            ('id', models.AutoField(primary_key=True)),
            ('paymentmethodcriterion', models.ForeignKey(PaymentMethodCriterion)),
            ('paymentmethod', models.ForeignKey(PaymentMethod)),
        ))
        
        cursor1.execute("""SELECT id FROM criteria_paymentmethodcriterion""")
        old_criteria = ", ".join([str(row[0]) for row in cursor1.fetchall()])
        
        content_type = ContentType.objects.get_for_model(PaymentMethodCriterion)
        cursor2.execute("""SELECT id, operator FROM criteria_paymentmethodcriterion""")
        for row in cursor2.fetchall():
            cursor3.execute("""Select content_type_id, content_id, position FROM criteria_criteriaobjects WHERE criterion_type_id=%s and criterion_id=%s""" % (content_type.id, row[0]))
            criterion_object = cursor3.fetchone()
            pmc = PaymentMethodCriterion.objects.create(operator=row[1], content_type_id=criterion_object[0], content_id=criterion_object[1], position=criterion_object[2])
        
            cursor4.execute("""Select paymentmethod_id FROM criteria_paymentmethodcriterion_payment_methods WHERE id=%s""" %  row[0])
            for row_2 in cursor4.fetchall():
                pmc.value.add(row_2[0])
        
        if old_criteria:
            cursor1.execute("""DELETE FROM criteria_paymentmethodcriterion WHERE id in (%s)""" % old_criteria)
        transaction.commit_unless_managed()
        
        db.delete_table("criteria_paymentmethodcriterion_payment_methods")
        
        # ShippingMethodCriterion
        from lfs.shipping.models import ShippingMethod
        db.create_table('criteria_shippingmethodcriterion_value', (
            ('id', models.AutoField(primary_key=True)),
            ('shippingmethodcriterion', models.ForeignKey(PaymentMethodCriterion)),
            ('shippingmethod', models.ForeignKey(ShippingMethod)),
        ))
        
        old_criteria = ", ".join([str(row[0]) for row in cursor1.fetchall()])
        
        content_type = ContentType.objects.get_for_model(ShippingMethodCriterion)
        cursor2.execute("""SELECT id, operator FROM criteria_shippingmethodcriterion""")
        for row in cursor2.fetchall():
            cursor3.execute("""Select content_type_id, content_id, position FROM criteria_criteriaobjects WHERE criterion_type_id=%s and criterion_id=%s""" % (content_type.id, row[0]))
            criterion_object = cursor3.fetchone()
            smc = ShippingMethodCriterion.objects.create(operator=row[1], content_type_id=criterion_object[0], content_id=criterion_object[1], position=criterion_object[2])
        
            cursor4.execute("""Select shippingmethod_id FROM criteria_shippingmethodcriterion_shipping_methods WHERE id=%s""" %  row[0])
            for row_2 in cursor4.fetchall():
                smc.value.add(row_2[0])
        
        if old_criteria:
            cursor1.execute("""DELETE FROM criteria_shippingmethodcriterion WHERE id in (%s)""" % old_criteria)
        transaction.commit_unless_managed()
        
        db.delete_table("criteria_shippingmethodcriterion_shipping_methods")
    
    def backwards(self, orm):
        raise NotImplementedError("Backward migration is not supported.")
