# django imports
from django.contrib.sessions.backends.file import SessionStore
from django.core.urlresolvers import reverse
from django.test import TestCase

# lfs imports
import lfs.catalog.utils
import lfs.core.settings as lfs_settings
from lfs.core.signals import property_type_changed
from lfs.catalog.settings import ACTIVE_FOR_SALE_YES
from lfs.catalog.settings import ACTIVE_FOR_SALE_STANDARD
from lfs.catalog.settings import ACTIVE_FOR_SALE_NO
from lfs.catalog.settings import CONTENT_CATEGORIES
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS, VARIANT
from lfs.catalog.settings import DELIVERY_TIME_UNIT_HOURS
from lfs.catalog.settings import DELIVERY_TIME_UNIT_WEEKS
from lfs.catalog.settings import DELIVERY_TIME_UNIT_DAYS
from lfs.catalog.settings import DELIVERY_TIME_UNIT_MONTHS
from lfs.catalog.settings import PROPERTY_NUMBER_FIELD
from lfs.catalog.settings import PROPERTY_SELECT_FIELD
from lfs.catalog.settings import PROPERTY_TEXT_FIELD
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_FILTER
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_VARIANT
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.catalog.settings import LIST

from lfs.catalog.models import Category
from lfs.catalog.models import DeliveryTime
from lfs.catalog.models import GroupsPropertiesRelation
from lfs.catalog.models import Image
from lfs.catalog.models import Product
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyGroup
from lfs.catalog.models import PropertyOption
from lfs.catalog.models import ProductAccessories
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import ProductsPropertiesRelation
from lfs.core.signals import product_changed
from lfs.core.signals import product_removed_property_group
from lfs.tax.models import Tax
from lfs.tests.utils import RequestFactory


