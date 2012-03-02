# python imports
from copy import deepcopy

# django imports
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.core.settings as lfs_settings
from lfs.voucher.models import Voucher

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
            print "Your database has been migrated to version 0.7."
        elif version == "0.6":
            self.migrate_to_07(application, version)
            print "Your database has been migrated to version 0.7."
        elif version == "0.7":
            print "You are up-to-date"

    def migrate_to_07(self, application, version):
        from lfs.catalog.models import Product
        from lfs.catalog.settings import VARIANT
        from lfs.core.utils import get_default_shop
        from lfs.customer.models import Address
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
