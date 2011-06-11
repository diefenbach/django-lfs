# django imports
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

# test imports
from lfs.tests.utils import create_request
from lfs.tests.utils import DummyRequest

# lfs imports
import lfs.cart.utils
from lfs.catalog.models import Product
from lfs.criteria.models import WeightCriterion
from lfs.criteria.models import CriteriaObjects
from lfs.criteria.settings import GREATER_THAN, LESS_THAN
from lfs.discounts.models import Discount


class DiscountsTestCase(TestCase):
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
