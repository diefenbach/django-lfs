# python imports
from datetime import datetime
from datetime import timedelta

# django imports
from django.core.urlresolvers import reverse
from django.test import TestCase

# lfs import
from lfs.catalog.models import Category
from lfs.catalog.models import Product
import lfs.marketing.utils
from lfs.marketing.models import Topseller
from lfs.marketing.utils import calculate_product_sales
from lfs.order.models import Order
from lfs.order.models import OrderItem
from lfs.order.settings import CLOSED


class RatingMailTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        self.p1 = Product.objects.create(name="Product 1", slug="product-1", active=True)

        self.c1 = Category.objects.create(name="Category 1", slug="category-1")
        self.c1.save()
        self.c1.products = (self.p1, )
        self.c1.save()

        self.o = Order.objects.create(invoice_country_id=1, shipping_country_id=1)
        self.oi1 = OrderItem.objects.create(order=self.o, product_amount=1, product=self.p1)

    def test_get_orders(self):
        """
        """
        # First there is no closed order
        orders = lfs.marketing.utils.get_orders()
        self.assertEqual(len(orders), 0)

        # Close order
        self.o.state = CLOSED
        self.o.save()

        # But order is closed within the limit, so there is still no order for
        # rating mails
        orders = lfs.marketing.utils.get_orders()
        self.assertEqual(len(orders), 0)

        # Set the state modified date before the limit
        self.o.state_modified = datetime.now() - timedelta(days=15)
        self.o.save()

        # Now there is a order for which there should a rating mail be sent
        orders = lfs.marketing.utils.get_orders()
        self.assertEqual(len(orders), 1)


class TopsellerTestCase(TestCase):
    """Tests the Topseller model
    """
    def setUp(self):
        """
        """
        self.p1 = Product.objects.create(name="Product 1", slug="product-1", active=True)
        self.t1 = Topseller.objects.create(product=self.p1)

    def test_defaults(self):
        """
        """
        self.assertEqual(self.t1.position, 1)


