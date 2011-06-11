# django imports
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.file import SessionStore
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.test.client import Client

# test imports
from lfs.catalog.models import Product
from lfs.cart.models import Cart
from lfs.cart.models import CartItem
from lfs.cart.views import add_to_cart
from lfs.cart import utils as cart_utils
from lfs.core.models import Country
from lfs.customer.models import Address
from lfs.customer.models import Customer
from lfs.order.models import Order
from lfs.order.utils import add_order
from lfs.order.settings import SUBMITTED
from lfs.payment.models import PaymentMethod
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax
from lfs.tests.utils import DummySession
from lfs.tests.utils import RequestFactory


class OrderTestCase(TestCase):
    """
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        session = SessionStore()

        rf = RequestFactory()
        self.request = rf.get('/')
        self.request.session = session
        self.request.user = AnonymousUser()

        tax = Tax.objects.create(rate=19)

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
        ie = Country.objects.get(code="ie")

        address1 = Address.objects.create(
            firstname="John",
            lastname="Doe",
            company_name="Doe Ltd.",
            street="Street 42",
            city="Gotham City",
            zip_code="2342",
            country=ie,
            phone="555-111111",
            email="john@doe.com",
        )

        address2 = Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            company_name="Doe Ltd.",
            street="Street 43",
            city="Smallville",
            zip_code="2443",
            country=us,
            phone="666-111111",
            email="jane@doe.com",
        )

        self.customer = Customer.objects.create(
            session=session.session_key,
            selected_shipping_method=shipping_method,
            selected_payment_method=payment_method,
            selected_shipping_address=address1,
            selected_invoice_address=address2,
        )

        p1 = Product.objects.create(
            name="Product 1",
            slug="product-1",
            sku="sku-1",
            price=1.1,
            tax=tax,
        )

        p2 = Product.objects.create(
            name="Product 2",
            slug="product-2",
            sku="sku-2",
            price=2.2,
            tax=tax,
        )

        cart = Cart.objects.create(
            session=session.session_key
        )

        item = CartItem.objects.create(
            cart=cart,
            product=p1,
            amount=2,
        )

        item = CartItem.objects.create(
            cart=cart,
            product=p2,
            amount=3,
        )

    def test_add_order(self):
        """Tests the general adding of an order via the add_order method
        """
        order = add_order(self.request)

        self.assertEqual(order.state, SUBMITTED)
        self.assertEqual("%.2f" % order.price, "9.80")
        self.assertEqual("%.2f" % order.tax, "1.56")

        self.assertEqual(order.shipping_method.name, "Standard")
        self.assertEqual(order.shipping_price, 1.0)
        self.assertEqual("%.2f" % order.shipping_tax, "0.16")

        self.assertEqual(order.payment_method.name, "Direct Debit")
        self.assertEqual(order.payment_price, 0.0)
        self.assertEqual(order.payment_tax, 0.0)

        self.assertEqual(order.shipping_firstname, "John")
        self.assertEqual(order.shipping_lastname, "Doe")
        self.assertEqual(order.shipping_line1, "Doe Ltd.")
        self.assertEqual(order.shipping_line2, "Street 42")
        self.assertEqual(order.shipping_city, "Gotham City")
        self.assertEqual(order.shipping_code, "2342")
        self.assertEqual(order.shipping_phone, "555-111111")

        self.assertEqual(order.invoice_firstname, "Jane")
        self.assertEqual(order.invoice_lastname, "Doe")
        self.assertEqual(order.invoice_line1, "Doe Ltd.")
        self.assertEqual(order.invoice_line2, "Street 43")
        self.assertEqual(order.invoice_city, "Smallville")
        self.assertEqual(order.invoice_code, "2443")
        self.assertEqual(order.invoice_phone, "666-111111")

        # Items
        self.assertEqual(len(order.items.all()), 2)

        item = order.items.all().order_by('id')[0]
        self.assertEqual(item.product_amount, 2)
        self.assertEqual(item.product_sku, "sku-1")
        self.assertEqual(item.product_name, "Product 1")
        self.assertEqual("%.2f" % item.product_price_gross, "1.10")
        self.assertEqual("%.2f" % item.product_price_net, "0.92")
        self.assertEqual("%.2f" % item.product_tax, "0.18")

        item = order.items.all().order_by('id')[1]
        self.assertEqual(item.product_amount, 3)
        self.assertEqual(item.product_sku, "sku-2")
        self.assertEqual(item.product_name, "Product 2")
        self.assertEqual("%.2f" % item.product_price_gross, "2.20")
        self.assertEqual("%.2f" % item.product_price_net, "1.85")
        self.assertEqual("%.2f" % item.product_tax, "0.35")

        # The cart should be deleted after the order has been created
        cart = cart_utils.get_cart(self.request)
        self.assertEqual(cart, None)

    def test_pay_link(self):
        """Tests empty pay link.
        """
        from lfs.payment.utils import process_payment
        result = process_payment(self.request)

        order = Order.objects.filter()[0]
        self.assertEqual(order.get_pay_link(), "")

    def test_paypal_link(self):
        """Tests created paypal link.
        """
        payment_method, created = PaymentMethod.objects.get_or_create(
            id=3,
            name="PayPal",
            active=True,
        )

        self.customer.selected_payment_method = payment_method
        self.customer.save()

        from lfs.payment.utils import process_payment
        result = process_payment(self.request)

        order = Order.objects.filter()[0]
        self.failIf(order.get_pay_link().find("paypal") == -1)
