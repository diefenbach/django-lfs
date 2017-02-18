# coding: utf-8

import locale
import json
import datetime

from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.file import SessionStore
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import TestCase

import lfs.cart.utils
from lfs.cart.models import Cart
from lfs.cart.models import CartItem
from lfs.cart.utils import get_cart
from lfs.cart.utils import update_cart_after_login
from lfs.cart.views import add_to_cart
from lfs.cart.views import added_to_cart_items
from lfs.cart.views import refresh_cart
from lfs.catalog.models import DeliveryTime
from lfs.catalog.models import Product
from lfs.catalog.models import GroupsPropertiesRelation
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyGroup
from lfs.catalog.settings import CONFIGURABLE_PRODUCT
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.catalog.settings import DELIVERY_TIME_UNIT_DAYS
from lfs.catalog.settings import PROPERTY_TEXT_FIELD
from lfs.tests.utils import RequestFactory
from lfs.tax.models import Tax


class LoginTestCase(TestCase):
    fixtures = ['lfs_shop.xml', "lfs_user.xml"]

    def setUp(self):
        self.p0 = Product.objects.create(name="Product 0", slug="product-0", price=5, active=True, sub_type=STANDARD_PRODUCT)

        self.pg = PropertyGroup.objects.create(name="T-Shirts")
        self.pp1 = Property.objects.create(name="Length", type=PROPERTY_TEXT_FIELD)
        self.gpr1 = GroupsPropertiesRelation.objects.create(group=self.pg, property=self.pp1)

        self.p1 = Product.objects.create(name="Product 1", slug="product-1", price=5, active=True, sub_type=CONFIGURABLE_PRODUCT)
        self.pg.products = [self.p1]
        self.pg.save()

        self.admin = User.objects.get(username="admin")

    def test_standard_product(self):
        session = SessionStore()
        rf = RequestFactory()

        request = rf.post("/", {"product_id": self.p0.id, "quantity": 1})
        request.session = session
        request.user = AnonymousUser()

        cart = get_cart(request)
        self.assertEqual(cart, None)

        add_to_cart(request)

        cart = get_cart(request)
        self.assertEqual(int(cart.get_items()[0].amount), 1)

        # 1l login admin
        request = rf.get("/")
        request.session = session
        request.user = self.admin

        cart = get_cart(request)
        self.assertEqual(cart, None)

        update_cart_after_login(request)

        cart = get_cart(request)
        self.assertEqual(int(cart.get_items()[0].amount), 1)

        # logout
        session = SessionStore()
        request = rf.post("/", {"product_id": self.p0.id, "quantity": 2})
        request.session = session
        request.user = AnonymousUser()

        cart = get_cart(request)
        self.assertEqual(cart, None)

        add_to_cart(request)

        cart = get_cart(request)
        self.assertEqual(int(cart.get_items()[0].amount), 2)

        # 2. login admin
        request = rf.get("/")
        request.session = session
        request.user = self.admin

        cart = get_cart(request)
        self.assertEqual(int(cart.get_items()[0].amount), 1)

        update_cart_after_login(request)

        cart = get_cart(request)
        self.assertEqual(int(cart.get_items()[0].amount), 3)

    def test_configurable_product(self):
        rf = RequestFactory()
        session = SessionStore()

        request = rf.post("/", {"product_id": self.p1.id, "quantity": 1, "property-%s-%s" % (self.pg.pk,
                                                                                             self.pp1.id): "A"})
        request.session = session
        request.user = AnonymousUser()

        cart = get_cart(request)
        self.assertEqual(cart, None)

        add_to_cart(request)

        cart = get_cart(request)
        self.assertEqual(int(cart.get_items()[0].amount), 1)

        request = rf.post("/", {"product_id": self.p1.id, "quantity": 10, "property-%s-%s" % (self.pg.pk,
                                                                                              self.pp1.id): "B"})
        request.session = session
        request.user = AnonymousUser()
        add_to_cart(request)

        cart = get_cart(request)
        self.assertEqual(int(cart.get_items()[0].amount), 1)
        self.assertEqual(int(cart.get_items()[1].amount), 10)

        # 1. login admin
        request = rf.get("/")
        request.session = session
        request.user = self.admin

        cart = get_cart(request)
        self.assertEqual(cart, None)

        update_cart_after_login(request)

        cart = get_cart(request)
        self.assertEqual(int(cart.get_items()[0].amount), 1)
        self.assertEqual(int(cart.get_items()[1].amount), 10)

        # logout
        session = SessionStore()

        request = rf.post("/", {"product_id": self.p1.id, "quantity": 2, "property-%s-%s" % (self.pg.pk,
                                                                                             self.pp1.id): "A"})
        request.session = session
        request.user = AnonymousUser()

        cart = get_cart(request)
        self.assertEqual(cart, None)

        add_to_cart(request)

        cart = get_cart(request)
        self.assertEqual(int(cart.get_items()[0].amount), 2)

        request = rf.post("/", {"product_id": self.p1.id, "quantity": 20, "property-%s-%s" % (self.pg.pk,
                                                                                              self.pp1.id): "B"})
        request.session = session
        request.user = AnonymousUser()
        add_to_cart(request)

        cart = get_cart(request)
        self.assertEqual(int(cart.get_items()[0].amount), 2)
        self.assertEqual(int(cart.get_items()[1].amount), 20)

        # 2. login admin
        request = rf.get("/")
        request.session = session
        request.user = self.admin

        cart = get_cart(request)
        self.assertEqual(int(cart.get_items()[0].amount), 1)
        self.assertEqual(int(cart.get_items()[1].amount), 10)

        update_cart_after_login(request)

        cart = get_cart(request)
        self.assertEqual(int(cart.get_items()[0].amount), 3)
        self.assertEqual(int(cart.get_items()[1].amount), 30)