class TopsellerUtilsTestCase(TestCase):
    """Tests the utils of the lfs.marketing
    """
    def setUp(self):
        """
        """
        self.p1 = Product.objects.create(name="Product 1", slug="product-1", active=True)
        self.p2 = Product.objects.create(name="Product 2", slug="product-2", active=True)
        self.p3 = Product.objects.create(name="Product 3", slug="product-3", active=True)
        self.p4 = Product.objects.create(name="Product 4", slug="product-4", active=True)

        self.c1 = Category.objects.create(name="Category 1", slug="category-1")
        self.c1.save()

        self.c11 = Category.objects.create(name="Category 11", slug="category-11", parent=self.c1)
        self.c11.products = (self.p1, self.p2)
        self.c11.save()

        self.c12 = Category.objects.create(name="Category 12", slug="category-12", parent=self.c1)
        self.c12.products = (self.p3, self.p4)
        self.c12.save()

        self.o = Order.objects.create(invoice_country_id=1, shipping_country_id=1)
        self.oi1 = OrderItem.objects.create(order=self.o, product_amount=1, product=self.p1)
        self.oi2 = OrderItem.objects.create(order=self.o, product_amount=2, product=self.p2)
        self.oi3 = OrderItem.objects.create(order=self.o, product_amount=3, product=self.p3)
        self.oi4 = OrderItem.objects.create(order=self.o, product_amount=4, product=self.p4)

        calculate_product_sales()

    def test_topseller_1(self):
        """Tests general topsellers.
        """
        ts = lfs.marketing.utils.get_topseller(2)

        self.assertEqual(len(ts), 2)

        self.assertEqual(ts[0], self.p4)
        self.assertEqual(ts[1], self.p3)

    def test_topseller_2(self):
        """Tests general topseller with explicitly selected products.
        """
        # Explicit topseller
        self.p5 = Product.objects.create(name="Product 5", slug="product-5", active=True)
        t5 = Topseller.objects.create(product=self.p5, position=1)

        ts = lfs.marketing.utils.get_topseller(2)
        self.assertEqual(ts[0], self.p5)
        self.assertEqual(ts[1], self.p4)

        self.p6 = Product.objects.create(name="Product 6", slug="product-6", active=True)
        t6 = Topseller.objects.create(product=self.p6, position=2)

        ts = lfs.marketing.utils.get_topseller(2)
        self.assertEqual(ts[0], self.p5)
        self.assertEqual(ts[1], self.p6)

        # Exchange positions
        t5.position = 2
        t5.save()
        t6.position = 1
        t6.save()

        ts = lfs.marketing.utils.get_topseller(2)
        self.assertEqual(ts[0], self.p6)
        self.assertEqual(ts[1], self.p5)

        # Now the position is to greater than limit, so it shouldn't be within
        # topsellers at all
        t6.position = 3
        t6.save()

        ts = lfs.marketing.utils.get_topseller(2)
        self.assertEqual(ts[0], self.p4)
        self.assertEqual(ts[1], self.p5)  # has to be on pasition 2

    def test_topseller_3(self):
        """Tests general topseller with explicitly assigned products which
        are also in calculated topsellers.
        """
        ts = lfs.marketing.utils.get_topseller(2)

        self.assertEqual(len(ts), 2)

        self.assertEqual(ts[0], self.p4)
        self.assertEqual(ts[1], self.p3)

        # Explicit topseller P4, which is already a topseller
        t = Topseller.objects.create(product=self.p4, position=1)

        # P4 should only displayed once
        ts = lfs.marketing.utils.get_topseller(2)
        self.assertEqual(ts[0], self.p4)
        self.assertEqual(ts[1], self.p3)

    def test_topseller_for_category_1(self):
        """Tests topseller for specific categories.
        """
        # Tests the top level category
        ts = lfs.marketing.utils.get_topseller_for_category(self.c1, limit=2)
        self.assertEqual(len(ts), 2)

        self.assertEqual(ts[0], self.p4)
        self.assertEqual(ts[1], self.p3)

        # Tests the direct categories
        ts = lfs.marketing.utils.get_topseller_for_category(self.c11, limit=1)
        self.assertEqual(len(ts), 1)

        self.assertEqual(ts[0], self.p2)

        ts = lfs.marketing.utils.get_topseller_for_category(self.c12, limit=1)
        self.assertEqual(len(ts), 1)

        self.assertEqual(ts[0], self.p4)

    def test_topseller_for_category_2(self):
        """Tests the top seller for specific categories. With explicitly
        selected products
        """
        # Explicit topseller for c1
        self.p5 = Product.objects.create(name="Product 5", slug="product-5", active=True)
        t5 = Topseller.objects.create(product=self.p5, position=1)

        self.c11.products = (self.p1, self.p2, self.p5)

        # Tests the top level category
        ts = lfs.marketing.utils.get_topseller_for_category(self.c1, limit=2)
        self.assertEqual(len(ts), 2)

        self.assertEqual(ts[0], self.p5)
        self.assertEqual(ts[1], self.p4)

        # Tests the direct categories
        ts = lfs.marketing.utils.get_topseller_for_category(self.c11, limit=2)
        self.assertEqual(len(ts), 2)
        self.assertEqual(ts[0], self.p5)
        self.assertEqual(ts[1], self.p2)

        # The explicit topseller with category 1 has no impact for topsellers of
        # c2
        ts = lfs.marketing.utils.get_topseller_for_category(self.c12, limit=2)
        self.assertEqual(len(ts), 2)
        self.assertEqual(ts[0], self.p4)
        self.assertEqual(ts[1], self.p3)

        # Now we add Product 5 also to c12
        self.c12.products = (self.p3, self.p4, self.p5)
        self.c12.save()

        # Now Product 5 is among the topseller
        ts = lfs.marketing.utils.get_topseller_for_category(self.c12, limit=2)
        self.assertEqual(len(ts), 2)
        self.assertEqual(ts[0], self.p5)
        self.assertEqual(ts[1], self.p4)

        # Change to position of p5 to 2
        t5.position = 2
        t5.save()

        ts = lfs.marketing.utils.get_topseller_for_category(self.c12, limit=2)
        self.assertEqual(len(ts), 2)
        self.assertEqual(ts[0], self.p4)
        self.assertEqual(ts[1], self.p5)

        # Change to position of p5 to 3. it isn't within topsellers anymore
        t5.position = 3
        t5.save()

        ts = lfs.marketing.utils.get_topseller_for_category(self.c12, limit=2)
        self.assertEqual(len(ts), 2)
        self.assertEqual(ts[0], self.p4)
        self.assertEqual(ts[1], self.p3)

    def test_topseller_for_category_3(self):
        """Tests the top seller for specific categories. With explicitly
        selected products and ca
        """
        # Tests the top level category
        ts = lfs.marketing.utils.get_topseller_for_category(self.c1, limit=2)
        self.assertEqual(len(ts), 2)

        self.assertEqual(ts[0], self.p4)
        self.assertEqual(ts[1], self.p3)

        # Explicit topseller P4 for c1, which is already a topseller
        t = Topseller.objects.create(product=self.p4, position=1)

        # Tests the top level category
        ts = lfs.marketing.utils.get_topseller_for_category(self.c1, limit=2)
        self.assertEqual(len(ts), 2)

        self.assertEqual(ts[0], self.p4)
        self.assertEqual(ts[1], self.p3)

        # Tests the direct categories
        ts = lfs.marketing.utils.get_topseller_for_category(self.c12, limit=2)
        self.assertEqual(len(ts), 2)

        self.assertEqual(ts[0], self.p4)
        self.assertEqual(ts[1], self.p3)
