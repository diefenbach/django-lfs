# django imports
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.file import SessionStore
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

# test imports
from lfs.tests.utils import create_request
from lfs.tests.utils import DummyRequest

# lfs imports
import lfs.cart.utils
from lfs.cart.models import Cart
from lfs.cart.models import CartItem
from lfs.cart.views import add_to_cart
from lfs.cart import utils as cart_utils
from lfs.catalog.models import Product
from lfs.core.models import Country
from lfs.customer.models import Address
from lfs.customer.models import Customer
from lfs.order.models import Order
from lfs.order.models import OrderItem
from lfs.order.utils import add_order
from lfs.criteria.models import WeightCriterion
from lfs.criteria.models import CriteriaObjects
from lfs.criteria.settings import GREATER_THAN, LESS_THAN
from lfs.discounts.models import Discount
from lfs.payment.models import PaymentMethod
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax
from lfs.tests.utils import RequestFactory

class DiscountsTestCase1(TestCase):
    """Unit tests for lfs.discounts
    """
    fixtures = ['lfs_shop.xml', "lfs_user.xml"]

    def setUp(self):
        """
        """
        self.user = User.objects.get(username="admin")
        self.request = DummyRequest(user=self.user)

        self.d = Discount.objects.create(name="Summer", value=10.0, type=0)
        self.p = Product.objects.create(name="Product", slug="p", price=11, weight=12.0)

        # Delete the cart for every test method.
        cart = lfs.cart.utils.get_cart(self.request)
        if cart:
            cart.delete()

    def test_model(self):
        """
        """
        self.assertEqual(self.d.name, "Summer")
        self.assertEqual(self.d.value, 10.0)
        self.assertEqual(self.d.type, 0)

        self.assertEqual(self.d.is_valid(self.request), True)

    def test_criteria(self):
        """
        """
        c = WeightCriterion.objects.create(weight=10.0, operator=GREATER_THAN)
        co = CriteriaObjects(criterion=c, content=self.d)
        co.save()

        self.assertEqual(self.d.is_valid(self.request), False)
        self.assertEqual(self.d.is_valid(self.request, self.p), True)


class DiscountTestCase2(TestCase):
    """
    """
    fixtures = ['lfs_shop.xml', "lfs_user.xml"]

    def setUp(self):
        """
        """
        session = SessionStore()

        rf = RequestFactory()
        self.request = rf.get('/')
        self.request.session = session
        self.request.user = AnonymousUser()

        tax = Tax.objects.create(rate=19)

        discount = Discount.objects.create(name="Summer", value=10.0, type=0, tax=tax)

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

        us = Country.objects.get(code="us")

        address1 = Address.objects.create(
            firstname="John",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 42",
            city="Gotham City",
            zip_code="2342",
            country=us,
            phone="555-111111",
            email="john@doe.com",
        )

        self.customer = Customer.objects.create(
            session=session.session_key,
            selected_shipping_method=shipping_method,
            selected_payment_method=payment_method,
            selected_shipping_address=address1,
            selected_invoice_address=address1,
        )

        self.p1 = Product.objects.create(
            name="Product 1",
            slug="product-1",
            sku="sku-1",
            price=1.1,
            tax=tax,
            active=True,
        )

        self.p2 = Product.objects.create(
            name="Product 2",
            slug="product-2",
            sku="sku-2",
            price=2.2,
            tax=tax,
            active=True,
        )

        cart = Cart.objects.create(
            session=session.session_key
        )

        item = CartItem.objects.create(
            cart=cart,
            product=self.p1,
            amount=2,
        )

        item = CartItem.objects.create(
            cart=cart,
            product=self.p2,
            amount=3,
        )

    def test_order_discount_price(self):
        """Tests the price of the discount within an order.
        """
        order = add_order(self.request)

        for order_item in order.items.all():
            if order_item.product_name == "Summer":
                self.assertEqual("%.2f" % order_item.price_net, "-8.40")
                self.assertEqual("%.2f" % order_item.product_price_net, "-8.40")
