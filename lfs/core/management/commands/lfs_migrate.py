# python imports
from copy import deepcopy

# django imports
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from django.db import transaction
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

# lfs imports
import lfs.core.settings as lfs_settings
from lfs.voucher.models import Voucher
from lfs.manufacturer.models import Manufacturer
from lfs.core.fields.thumbs import ImageWithThumbsField

# south imports
from south.db import db


class Command(BaseCommand):
    args = ''
    help = 'Migrations for LFS'

    def handle(self, *args, **options):
        """
        """
        from lfs.core.models import Application
        try:
            application = Application.objects.get(pk=1)
        except Application.DoesNotExist:
            application = Application.objects.create(version="0.5")

        version = application.version
        print "Detected version: %s" % version

        if version == "0.5":
            self.migrate_to_06(application, version)
            self.migrate_to_07(application, version)
            self.migrate_to_08(application, version)
            print "Your database has been migrated to version 0.8."
        elif version == "0.6":
            self.migrate_to_07(application, version)
            self.migrate_to_08(application, version)
            print "Your database has been migrated to version 0.8."
        elif version == "0.7":
            self.migrate_to_08(application, version)
            print "Your database has been migrated to version 0.8."
        elif version == "0.8":
            print "You are up-to-date"

    def migrate_to_08(self, application, version):
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

        # Addresses
        db.add_column("customer_customer", "sa_content_type", models.ForeignKey(ContentType, related_name="sa_content_type", blank=True, null=True))
        db.add_column("customer_customer", "sa_object_id", models.PositiveIntegerField(default=0))

        db.add_column("customer_customer", "ia_content_type", models.ForeignKey(ContentType, related_name="ia_content_type", blank=True, null=True))
        db.add_column("customer_customer", "ia_object_id", models.PositiveIntegerField(default=0))

        db.add_column("order_order", "sa_content_type", models.ForeignKey(ContentType, related_name="sa_content_type", blank=True, null=True))
        db.add_column("order_order", "sa_object_id", models.PositiveIntegerField(default=0))

        db.add_column("order_order", "ia_content_type", models.ForeignKey(ContentType, related_name="ia_content_type", blank=True, null=True))
        db.add_column("order_order", "ia_object_id", models.PositiveIntegerField(default=0))

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customer_address")
        for address in dictfetchall(cursor):
            try:
                # 1st try to get customer by the stored customer_id in addresses
                customer = Customer.objects.get(pk=address["customer_id"])
            except Customer.DoesNotExist:
                # If there is no customer_id we try the other way around.
                customer_cursor = connection.cursor()
                customer_cursor.execute("SELECT id from customer_customer WHERE selected_invoice_address_id=%s or selected_shipping_address_id=%s" % (address["id"], address["id"]))
                try:
                    customer_id = customer_cursor.fetchone()[0]
                except TypeError:
                    continue
                else:
                    customer = Customer.objects.get(pk=customer_id)

            # Create new address out of old
            new_address = Address.objects.create(
                pk=address["id"],
                customer= customer,
                firstname = address["firstname"],
                lastname = address["lastname"],
                company_name = address["company_name"],
                line1 = address["line1"],
                line2 = address["line2"],
                zip_code = address["zip_code"],
                city = address["city"],
                state = address["state"],
                country_id = address["country_id"],
                phone = address["phone"],
                email = address["email"],
            )

            # Get current selected shipping and invoice address (these aren't
            # available through ORM)
            customer_cursor = connection.cursor()
            customer_cursor.execute("SELECT selected_invoice_address_id, selected_shipping_address_id from customer_customer WHERE id=%s" % customer.id)
            cur_ia, cur_sa = customer_cursor.fetchone()

            # Assign the new address to the customer
            if cur_ia == address["id"]:
                customer.selected_invoice_address = new_address
            elif cur_sa == address["id"]:
                customer.selected_shipping_address = new_address
            customer.save()

        # Migrate addresses of orders
        cursor.execute("SELECT * FROM order_order")
        for order in dictfetchall(cursor):

            if order["user_id"]:
                try:
                    customer = Customer.objects.get(user=order["user_id"])
                except Customer.DoesNotExist:
                    continue
            else:
                customer = None

            invoice_address = Address.objects.create(
                order_id = order["id"],
                customer = customer,
                firstname = order["invoice_firstname"],
                lastname = order["invoice_lastname"],
                company_name = order["invoice_company_name"],
                line1 = order["invoice_line1"],
                line2 = order["invoice_line2"],
                zip_code = order["invoice_code"],
                city = order["invoice_city"],
                state = order["invoice_state"],
                country_id = order["invoice_country_id"],
                phone = order["invoice_phone"],
                email = order["customer_email"],
            )

            shipping_address = Address.objects.create(
                order_id = order["id"],
                customer = customer,
                firstname = order["shipping_firstname"],
                lastname = order["shipping_lastname"],
                company_name = order["shipping_company_name"],
                line1 = order["shipping_line1"],
                line2 = order["shipping_line2"],
                zip_code = order["shipping_code"],
                city = order["shipping_city"],
                state = order["shipping_state"],
                country_id = order["shipping_country_id"],
                phone = order["shipping_phone"],
                email = order["customer_email"],
            )

            order_instance = Order.objects.get(pk=order["id"])
            order_instance.invoice_address = invoice_address
            order_instance.shipping_address = shipping_address
            order_instance.save()

        fields = [
            "invoice_firstname",
            "invoice_lastname",
            "invoice_company_name",
            "invoice_line1",
            "invoice_line2",
            "invoice_city",
            "invoice_state",
            "invoice_code",
            "invoice_country",
            "invoice_phone",
            "shipping_firstname",
            "shipping_lastname",
            "shipping_company_name",
            "shipping_line1",
            "shipping_line2",
            "shipping_city",
            "shipping_state",
            "shipping_code",
            "shipping_country",
            "shipping_phone",
        ]

        for field in fields:
            db.delete_column("order_order", field)

        # Delete locale from shop
        db.delete_column("core_shop", "default_locale")

        # Migrate Criteria #####################################################

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

        cursor1.execute("""DELETE FROM criteria_shippingmethodcriterion WHERE id in (%s)""" % old_criteria)
        transaction.commit_unless_managed()

        db.delete_table("criteria_shippingmethodcriterion_shipping_methods")

        # Manufacturers
        # Adding field 'Manufacturer.position'
        db.add_column('manufacturer_manufacturer', 'position', models.IntegerField(default=1000), keep_default=False)

        # Adding field 'Manufacturer.short_description'
        db.add_column('manufacturer_manufacturer', 'short_description', models.TextField(default='', blank=True), keep_default=False)

        # Adding field 'Manufacturer.description'
        db.add_column('manufacturer_manufacturer', 'description', models.TextField(default='', blank=True), keep_default=False)

        # Adding field 'Manufacturer.image'
        db.add_column('manufacturer_manufacturer', 'image', ImageWithThumbsField(blank=True, max_length=100, null=True, sizes=((60, 60), (100, 100), (200, 200), (400, 400))), keep_default=False)

        # Adding field 'Manufacturer.meta_title'
        db.add_column('manufacturer_manufacturer', 'meta_title', models.CharField(default='<name>', max_length=100), keep_default=False)

        # Adding field 'Manufacturer.meta_keywords'
        db.add_column('manufacturer_manufacturer', 'meta_keywords', models.TextField(default='', blank=True), keep_default=False)

        # Adding field 'Manufacturer.meta_description'
        db.add_column('manufacturer_manufacturer', 'meta_description', models.TextField(default='', blank=True), keep_default=False)

        # Adding field 'Manufacturer.slug'
        db.add_column('manufacturer_manufacturer', 'slug', models.SlugField(default='', max_length=50, db_index=True, null=True), keep_default=False)

        # Adding field 'Manufacturer.active_formats'
        db.add_column('manufacturer_manufacturer', 'active_formats', models.fields.BooleanField(default=False), keep_default=False)

        # Adding field 'Manufacturer.product_rows'
        db.add_column('manufacturer_manufacturer', 'product_rows', models.fields.IntegerField(default=3), keep_default=False)

        # Adding field 'Manufacturer.product_cols'
        db.add_column('manufacturer_manufacturer', 'product_cols', models.fields.IntegerField(default=3), keep_default=False)

        for i, manufacturer in enumerate(Manufacturer.objects.all()):
            manufacturer.slug = slugify(manufacturer.name)
            manufacturer.position = (i + 1) * 10
            manufacturer.save()

        # Set field 'Manufacturer.slug' to not null
        db.alter_column('manufacturer_manufacturer', 'slug', models.SlugField(unique=True, max_length=50))

        # Delivery Time
        db.add_column('core_shop', 'delivery_time', models.ForeignKey(DeliveryTime, verbose_name=_(u"Delivery time"), blank=True, null=True))

        # PayPal
        paypal = PaymentMethod.objects.get(pk=3)
        paypal.module = "lfs_paypal.PayPalProcessor"
        paypal.save()

        # Adding model 'LatestPortlet'
        db.create_table('portlet_latestportlet', (
            ('id', models.fields.AutoField(primary_key=True)),
            ('title', models.fields.CharField(max_length=100, blank=True)),
            ('limit', models.fields.IntegerField(default=5)),
            ('current_category', models.fields.BooleanField(default=False)),
            ('slideshow', models.fields.BooleanField(default=False)),
        ))

        application.version = "0.8"
        application.save()

    def migrate_to_07(self, application, version):
        from lfs.catalog.models import Product
        from lfs.catalog.settings import VARIANT
        from lfs.core.utils import get_default_shop
        from lfs.addresses.models import Address
        from lfs.page.models import Page
        from lfs.shipping.models import ShippingMethod
        from lfs_order_numbers.models import OrderNumberGenerator

        # Product
        from lfs.catalog.settings import QUANTITY_FIELD_INTEGER
        from lfs.catalog.settings import QUANTITY_FIELD_TYPES

        db.add_column("catalog_product", "type_of_quantity_field", models.PositiveSmallIntegerField(_(u"Type of quantity field"), null=True, blank=True, choices=QUANTITY_FIELD_TYPES))
        db.add_column("catalog_product", "category_variant", models.SmallIntegerField(_(u"Category variant"), blank=True, null=True))
        db.add_column("catalog_product", "active_base_price", models.PositiveSmallIntegerField(_(u"Active base price"), default=0))
        db.add_column("catalog_product", "base_price_unit", models.CharField(_(u"Base price unit"), blank=True, null=True, max_length=30, choices=settings.LFS_BASE_PRICE_UNITS))
        db.add_column("catalog_product", "base_price_amount", models.FloatField(_(u"Base price amount"), default=0.0, blank=True, null=True))

        if db.backend_name == "postgres":
            db.execute('ALTER TABLE catalog_product ALTER active_packing_unit TYPE smallint USING CASE WHEN active_packing_unit=FALSE THEN 0 ELSE 1 END;')
        else:
            db.alter_column('catalog_product', 'active_packing_unit', models.PositiveSmallIntegerField(_(u"Active packing"), default=0))
            for product in Product.objects.all():
                if product.active_packing_unit != 0:
                    product.active_packing_unit = 1
                    product.save()

        # Pages
        print "Migrating to 0.7"
        db.add_column("page_page", "meta_title", models.CharField(_(u"Meta title"), blank=True, default="<title>", max_length=80))
        db.add_column("page_page", "meta_keywords", models.TextField(_(u"Meta keywords"), null=True, blank=True))
        db.add_column("page_page", "meta_description", models.TextField(_(u"Meta description"), null=True, blank=True))
        for page in Page.objects.all():
            page.meta_title = "<title>"
            page.meta_keywords = ""
            page.meta_description = ""
            page.save()

        # Copy the old page with id=1 and create a new one with id=1, which
        # will act as the root of all pages.
        try:
            page = Page.objects.get(pk=1)
        except Page.DoesNotExist:
            pass
        else:
            new_page = deepcopy(page)
            new_page.id = None
            new_page.save()
            page.delete()

        Page.objects.create(id=1, title="Root", slug="", active=1, exclude_from_navigation=1)

        # Shop
        db.add_column("core_shop", "meta_title", models.CharField(_(u"Meta title"), blank=True, default="<name>", max_length=80))
        db.add_column("core_shop", "meta_keywords", models.TextField(_(u"Meta keywords"), null=True, blank=True))
        db.add_column("core_shop", "meta_description", models.TextField(_(u"Meta description"), null=True, blank=True))

        shop = get_default_shop()
        shop.meta_keywords = ""
        shop.meta_description = ""
        shop.save()

        # Order
        db.add_column("order_order", "number", models.CharField(max_length=30, unique=True, null=True))
        OrderNumberGenerator.objects.create(pk="1", last=0)

        # Add new lines
        db.add_column("order_order", "invoice_company_name", models.CharField(null=True, blank=True, max_length=100))
        db.add_column("order_order", "shipping_company_name", models.CharField(null=True, blank=True, max_length=100))

        # Shipping Method
        db.add_column("shipping_shippingmethod", "price_calculator", models.CharField(max_length=200, choices=settings.LFS_SHIPPING_METHOD_PRICE_CALCULATORS, default=settings.LFS_SHIPPING_METHOD_PRICE_CALCULATORS[0][0]))
        for shipping_method in ShippingMethod.objects.all():
            shipping_method.price_calculator = settings.LFS_SHIPPING_METHOD_PRICE_CALCULATORS[0][0]
            shipping_method.save()

        # Static Block
        db.add_column("catalog_staticblock", "position", models.PositiveSmallIntegerField(_(u"Position"), default=999))

        # Addresses
        db.add_column("customer_address", "line1", models.CharField(_("Line 1"), max_length=100, blank=True, null=True))
        db.add_column("customer_address", "line2", models.CharField(_("Line 2"), max_length=100, blank=True, null=True))

        cursor = connection.cursor()
        cursor.execute("""SELECT id, street FROM customer_address""")
        for row in cursor.fetchall():
            address = Address.objects.get(pk=row[0])
            address.line1 = row[1]
            address.save()

        db.delete_column("customer_address", "street")

        application.version = "0.7"
        application.save()

    def migrate_to_06(self, application, version):
        from lfs.core.models import Shop
        print "Migrating to 0.6"

        # Vouchers ###########################################################
        db.add_column("voucher_voucher", "used_amount", models.PositiveSmallIntegerField(default=0))
        db.add_column("voucher_voucher", "last_used_date", models.DateTimeField(blank=True, null=True))
        db.add_column("voucher_voucher", "limit", models.PositiveSmallIntegerField(default=1))

        for voucher in Voucher.objects.all():
            voucher.limit = 1
            voucher.save()

        # This mus be done with execute because the old fields are not there
        # anymore (and therefore can't be accessed via attribute) after the user
        # has upgraded to the latest version.
        db.execute("update voucher_voucher set used_amount = 1 where used = 1")
        db.execute("update voucher_voucher set used_amount = 0 where used = 0")
        db.execute("update voucher_voucher set last_used_date = used_date")

        db.delete_column('voucher_voucher', 'used')
        db.delete_column('voucher_voucher', 'used_date')

        # Price calculator ###################################################
        db.add_column("catalog_product", "price_calculator", models.CharField(
            null=True, blank=True, choices=settings.LFS_PRICE_CALCULATORS, max_length=255))

        db.add_column("core_shop", "price_calculator",
            models.CharField(choices=lfs_settings.LFS_PRICE_CALCULATORS, default="lfs.gross_price.GrossPriceCalculator", max_length=255))

        # Locale and currency settings #######################################
        db.add_column("core_shop", "default_locale",
            models.CharField(_(u"Default Shop Locale"), max_length=20, default="en_US.UTF-8"))
        db.add_column("core_shop", "use_international_currency_code",
            models.BooleanField(_(u"Use international currency codes"), default=False))
        db.delete_column('core_shop', 'default_currency')

        db.add_column("catalog_product", "supplier_id", models.IntegerField(_(u"Supplier"), blank=True, null=True))

        # Invoice/Shipping countries
        try:
            shop = Shop.objects.only("id").get(pk=1)
        except Shop.DoesNotExist, e:  # No guarantee that our shop will have pk=1 in postgres
            shop = Shop.objects.only("id").all()[0]

        db.create_table("core_shop_invoice_countries", (
            ("id", models.AutoField(primary_key=True)),
            ("shop_id", models.IntegerField("shop_id")),
            ("country_id", models.IntegerField("country_id")),
        ))
        db.create_index("core_shop_invoice_countries", ("shop_id", ))
        db.create_index("core_shop_invoice_countries", ("country_id", ))
        db.create_unique("core_shop_invoice_countries", ("shop_id", "country_id"))

        db.create_table("core_shop_shipping_countries", (
            ("id", models.AutoField(primary_key=True)),
            ("shop_id", models.IntegerField("shop_id")),
            ("country_id", models.IntegerField("country_id")),
        ))
        db.create_index("core_shop_shipping_countries", ("shop_id", ))
        db.create_index("core_shop_shipping_countries", ("country_id", ))
        db.create_unique("core_shop_shipping_countries", ("shop_id", "country_id"))

        cursor = connection.cursor()
        cursor.execute("""SELECT country_id FROM core_shop_countries""")
        for row in cursor.fetchall():
            shop.invoice_countries.add(row[0])
            shop.shipping_countries.add(row[0])

        db.delete_table("core_shop_countries")

        # Orders #############################################################

        # Add new lines
        db.add_column("order_order", "invoice_line1", models.CharField(null=True, blank=True, max_length=100))
        db.add_column("order_order", "shipping_line1", models.CharField(null=True, blank=True, max_length=100))
        db.add_column("order_order", "invoice_line2", models.CharField(null=True, blank=True, max_length=100))
        db.add_column("order_order", "shipping_line2", models.CharField(null=True, blank=True, max_length=100))
        db.add_column("order_order", "invoice_code", models.CharField(null=True, blank=True, max_length=100))
        db.add_column("order_order", "shipping_code", models.CharField(null=True, blank=True, max_length=100))

        # Migrate data
        cursor.execute("""SELECT id, invoice_zip_code, shipping_zip_code, invoice_street, shipping_street FROM order_order""")
        for row in cursor.fetchall():
            order = Order.objects.get(pk=row[0])
            order.invoice_code = row[1]
            order.shipping_code = row[2]
            order.invoice_line1 = row[3]
            order.shipping_line1 = row[4]
            order.invoice_line2 = ""
            order.shipping_line2 = ""
            order.save()

        # Remove old code fields
        db.delete_column('order_order', 'invoice_zip_code')
        db.delete_column('order_order', 'shipping_zip_code')
        db.delete_column('order_order', 'invoice_street')
        db.delete_column('order_order', 'shipping_street')

        application.version = "0.6"
        application.save()

def dictfetchall(cursor):
    """
    Returns all rows from a cursor as a dict
    """
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