class NetPriceTestCase(TestCase):
    """Tests attributes and methods of Products
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        shop = lfs.core.utils.get_default_shop()
        shop.price_calculator = "lfs.net_price.NetPriceCalculator"
        shop.save()

        self.request = RequestFactory().get("/")
        self.request.session = SessionStore()

        # set up our price calculator
        self.orig_price_calculator = lfs_settings.LFS_DEFAULT_PRICE_CALCULATOR
        lfs_settings.LFS_DEFAULT_PRICE_CALCULATOR = "lfs.net_price.NetPriceCalculator"

        # Create a tax
        self.t1 = Tax.objects.create(rate=19.0)

        # A product with properties and variants
        self.p1 = Product.objects.create(
            name=u"Product 1",
            slug=u"product-1",
            sku=u"SKU P1",
            description=u"Description",
            short_description=u"Short description product 1",
            meta_description=u"Meta description product 1",
            meta_keywords=u"Meta keywords product 1",
            sub_type=PRODUCT_WITH_VARIANTS,
            tax=self.t1,
            price=1.0,
            for_sale_price=0.5,
            stock_amount=2,
            width=1.0,
            height=2.0,
            length=3.0,
            weight=4.0,
            active=True)

        # Products without properties and variants
        self.p2 = Product.objects.create(name=u"Product 2", slug=u"product-2", active=True)

        # Add a variant with color = red, size = m
        self.v1 = Product.objects.create(
            name=u"Variant 1",
            slug=u"variant-1",
            sku=u"SKU V1",
            description=u"This is the description of variant 1",
            meta_description=u"Meta description of variant 1",
            meta_keywords=u"Meta keywords variant 1",
            sub_type=VARIANT,
            price=2.0,
            for_sale_price=1.5,
            parent=self.p1,
            width=11.0,
            height=12.0,
            length=13.0,
            weight=14.0,
            active=True,
        )

    def tearDown(self):
        lfs_settings.LFS_DEFAULT_PRICE_CALCULATOR = self.orig_price_calculator

    def test_defaults(self):
        """Tests the default value after a product has been created
        """
        p = Product.objects.create(
            name="Product", slug="product", sku="4711", price=42.0)

        self.assertEqual(p.name, "Product")
        self.assertEqual(p.slug, "product")
        self.assertEqual(p.sku, "4711")
        self.assertEqual(p.price, 42.0)
        self.assertEqual(p.effective_price, 42.0)
        self.assertEqual(p.short_description, "")
        self.assertEqual(p.description, "")
        self.assertEqual(len(p.images.all()), 0)

        self.assertEqual(p.meta_title, "<name>")
        self.assertEqual(p.meta_description, "")
        self.assertEqual(p.meta_keywords, "")

        self.assertEqual(len(p.related_products.all()), 0)
        self.assertEqual(len(p.accessories.all()), 0)

        self.assertEqual(p.for_sale, False)
        self.assertEqual(p.for_sale_price, 0.0)
        self.assertEqual(p.active, False)

        self.assertEqual(p.deliverable, True)
        self.assertEqual(p.manual_delivery_time, False)
        self.assertEqual(p.delivery_time, None)
        self.assertEqual(p.order_time, None)
        self.assertEqual(p.ordered_at, None)
        self.assertEqual(p.manage_stock_amount, False)
        self.assertEqual(p.stock_amount, 0)

        self.assertEqual(p.weight, 0)
        self.assertEqual(p.height, 0)
        self.assertEqual(p.length, 0)
        self.assertEqual(p.width, 0)

        self.assertEqual(p.tax, None)
        self.assertEqual(p.sub_type, STANDARD_PRODUCT)

        self.assertEqual(p.default_variant, None)
        self.assertEqual(p.variants_display_type, LIST)

        self.assertEqual(p.parent, None)
        self.assertEqual(p.active_name, False)
        self.assertEqual(p.active_sku, False)
        self.assertEqual(p.active_short_description, False)
        self.assertEqual(p.active_description, False)
        self.assertEqual(p.active_price, False)
        self.assertEqual(p.active_images, False)
        self.assertEqual(p.active_related_products, False)
        self.assertEqual(p.active_accessories, False)
        self.assertEqual(p.active_meta_description, False)
        self.assertEqual(p.active_meta_keywords, False)

    def test_get_price(self):
        """
        """
        # Test product
        self.assertEqual(self.p1.get_price(self.request), 1.0)

        # Test variant. By default the price of a variant is inherited
        self.assertEqual(self.v1.get_price(self.request), 1.0)

        # Now we switch to active price.
        self.v1.active_price = True
        self.v1.save()

        # Now we get the price of the variant product (not it's parent)
        self.assertEqual(self.v1.get_price(self.request), 2.0)

    def test_get_price_gross(self):
        """Tests the gross price of a product and a variant. Takes active_price
        of the variant into account.
        """
        # Test product
        self.assertEqual(self.p1.get_price_gross(self.request), 1.19)

        # Test variant. By default the price_gross of a variant is inherited
        self.assertEqual(self.v1.get_price_gross(self.request), 1.19)

        # Now we switch to active price.
        self.v1.active_price = True
        self.v1.save()

        # Now we get the price gross of the parent product
        self.assertEqual(self.v1.get_price_gross(self.request), 2.38)

    def test_get_price_net(self):
        """Tests the net price of a product and a variant. Takes active_price of
        the variant into account.
        """
        # Test product
        self.assertEqual("%.2f" % self.p1.get_price_net(self.request), "1.00")

        # Test variant. By default the price_net of a variant is inherited,
        # but the tax is.
        self.assertEqual("%.2f" % self.v1.get_price_net(self.request), "1.00")

        # Now we switch to active price.
        self.v1.active_price = True
        self.v1.save()

        # Now we get the price net of the parent product
        self.assertEqual("%.2f" % self.v1.get_price_net(self.request), "2.00")

    def test_get_standard_price_1(self):
        """Test the price vs. standard price for a product.
        """
        # By default get_standard_price returns then normal price of the product
        standard_price = self.p1.get_standard_price(self.request)
        self.assertEqual(standard_price, 1.0)

        # Switch to for sale
        self.p1.for_sale = True
        self.p1.save()

        # If the product is for sale ``get_price`` returns the for sale price
        price = self.p1.get_price(self.request)
        self.assertEqual(price, 0.5)

        # But ``get_standard_price`` returns still the normal price
        standard_price = self.p1.get_standard_price(self.request)
        self.assertEqual(standard_price, 1.0)

    def test_get_standard_price_2(self):
        """Test the price vs. standard price for a variant.
        """
        #
        self.p1.for_sale = False
        self.p1.save()

        self.v1.active_price = False
        self.v1.active_for_sale_price = False
        self.v1.save()

        self.assertEqual(self.v1.get_standard_price(self.request), 1.0)
        self.assertEqual(self.v1.get_price(self.request), 1.0)
        self.assertEqual(self.v1.get_for_sale(), False)

        #
        self.p1.for_sale = False
        self.p1.save()

        self.v1.active_price = False
        self.v1.active_for_sale_price = True
        self.v1.save()

        self.assertEqual(self.v1.get_standard_price(self.request), 1.0)
        self.assertEqual(self.v1.get_price(self.request), 1.0)
        self.assertEqual(self.v1.get_for_sale(), False)

        #
        self.p1.for_sale = False
        self.p1.save()

        self.v1.active_price = True
        self.v1.active_for_sale_price = False
        self.v1.save()

        self.assertEqual(self.v1.get_standard_price(self.request), 2.0)
        self.assertEqual(self.v1.get_price(self.request), 2.0)
        self.assertEqual(self.v1.get_for_sale(), False)

        #
        self.p1.for_sale = False
        self.p1.save()

        self.v1.active_price = True
        self.v1.active_for_sale_price = True
        self.v1.save()

        self.assertEqual(self.v1.get_standard_price(self.request), 2.0)
        self.assertEqual(self.v1.get_price(self.request), 2.0)
        self.assertEqual(self.v1.get_for_sale(), False)

        #
        self.p1.for_sale = True
        self.p1.save()

        self.v1.active_price = False
        self.v1.active_for_sale_price = False
        self.v1.save()

        self.assertEqual(self.v1.get_standard_price(self.request), 1.0)
        self.assertEqual(self.v1.get_price(self.request), 0.5)
        self.assertEqual(self.v1.get_for_sale(), True)

        #
        self.p1.for_sale = True
        self.p1.save()

        self.v1.active_price = False
        self.v1.active_for_sale_price = True
        self.v1.save()

        self.assertEqual(self.v1.get_standard_price(self.request), 1.0)
        self.assertEqual(self.v1.get_price(self.request), 1.5)
        self.assertEqual(self.v1.get_for_sale(), True)

        #
        self.p1.for_sale = True
        self.p1.save()

        self.v1.active_price = True
        self.v1.active_for_sale_price = False
        self.v1.save()

        self.assertEqual(self.v1.get_standard_price(self.request), 2.0)
        self.assertEqual(self.v1.get_price(self.request), 0.5)
        self.assertEqual(self.v1.get_for_sale(), True)

        #
        self.p1.for_sale = True
        self.p1.save()

        self.v1.active_price = True
        self.v1.active_for_sale_price = True
        self.v1.save()

        self.assertEqual(self.v1.get_standard_price(self.request), 2.0)
        self.assertEqual(self.v1.get_price(self.request), 1.5)
        self.assertEqual(self.v1.get_for_sale(), True)

        #
        self.p1.for_sale = True
        self.p1.save()

        self.v1.active_for_sale = ACTIVE_FOR_SALE_STANDARD
        self.v1.save()

        self.assertEqual(self.v1.get_for_sale(), True)

        self.v1.active_for_sale = ACTIVE_FOR_SALE_YES
        self.v1.save()

        self.assertEqual(self.v1.get_for_sale(), True)

        self.v1.active_for_sale = ACTIVE_FOR_SALE_NO
        self.v1.save()

        self.assertEqual(self.v1.get_for_sale(), False)

        #
        self.p1.for_sale = False
        self.p1.save()

        self.v1.active_for_sale = ACTIVE_FOR_SALE_STANDARD
        self.v1.save()

        self.assertEqual(self.v1.get_for_sale(), False)

        self.v1.active_for_sale = ACTIVE_FOR_SALE_YES
        self.v1.save()

        self.assertEqual(self.v1.get_for_sale(), True)

        self.v1.active_for_sale = ACTIVE_FOR_SALE_NO
        self.v1.save()

        self.assertEqual(self.v1.get_for_sale(), False)

    def test_get_tax_rate(self):
        """
        """
        tax_rate = self.p1.get_tax_rate(self.request)
        self.assertEqual(tax_rate, 19.0)

        # The variant has the same tax rate as the parent product
        tax_rate = self.v1.get_tax_rate(self.request)
        self.assertEqual(tax_rate, 19.0)

        # Product 2 doesn't have an assigned tax rate, hence it should be 0.0
        tax_rate = self.p2.get_tax_rate(self.request)
        self.assertEqual(tax_rate, 0.0)

    def test_get_tax(self):
        """
        """
        tax = self.p1.get_tax(self.request)
        self.assertEqual("%.2f" % tax, "0.19")

        # The variant has the same tax rate as the parent product
        self.v1.active_price = False
        tax = self.v1.get_tax(self.request)
        self.assertEqual("%.2f" % tax, "0.19")

        # If the variant has an active price the tax has to take care of this.
        self.v1.active_price = True
        tax = self.v1.get_tax(self.request)
        self.assertEqual("%.2f" % tax, "0.38")

        # Product 2 doesn't have a assigned tax rate, hence the tax should 0.0
        tax = self.p2.get_tax(self.request)
        self.assertEqual("%.2f" % tax, "0.00")
