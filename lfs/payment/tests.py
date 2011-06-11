# django imports
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

# lfs imports
from lfs.core.models import Country
from lfs.order.models import Order
from lfs.order.settings import PAID, PAYMENT_FAILED, PAYMENT_FLAGGED, SUBMITTED
from lfs.payment.models import PayPalOrderTransaction
from lfs.payment.utils import get_paypal_link_for_order

# other imports
from paypal.standard.ipn.models import PayPalIPN
from paypal.standard.models import ST_PP_COMPLETED, ST_PP_DENIED
import uuid


class PayPalPaymentTestCase(TestCase):
    """Tests paypal payments
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):

        self.uuid = "981242b5-fb0c-4563-bccb-e03033673d2a"
        self.IPN_POST_PARAMS = {
            "protection_eligibility": "Ineligible",
            "last_name": "User",
            "txn_id": "51403485VH153354B",
            "receiver_email": settings.PAYPAL_RECEIVER_EMAIL,
            "payment_status": ST_PP_COMPLETED,
            "payment_gross": "10.00",
            "tax": "0.00",
            "residence_country": "US",
            "invoice": "0004",
            "payer_status": "verified",
            "txn_type": "express_checkout",
            "handling_amount": "0.00",
            "payment_date": "23:04:06 Feb 02, 2009 PST",
            "first_name": "Test",
            "item_name": "Something from the shop",
            "charset": "windows-1252",
            "custom": self.uuid,
            "notify_version": "2.6",
            "transaction_subject": "",
            "test_ipn": "1",
            "item_number": "1",
            "receiver_id": "258DLEHY2BDK6",
            "payer_id": "BN5JZ2V7MLEV4",
            "verify_sign": "An5ns1Kso7MWUdW4ErQKJJJ4qi4-AqdZy6dD.sGO3sDhTf1wAbuO2IZ7",
            "payment_fee": "0.59",
            "mc_fee": "0.59",
            "mc_currency": "USD",
            "shipping": "0.00",
            "payer_email": "bishan_1233269544_per@gmail.com",
            "payment_type": "instant",
            "mc_gross": "10.00",
            "quantity": "1",
        }

        # Every test needs a client.
        self.client = Client()

    def test_successful_order_transaction_created(self):
        """Tests we have a transaction associated with an order after payment
        """
        def fake_postback(self, test=True):
            """Perform a Fake PayPal IPN Postback request."""
            return 'VERIFIED'

        PayPalIPN._postback = fake_postback

        country = Country.objects.get(code="ie")
        order = Order(invoice_country=country, shipping_country=country, uuid=self.uuid)
        self.assertEqual(order.state, SUBMITTED)
        order.save()
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalOrderTransaction.objects.all()), 0)
        post_params = self.IPN_POST_PARAMS
        response = self.client.post(reverse('paypal-ipn'), post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        self.assertEqual(len(PayPalOrderTransaction.objects.all()), 1)
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.flag, False)
        order = Order.objects.all()[0]
        self.assertEqual(order.state, PAID)

    def test_failed_order_transaction_created(self):
        """Tests a failed paypal transaction
        """
        def fake_postback(self, test=True):
            """Perform a Fake PayPal IPN Postback request."""
            return 'INVALID'

        PayPalIPN._postback = fake_postback

        country = Country.objects.get(code="ie")
        order = Order(invoice_country=country, shipping_country=country, uuid=self.uuid)
        self.assertEqual(order.state, SUBMITTED)
        order.save()
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalOrderTransaction.objects.all()), 0)
        post_params = self.IPN_POST_PARAMS
        payment_status_update = {"payment_status": ST_PP_DENIED}
        post_params.update(payment_status_update)
        response = self.client.post(reverse('paypal-ipn'), post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        self.assertEqual(len(PayPalOrderTransaction.objects.all()), 1)
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.payment_status, ST_PP_DENIED)
        self.assertEqual(ipn_obj.flag, True)
        order = Order.objects.all()[0]
        self.assertEqual(order.state, PAYMENT_FAILED)

    def test_succesful_order_with_flagged_payment_invalid_receiver_email(self):
        """Tests a succesful paypal transaction that is flagged with an invalide receiver email
        """
        def fake_postback(self, test=True):
            """Perform a Fake PayPal IPN Postback request."""
            return 'VERIFIED'

        PayPalIPN._postback = fake_postback
        country = Country.objects.get(code="ie")
        order = Order(invoice_country=country, shipping_country=country, uuid=self.uuid)
        self.assertEqual(order.state, SUBMITTED)
        order.save()
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalOrderTransaction.objects.all()), 0)
        post_params = self.IPN_POST_PARAMS
        incorrect_receiver_email_update = {"receiver_email": "incorrect_email@someotherbusiness.com"}
        post_params.update(incorrect_receiver_email_update)
        response = self.client.post(reverse('paypal-ipn'), post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        self.assertEqual(len(PayPalOrderTransaction.objects.all()), 1)
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.payment_status, ST_PP_COMPLETED)
        self.assertEqual(ipn_obj.flag, True)
        self.assertEqual(ipn_obj.flag_info, u'Invalid receiver_email. (incorrect_email@someotherbusiness.com)')
        order = Order.objects.all()[0]
        self.assertEqual(order.state, PAYMENT_FLAGGED)

    def test_correct_address_fields_set_on_checkout(self):
        country = Country.objects.get(code="us")
        order = Order(invoice_firstname="bill", invoice_lastname="blah",
                      invoice_line1="bills house", invoice_line2="bills street",
                      invoice_city="bills town", invoice_state="bills state",
                      invoice_code="bills zip code", invoice_country=country,
                      shipping_country=country, uuid=self.uuid)
        self.assertEqual(order.state, SUBMITTED)
        order.save()
        url = get_paypal_link_for_order(order)

        # test unique id
        self.assertEqual(('custom=' + self.uuid) in url, True)

        # test address stuff
        self.assertEqual('first_name=bill' in url, True)
        self.assertEqual('last_name=blah' in url, True)
        self.assertEqual('address1=bills house' in url, True)
        self.assertEqual('address2=bills street' in url, True)
        self.assertEqual('state=bills state' in url, True)
        self.assertEqual('zip=bills zip code' in url, True)