class CartModelsTestCase(TestCase):
    """
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        self.request = RequestFactory().get("/")
        self.request.session = SessionStore()
        self.request.user = User(id=1)

        self.tax = Tax.objects.create(rate=19.0)

        self.p1 = Product.objects.create(name="Product 1", slug="product-1", price=10.0, tax=self.tax, active=True)
        self.p2 = Product.objects.create(name="Product 2", slug="product-2", price=100.0, tax=self.tax, active=True)
        # This product is not considered as it is not active
        self.p3 = Product.objects.create(name="Product 3", slug="product-3", price=1000.0, tax=self.tax, active=False)

        self.cart = Cart.objects.create()
        CartItem.objects.create(cart=self.cart, product=self.p1, amount=1)
        CartItem.objects.create(cart=self.cart, product=self.p2, amount=1)
        CartItem.objects.create(cart=self.cart, product=self.p3, amount=1)

    def test_get_price(self):
        """
        """
        price_net = self.cart.get_price_net(self.request)
        self.assertEqual("%.2f" % price_net, "%.2f" % 92.44)

    def test_get_gross(self):
        """
        """
        price_gross = self.cart.get_price_gross(self.request)
        self.assertEqual(price_gross, 110.0)

    def test_tax(self):
        """
        """
        tax = self.cart.get_tax(self.request)
        self.assertEqual("%.2f" % tax, "%.2f" % 17.56)

    def test_get_amount_of_items(self):
        """
        """
        amount = self.cart.get_amount_of_items()
        self.assertEqual(amount, 2)

    def test_get_items(self):
        """
        """
        items = self.cart.get_items()
        self.assertEqual(len(items), 2)


class CartItemTestCase(TestCase):
    """
    """
    fixtures = ['lfs_shop.xml', "lfs_user.xml"]

    def setUp(self):
        self.tax = Tax.objects.create(rate=19.0)

        self.p1 = Product.objects.create(name="Product 1", slug="product-1", price=10.0, tax=self.tax, active=True)
        self.p2 = Product.objects.create(name="Product 2", slug="product-2", price=100.0, tax=self.tax)

        self.cart = Cart.objects.create()
        self.item = CartItem.objects.create(cart=self.cart, product=self.p1, amount=1)

    def test_get_properties(self):
        """
        """
        result = self.item.get_properties()
        self.assertEqual(result, [])

    def test_get_items(self):
        """ If product that is in the cart is out of stock then cart.get_items should update cart_items.
        """
        self.assertFalse(self.p1.manage_stock_amount)
        self.assertTrue(self.p1.active)
        self.assertEqual(len(list(self.cart.get_items())), 1)
        self.p1.manage_stock_amount = True
        self.p1.stock_amount = 2
        self.p1.save()

        self.assertEqual(len(list(self.cart.get_items())), 1)
        self.p1.stock_amount = 0
        self.p1.save()
        self.assertEqual(len(list(self.cart.get_items())), 0)


class AddToCartTestCase(TestCase):
    """Test case for add_to_cart view.
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        self.p1 = Product.objects.create(name="Product 1", slug="product-1", price=10.0)
        from django.contrib.auth.models import User

        self.dt = DeliveryTime.objects.create(min=1, max=2, unit=DELIVERY_TIME_UNIT_DAYS)
        self.user = User.objects.create(username="doe")
        self.session = SessionStore()
        self.session.save()

    def test_add_to_cart_non_active(self):
        """Try to add product to the cart which is not active.
        """
        rf = RequestFactory()
        request = rf.post("/", {"product_id": self.p1.id, "quantity": 1})
        request.session = self.session
        request.user = self.user

        self.assertRaises(Http404, add_to_cart, request, self.p1.id)

    def test_add_to_cart_not_deliverable(self):
        """Try to add product to the cart which is not deliverable.
        """
        self.p1.active = True
        self.p1.deliverable = False
        self.p1.save()

        rf = RequestFactory()
        request = rf.post("/", {"product_id": self.p1.id, "quantity": 1})
        request.session = self.session
        request.user = self.user

        # Not deliverable
        self.assertRaises(Http404, add_to_cart, request, self.p1.id)

    def test_add_to_cart_not_in_stock(self):
        """Try to add product to the cart which is not in stock.
        """
        self.p1.active = True
        self.p1.deliverable = True
        self.p1.manage_stock_amount = True
        self.p1.stock_amount = 0
        self.p1.save()

        rf = RequestFactory()
        request = rf.post("/", {"product_id": self.p1.id, "quantity": 2})
        request.session = self.session
        request.user = self.user

        self.assertRaises(Http404, add_to_cart, request)

        # But no message if product is ordered ...
        self.p1.order_time = self.dt
        self.p1.save()

        result = add_to_cart(request)
        self.failIf("message" in result.cookies)

        # ... or LFS doesn't manage stock amount
        self.p1.manage_stock_amount = False
        self.p1.order_time = None
        self.p1.save()

        result = add_to_cart(request)
        self.failIf("message" in result.cookies)

    def test_add_to_cart_stock_1(self):
        """Try to add product two times to cart if only one is in stock.
        """
        self.p1.active = True
        self.p1.deliverable = True
        self.p1.manage_stock_amount = True
        self.p1.stock_amount = 1
        self.p1.save()

        rf = RequestFactory()
        request = rf.post("/", {"product_id": self.p1.id, "quantity": 2})
        request.session = self.session
        request.user = self.user

        # This need to result in a message to the customer
        result = add_to_cart(request)
        self.failIf(result.cookies.get("message").__str__().find("Sorry%2C%20but%20%27Product%201%27%20is%20only%20one%20time%20available.") == -1)

        # But no message if product is ordered ...
        self.p1.order_time = self.dt
        self.p1.save()

        result = add_to_cart(request)
        self.failIf("message" in result.cookies)

        # ... or LFS doesn't manage stock amount
        self.p1.manage_stock_amount = False
        self.p1.order_time = None
        self.p1.save()

        result = add_to_cart(request)
        self.failIf("message" in result.cookies)

    def test_add_to_cart_stock_2(self):
        """Try to add product three times to cart if only two is in stock.
        """
        self.p1.active = True
        self.p1.deliverable = True
        self.p1.manage_stock_amount = True
        self.p1.stock_amount = 2
        self.p1.save()

        rf = RequestFactory()
        request = rf.post("/", {"product_id": self.p1.id, "quantity": 3})
        request.session = self.session
        request.user = self.user

        # This need to result in a message to the customer
        result = add_to_cart(request)
        self.failIf(result.cookies.get("message").__str__().find("Sorry%2C%20but%20%27Product%201%27%20is%20only%202.0%20times%20available.") == -1)

        # But no message if product is ordered ...
        self.p1.order_time = self.dt
        self.p1.save()

        result = add_to_cart(request)
        self.failIf("message" in result.cookies)

        # ... or LFS doesn't manage stock amount
        self.p1.manage_stock_amount = False
        self.p1.order_time = None
        self.p1.save()

        result = add_to_cart(request)
        self.failIf("message" in result.cookies)


