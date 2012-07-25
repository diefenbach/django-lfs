import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    def forwards(self, orm):
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
        
    def backwards(self, orm):
        raise NotImplementedError("Backward migration is not supported.")