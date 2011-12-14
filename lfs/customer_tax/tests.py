# django imports
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

# test imports
from lfs.tests.utils import create_request

# lfs imports
from lfs.catalog.models import Product
from lfs.core.models import Country
from lfs.customer_tax.models import CustomerTax
from lfs.customer_tax.utils import get_customer_tax_rate
from lfs.customer.utils import get_or_create_customer

class CustomerTaxTestCase(TestCase):
    """Unit tests for lfs.customer_tax
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        self.us = Country.objects.create(code="us", name="USA")
        self.ch = Country.objects.create(code="ch", name="Switzerland")
        self.de = Country.objects.create(code="de", name="Germany")
        self.ie = Country.objects.create(code="ie", name="Ireland")

        self.product = Product.objects.create(name="P1", slug="p1", price=100.0)

        self.request = create_request()
        self.request.user = AnonymousUser()
        self.customer = get_or_create_customer(self.request)

        self.ct1 = CustomerTax.objects.create(rate = 20.0)
        self.ct1.countries.add(self.ch)
        self.ct1.countries.add(self.us)

        self.ct2 = CustomerTax.objects.create(rate = 10.0)
        self.ct2.countries.add(self.ie)

    def test_customer_tax(self):
        self.assertEqual(self.ct1.rate, 20.0)
        self.assertEqual(list(self.ct1.countries.all()), [self.ch, self.us])

        self.assertEqual(self.ct2.rate, 10.0)
        self.assertEqual(list(self.ct2.countries.all()), [self.ie])

    def test_get_customer_tax_rate(self):
        self.customer.selected_shipping_address.country = self.us
        self.customer.selected_shipping_address.save()
        result = get_customer_tax_rate(self.request, self.product)
        self.assertEqual(result, 20.0)

        self.customer.selected_shipping_address.country = self.ch
        self.customer.selected_shipping_address.save()
        result = get_customer_tax_rate(self.request, self.product)
        self.assertEqual(result, 20.0)

        self.customer.selected_shipping_address.country = self.ie
        self.customer.selected_shipping_address.save()
        result = get_customer_tax_rate(self.request, self.product)
        self.assertEqual(result, 10.0)

        self.customer.selected_shipping_address.country = self.de
        self.customer.selected_shipping_address.save()
        result = get_customer_tax_rate(self.request, self.product)
        self.assertEqual(result, 0.0)