class RefreshCartTestCase(TestCase):
    """Test case for refresh_cart view.
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        self.p1 = Product.objects.create(name="Product 1", slug="product-1", price=10.0, active=True)
        self.dt = DeliveryTime.objects.create(min=1, max=2, unit=DELIVERY_TIME_UNIT_DAYS)
        self.user = User.objects.create(username="doe")
        self.session = SessionStore()
        self.session.save()

    def test_amount_1(self):
        """Don't manage stock amount.
        """
        rf = RequestFactory()
        request = rf.post("/", {"product_id": self.p1.id, "quantity": 1})
        request.session = self.session
        request.user = self.user

        # Add product to cart
        add_to_cart(request)

        cart = lfs.cart.utils.get_cart(request)
        self.assertEqual(cart.get_amount_of_items(), 1.0)

        # prepare shipping/payment methods
        from lfs.payment.models import PaymentMethod
        from lfs.shipping.models import ShippingMethod
        pm = PaymentMethod.objects.create(name='pm')
        sm = ShippingMethod.objects.create(name='sm')

        # Refresh item amount
        request = rf.post("/", {"product_id": self.p1.id, "amount-cart-item_%s" % cart.get_items()[0].id: 2,
                                "shipping_method": sm.pk, "payment_method": pm.pk})
        request.session = self.session
        request.user = self.user
        refresh_cart(request)
        self.assertEqual(cart.get_amount_of_items(), 2.0)

    def test_amount_2(self):
        """Manage stock amount; refresh to 2 only 1 products there.
        """
        self.p1.manage_stock_amount = True
        self.p1.stock_amount = 1
        self.p1.save()

        rf = RequestFactory()
        request = rf.post("/", {"product_id": self.p1.id, "quantity": 1})
        request.session = self.session
        request.user = self.user

        # Add product to cart
        result = add_to_cart(request)

        cart = lfs.cart.utils.get_cart(request)
        self.assertEqual(cart.get_amount_of_items(), 1.0)

        # prepare shipping/payment methods
        from lfs.payment.models import PaymentMethod
        from lfs.shipping.models import ShippingMethod
        pm = PaymentMethod.objects.create(name='pm')
        sm = ShippingMethod.objects.create(name='sm')

        # Try to increase item to two, but there is only one in stock
        request = rf.post("/", {"product_id": self.p1.id, "amount-cart-item_%s" % cart.get_items()[0].id: 2,
                                "shipping_method": sm.pk, "payment_method": pm.pk})
        request.session = self.session
        request.user = self.user

        # This results into a message to the customer
        result = json.loads(refresh_cart(request).content)
        self.assertEqual(result.get("message"), "Sorry, but \'Product 1\' is only one time available.")

        # And the amount of the item is still 1.0
        self.assertEqual(cart.get_amount_of_items(), 1.0)

        # If the product is ordered the customer can add it into cart again
        self.p1.order_time = self.dt
        self.p1.save()

        result = json.loads(refresh_cart(request).content)
        self.assertEqual(result.get("message"), "")
        self.assertEqual(cart.get_amount_of_items(), 2.0)

        # Or if LFS not managing stock amount the product can be added to the cart
        self.p1.order_time = None
        self.p1.manage_stock_amount = False
        self.p1.save()

        result = json.loads(refresh_cart(request).content)
        self.assertEqual(result.get("message"), "")
        self.assertEqual(cart.get_amount_of_items(), 2.0)

    def test_amount_3(self):
        """Manage stock amount; refresh to 3 only 2 products there.
        """
        self.p1.manage_stock_amount = True
        self.p1.stock_amount = 2
        self.p1.save()

        rf = RequestFactory()
        request = rf.post("/", {"product_id": self.p1.id, "quantity": 1})
        request.session = self.session
        request.user = self.user

        # Add product to cart
        result = add_to_cart(request)

        cart = lfs.cart.utils.get_cart(request)
        self.assertEqual(cart.get_amount_of_items(), 1.0)

        # prepare shipping/payment methods
        from lfs.payment.models import PaymentMethod
        from lfs.shipping.models import ShippingMethod
        pm = PaymentMethod.objects.create(name='pm')
        sm = ShippingMethod.objects.create(name='sm')

        # Increase items to two
        request = rf.post("/", {"product_id": self.p1.id, "amount-cart-item_%s" % cart.get_items()[0].id: 2,
                                "shipping_method": sm.pk, "payment_method": pm.pk})
        request.session = self.session
        request.user = self.user

        # Refresh to amount of two is possible
        result = json.loads(refresh_cart(request).content)
        self.assertEqual(result.get("message"), "")
        self.assertEqual(cart.get_amount_of_items(), 2.0)

        # Try to increase item to 3, but there are only 2 in stock
        request = rf.post("/", {"product_id": self.p1.id, "amount-cart-item_%s" % cart.get_items()[0].id: 3,
                                "shipping_method": sm.pk, "payment_method": pm.pk})
        request.session = self.session
        request.user = self.user

        result = json.loads(refresh_cart(request).content)
        self.assertEqual(result.get("message"), "Sorry, but \'Product 1\' is only 2.0 times available.")

        # And the amount of the item is still 2.0
        self.assertEqual(cart.get_amount_of_items(), 2.0)

        # If the product is ordered the customer can add it into cart again
        self.p1.order_time = self.dt
        self.p1.save()

        result = json.loads(refresh_cart(request).content)
        self.assertEqual(result.get("message"), "")
        self.assertEqual(cart.get_amount_of_items(), 3.0)

        # Or if LFS not managing stock amount the product can be added to the cart
        self.p1.order_time = None
        self.p1.manage_stock_amount = False
        self.p1.save()

        result = json.loads(refresh_cart(request).content)
        self.assertEqual(result.get("message"), "")
        self.assertEqual(cart.get_amount_of_items(), 3.0)

    def test_amount_4(self):
        """Manage stock amount; refresh to 2 but no product is there anymore.
        """
        self.p1.manage_stock_amount = True
        self.p1.stock_amount = 1
        self.p1.save()

        rf = RequestFactory()
        request = rf.post("/", {"product_id": self.p1.id, "quantity": 1})
        request.session = self.session
        request.user = self.user

        # Add product to cart
        result = add_to_cart(request)

        cart = lfs.cart.utils.get_cart(request)
        self.assertEqual(cart.get_amount_of_items(), 1.0)

        item_id = cart.get_items()[0].id

        self.p1.stock_amount = 0
        self.p1.save()

        self.assertEqual(0, len(cart.get_items()))

        # prepare shipping/payment methods
        from lfs.payment.models import PaymentMethod
        from lfs.shipping.models import ShippingMethod
        pm = PaymentMethod.objects.create(name='pm')
        sm = ShippingMethod.objects.create(name='sm')

        # Try to increase item to two, but there is no product in stock anymore
        request = rf.post("/", {"product_id": self.p1.id, "amount-cart-item_%s" % item_id: 2,
                                "shipping_method": sm.pk, "payment_method": pm.pk})
        request.session = self.session
        request.user = self.user

        # Refresh to amount of two is not possible
        result = json.loads(refresh_cart(request).content)
        self.assertEqual(cart.get_amount_of_items(), 0.0)
        self.assertTrue('Your Cart is empty' in result.get("html"))


class AddedToCartTestCase(TestCase):
    """
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        from lfs.customer.models import Customer
        from lfs.addresses.models import Address
        from lfs.shipping.models import ShippingMethod
        from lfs.payment.models import PaymentMethod
        from lfs.core.models import Country

        self.p1 = Product.objects.create(name="Product 1", slug="product-1", price=10.0, active=True, manage_stock_amount=False)
        from django.contrib.auth.models import User

        self.dt = DeliveryTime.objects.create(min=1, max=2, unit=DELIVERY_TIME_UNIT_DAYS)
        self.session = SessionStore()
        self.session.save()

        self.username = 'doe'
        self.password = 'bloggs'

        self.user = User.objects.create(username=self.username)

        self.user.set_password(self.password)
        self.user.save()

        tax = Tax.objects.create(rate=19)
        de = Country.objects.get(code="de")

        shipping_method = ShippingMethod.objects.create(
            name="Standard",
            active=True,
            price=1.0,
            tax=tax
        )

        payment_method = PaymentMethod.objects.create(
            name="Direct Debit",
            active=True,
            tax=tax,
        )

        self.address1 = Address.objects.create(
            firstname="John",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 42",
            city="Gotham City",
            zip_code="23422",
            country=de,
            phone="555-111111",
            email="john@doe.com",
        )

        address_1_id = self.address1.pk

        self.address1.pk = None
        self.address2 = self.address1.save()

        self.address1.pk = None
        self.address3 = self.address1.save()

        self.address1.pk = None
        self.address4 = self.address1.save()

        self.address1 = Address.objects.get(pk=address_1_id)

        self.customer = Customer.objects.create(
            user=self.user,
            selected_shipping_method=shipping_method,
            selected_payment_method=payment_method,
            selected_shipping_address=self.address1,
            selected_invoice_address=self.address2,
            default_shipping_address=self.address3,
            default_invoice_address=self.address4,
        )

    def test_totals_1(self):
        """Add a product without quantity to cart (implicit 1)
        """
        rf = RequestFactory()
        request = rf.post("/", {"product_id": self.p1.id})
        request.session = self.session
        request.user = self.user

        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        # Added product_1 to cart
        add_to_cart(request)
        response = added_to_cart_items(request)

        # need to test for two versions of currency output (Mac and Ubuntu differ)
        self.failIf(response.find(u'Total: <span class="money">$10.00</span>') == -1)

        # Added product_1 to cart again
        add_to_cart(request)
        response = added_to_cart_items(request)
        self.failIf(response.find(u'Total: <span class="money">$20.00</span>') == -1)

    def test_totals_2(self):
        """Add a product with explicit quantity to cart
        """
        rf = RequestFactory()
        request = rf.post("/", {"product_id": self.p1.id, "quantity": 2})
        request.session = self.session
        request.user = self.user

        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        # Added product_1 two times to cart
        add_to_cart(request)
        response = added_to_cart_items(request)
        self.failIf(response.find(u'Total: <span class="money">$20.00</span>') == -1)

        # Added product_1 two times to cart again
        add_to_cart(request)
        response = added_to_cart_items(request)
        self.failIf(response.find(u'Total: <span class="money">$40.00</span>') == -1)

    def test_discounts(self):
        """Add a product with explicit quantity to cart and use discounts/voucher
           Discount 'Summer' and Voucher are able to sum up while discount 'Special offer 1' cannot be summed up.
           Value of summed up 'Summer' and Voucher is bigger than 'Special offer 1' so these two should be used
        """
        from lfs.discounts.models import Discount
        from lfs.discounts.settings import DISCOUNT_TYPE_ABSOLUTE

        tax = Tax.objects.create(rate=19)

        Discount.objects.create(name="Summer",
                                active=True,
                                value=3.0,
                                type=DISCOUNT_TYPE_ABSOLUTE,
                                tax=tax,
                                sums_up=True)

        discount_value = 2.0
        Discount.objects.create(name="Special offer 1",
                                active=True,
                                value=discount_value,
                                type=DISCOUNT_TYPE_ABSOLUTE,
                                tax=tax,
                                sums_up=False)

        # vouchers
        from lfs.voucher.models import VoucherGroup, Voucher
        from lfs.voucher.settings import ABSOLUTE

        user = User.objects.get(username=self.username)

        self.vg = VoucherGroup.objects.create(
            name="xmas",
            creator=user
        )
        voucher_value = 1.0

        self.v1 = Voucher.objects.create(
            number="AAAA",
            group=self.vg,
            creator=user,
            start_date=datetime.date.today() + datetime.timedelta(days=-10),
            end_date=datetime.date.today() + datetime.timedelta(days=10),
            effective_from=0,
            kind_of=ABSOLUTE,
            value=voucher_value,
            sums_up=True,
            limit=2,
            tax=tax
        )

        rf = RequestFactory()
        request = rf.post("/", {"product_id": self.p1.id, "quantity": 2})
        request.session = self.session
        request.user = self.user

        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        add_to_cart(request)
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('lfs_cart'), data={'voucher': self.v1.number})

        self.assertNotContains(response, 'Special offer 1')
        self.assertContains(response, 'Summer')
        self.assertContains(response, 'Voucher')
        self.assertContains(response, 'The voucher is valid')
