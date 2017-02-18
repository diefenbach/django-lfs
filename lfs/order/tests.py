import locale
import datetime

from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.file import SessionStore
from django.test import TestCase

from lfs.catalog.models import Product, DeliveryTime
from lfs.cart.models import Cart
from lfs.cart.models import CartItem
from lfs.cart import utils as cart_utils
from lfs.core.models import Country
from lfs.addresses.models import Address
from lfs.customer.models import Customer
from lfs.discounts.settings import DISCOUNT_TYPE_ABSOLUTE
from lfs.order.models import Order
from lfs.order.models import OrderItem
from lfs.order.utils import add_order
from lfs.order.settings import SUBMITTED
from lfs.payment.models import PaymentMethod
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax
from lfs.tests.utils import RequestFactory
from lfs.discounts.models import Discount


class OrderTestCase(TestCase):
    """
    """
    fixtures = ['lfs_shop.xml', "lfs_user.xml"]

    def setUp(self):
        """
        """
        session = SessionStore()
        session.save()

        rf = RequestFactory()
        self.request = rf.get('/')
        self.request.session = session
        self.request.user = AnonymousUser()

        tax = Tax.objects.create(rate=19)

        delivery_time = DeliveryTime.objects.create(min=3, max=10)

        shipping_method = ShippingMethod.objects.create(
            name="Standard",
            active=True,
            price=1.0,
            tax=tax,
            delivery_time=delivery_time
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
            line1="Street 42",
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
            line1="Street 43",
            city="Smallville",
            zip_code="2443",
            country=us,
            phone="666-111111",
            email="jane@doe.com",
        )

        Address.objects.create(
            firstname="John",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 42",
            city="Gotham City",
            zip_code="2342",
            country=ie,
            phone="555-111111",
            email="john@doe.com",
        )

        Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            company_name="Doe Ltd.",
            line1="Street 43",
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
            default_shipping_address=address1,
            default_invoice_address=address2,
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

        CartItem.objects.create(
            cart=cart,
            product=self.p1,
            amount=2,
        )

        CartItem.objects.create(
            cart=cart,
            product=self.p2,
            amount=3,
        )

    def test_add_order(self):
        """Tests the general adding of an order via the add_order method
        """
        # check we have 2 addresses before the order
        self.assertEqual(4, Address.objects.count())

        order = add_order(self.request)

        # adding an order should deep copy our addresses above
        self.assertEqual(6, Address.objects.count())

        self.assertEqual(order.state, SUBMITTED)
        self.assertEqual("%.2f" % order.price, "9.80")
        self.assertEqual("%.2f" % order.tax, "1.56")

        self.assertEqual(order.shipping_method.name, "Standard")
        self.assertEqual(order.shipping_price, 1.0)
        self.assertEqual("%.2f" % order.shipping_tax, "0.16")

        self.assertEqual(order.payment_method.name, "Direct Debit")
        self.assertEqual(order.payment_price, 0.0)
        self.assertEqual(order.payment_tax, 0.0)

        self.assertEqual(order.shipping_address.firstname, "John")
        self.assertEqual(order.shipping_address.lastname, "Doe")
        self.assertEqual(order.shipping_address.line1, "Street 42")
        self.assertEqual(order.shipping_address.line2, None)
        self.assertEqual(order.shipping_address.city, "Gotham City")
        self.assertEqual(order.shipping_address.zip_code, "2342")
        self.assertEqual(order.shipping_address.phone, "555-111111")
        self.assertEqual(order.shipping_address.company_name, "Doe Ltd.")

        self.assertEqual(order.invoice_address.firstname, "Jane")
        self.assertEqual(order.invoice_address.lastname, "Doe")
        self.assertEqual(order.invoice_address.line1, "Street 43")
        self.assertEqual(order.invoice_address.line2, None)
        self.assertEqual(order.invoice_address.city, "Smallville")
        self.assertEqual(order.invoice_address.zip_code, "2443")
        self.assertEqual(order.invoice_address.phone, "666-111111")
        self.assertEqual(order.invoice_address.company_name, "Doe Ltd.")

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

        # delivery time should of the selected shipping method should be saved with order
        self.assertTrue(order.delivery_time is not None)

    def test_pay_link(self):
        """Tests empty pay link.
        """
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        from lfs.payment.utils import process_payment
        process_payment(self.request)

        order = Order.objects.filter()[0]
        self.assertEqual(order.get_pay_link(self.request), "")

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
        process_payment(self.request)

        order = Order.objects.filter()[0]
        self.failIf(order.get_pay_link(self.request).find("paypal") == -1)

    def test_delete_product(self):
        """Tests that OrderItems are not deleted when a product is deleted.
        """
        address = Address.objects.create()
        order = Order.objects.create(invoice_address=address, shipping_address=address)
        order_item_1 = OrderItem.objects.create(order=order, product=self.p1)
        self.p1.delete()
        OrderItem.objects.get(pk=order_item_1.id)

    def test_summed_up_order_discounts(self):
        """Tests the price of the discount within an order.
        """
        self.tax = Tax.objects.create(rate=19)

        Discount.objects.create(name="Summer",
                                active=True,
                                value=10.0,
                                type=DISCOUNT_TYPE_ABSOLUTE,
                                tax=self.tax,
                                sums_up=True)

        discount_value = 11.0
        Discount.objects.create(name="Special offer 1",
                                active=True,
                                value=discount_value,
                                type=DISCOUNT_TYPE_ABSOLUTE,
                                tax=self.tax,
                                sums_up=False)

        order = add_order(self.request)
        tax_value = discount_value * (self.tax.rate / (100.0 + self.tax.rate))

        all_product_names = list(order.items.values_list('product_name', flat=True))
        self.assertTrue("Summer" not in all_product_names)
        self.assertTrue("Special offer 1" in all_product_names)
        for order_item in order.items.all():
            if order_item.product_name == "Special offer 1":
                self.assertEqual("%.2f" % order_item.price_net, "%.2f" % (-discount_value + tax_value))
                self.assertEqual("%.2f" % order_item.product_price_net, "%.2f" % (-discount_value + tax_value))

    def test_summed_up_order_discounts_and_vouchers(self):
        """Tests the price of the discount/voucher within an order.
           We have 2 discounts ('Summer' is able to sum up) and 1 voucher (able to sum up)
           We expect 'Summer' discount to be applied as well as voucher as these can sum up and their total value
           is bigger than 'Special offer 1' discount's

        """
        tax = Tax.objects.create(rate=19)

        Discount.objects.create(name="Summer",
                                active=True,
                                value=10.0,
                                type=DISCOUNT_TYPE_ABSOLUTE,
                                tax=tax,
                                sums_up=True)

        discount_value = 11.0
        Discount.objects.create(name="Special offer 1",
                                active=True,
                                value=discount_value,
                                type=DISCOUNT_TYPE_ABSOLUTE,
                                tax=tax,
                                sums_up=False)

        # vouchers
        from lfs.voucher.models import VoucherGroup, Voucher
        from lfs.voucher.settings import ABSOLUTE

        user = User.objects.get(username="admin")

        self.vg = VoucherGroup.objects.create(
            name="xmas",
            creator=user
        )
        voucher_value = 12.0

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

        self.request.session['voucher'] = 'AAAA'

        order = add_order(self.request)
        voucher_value * (tax.rate / (100.0 + tax.rate))

        all_product_names = list(order.items.values_list('product_name', flat=True))
        # voucher value is biggest one
        self.assertTrue("Summer" in all_product_names)
        self.assertTrue("Special offer 1" not in all_product_names)
        self.assertEqual(order.voucher_price, voucher_value)

    def test_summed_up_order_discounts_and_vouchers2(self):
        """Tests the price of the discount/voucher within an order.
           We have 2 discounts ('Summer' is able to sum up) and 1 voucher (able to sum up)
           We expect 'Special offer 1' discount to be applied as it's value is bigger than value of summed up
           'Summer' discount and Voucher

        """
        tax = Tax.objects.create(rate=19)

        Discount.objects.create(name="Summer",
                                active=True,
                                value=10.0,
                                type=DISCOUNT_TYPE_ABSOLUTE,
                                tax=tax,
                                sums_up=True)

        discount_value = 25.0
        Discount.objects.create(name="Special offer 1",
                                active=True,
                                value=discount_value,
                                type=DISCOUNT_TYPE_ABSOLUTE,
                                tax=tax,
                                sums_up=False)

        # vouchers
        from lfs.voucher.models import VoucherGroup, Voucher
        from lfs.voucher.settings import ABSOLUTE

        user = User.objects.get(username="admin")

        self.vg = VoucherGroup.objects.create(
            name="xmas",
            creator=user
        )
        voucher_value = 12.0

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

        self.request.session['voucher'] = 'AAAA'

        order = add_order(self.request)
        voucher_value * (tax.rate / (100.0 + tax.rate))

        all_product_names = list(order.items.values_list('product_name', flat=True))
        # voucher value is biggest one
        self.assertTrue("Summer" not in all_product_names)
        self.assertTrue("Special offer 1" in all_product_names)
        self.assertEqual(order.voucher_price, 0)
