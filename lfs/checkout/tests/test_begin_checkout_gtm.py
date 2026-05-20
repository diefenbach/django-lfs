from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from lfs.cart.models import Cart, CartItem
from lfs.catalog.models import Product
from lfs.core.models import Country
from lfs.core.utils import get_default_shop
from lfs.customer.models import Customer
from lfs.addresses.models import Address
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import BY_INVOICE
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax


class BeginCheckoutTrackingTestCase(TestCase):
    fixtures = ["lfs_shop.xml"]

    def setUp(self):
        ie = Country.objects.get(code="ie")
        us = Country.objects.get(code="us")

        shop = get_default_shop()
        for country in Country.objects.all():
            shop.invoice_countries.add(country)
        shop.save()

        tax = Tax.objects.create(rate=19)
        shipping_method = ShippingMethod.objects.create(name="Standard", active=True, price=1.0, tax=tax)
        self.by_invoice = PaymentMethod.objects.get(pk=BY_INVOICE)

        address1 = Address.objects.create(
            firstname="John",
            lastname="Doe",
            line1="Street 42",
            city="Gotham City",
            zip_code="2342",
            country=ie,
        )
        address2 = Address.objects.create(
            firstname="Jane",
            lastname="Doe",
            line1="Street 43",
            city="Smallville",
            zip_code="2443",
            country=us,
        )

        user = User.objects.create_user(username="checkout@test.com", email="checkout@test.com")
        user.set_password("secret")
        user.save()

        self.customer = Customer.objects.create(
            user=user,
            selected_shipping_method=shipping_method,
            selected_payment_method=self.by_invoice,
            selected_shipping_address=address1,
            selected_invoice_address=address2,
            default_shipping_address=address1,
            default_invoice_address=address2,
        )

        p1 = Product.objects.create(
            name="Product 1",
            slug="product-1",
            price=10.0,
            active=True,
            deliverable=True,
        )

        self.client = Client()
        self.client.login(username="checkout@test.com", password="secret")

        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=p1, amount=1)

    def test_addresses_get_renders_begin_checkout_from_session(self):
        session = self.client.session
        session["begin_checkout_tracking"] = {
            "currency": "EUR",
            "value": 10.0,
            "line_items": [{"sku": "sku-1", "name": "Product 1", "price": 10.0, "quantity": 1}],
        }
        session.save()

        with override_settings(GTM_ID="GTM-TEST"):
            response = self.client.get(reverse("lfs_checkout_addresses"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('id="begin-checkout-event"', content)
        self.assertIn("begin_checkout", content)
        self.assertNotIn("begin_checkout_tracking", self.client.session)

    def test_addresses_post_does_not_render_begin_checkout(self):
        session = self.client.session
        session["begin_checkout_tracking"] = {
            "currency": "EUR",
            "value": 10.0,
            "line_items": [{"sku": "sku-1", "name": "Product 1", "price": 10.0, "quantity": 1}],
        }
        session.save()

        with override_settings(GTM_ID="GTM-TEST"):
            response = self.client.post(
                reverse("lfs_checkout_addresses"),
                {
                    "invoice-firstname": "John",
                    "invoice-lastname": "Doe",
                    "invoice-line1": "Street 42",
                    "invoice-city": "Gotham City",
                    "invoice-zip_code": "2342",
                    "invoice-country": "ie",
                    "invoice-email": "checkout@test.com",
                },
            )

        if response.status_code == 200:
            self.assertNotIn("begin-checkout-event", response.content.decode())

    def test_checkout_dispatcher_stores_begin_checkout_tracking(self):
        response = self.client.get(reverse("lfs_checkout_dispatcher"))

        self.assertEqual(response.status_code, 302)
        tracking = self.client.session.get("begin_checkout_tracking")
        self.assertIsNotNone(tracking)
        self.assertEqual(tracking["currency"], "EUR")
        self.assertNotIn("event", tracking)
