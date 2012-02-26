# django imports
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser

# test imports
from lfs.tests.utils import DummyRequest

# lfs imports
from lfs.catalog.settings import DELIVERY_TIME_UNIT_DAYS
from lfs.catalog.models import DeliveryTime
from lfs.catalog.models import Product
from lfs.customer import utils as customer_utils
from lfs.shipping.models import ShippingMethod
from lfs.shipping.models import ShippingMethodPrice
from lfs.shipping import utils
from lfs.criteria.models import UserCriterion
from lfs.criteria.models import CriteriaObjects
from lfs.criteria.models import CartPriceCriterion
from lfs.criteria.models import WeightCriterion
from lfs.criteria.settings import GREATER_THAN, LESS_THAN
from lfs.cart import utils as cart_utils
from lfs.cart.models import CartItem
from lfs.caching.listeners import update_cart_cache
from lfs.tests.utils import create_request


class ShippingMethodTestCase(TestCase):
    """Unit tests for lfs.shipping
    """
    fixtures = ['lfs_shop.xml', "lfs_user.xml"]

    def setUp(self):
        """
        """
        self.client.login(username="admin", password="admin")

        self.user = User.objects.get(username="admin")
        self.request = DummyRequest(user=self.user)

        # Create delivery times
        self.dt1 = DeliveryTime.objects.create(min=3, max=4, unit=DELIVERY_TIME_UNIT_DAYS)
        self.dt2 = DeliveryTime.objects.create(min=1, max=2, unit=DELIVERY_TIME_UNIT_DAYS)
        self.dt3 = DeliveryTime.objects.create(min=5, max=6, unit=DELIVERY_TIME_UNIT_DAYS)

        self.sm1 = ShippingMethod.objects.create(name="Standard", active=True, price=1, delivery_time=self.dt1, priority=1)
        self.sm2 = ShippingMethod.objects.create(name="Express", active=True, delivery_time=self.dt2, priority=2)

        self.p1 = Product.objects.create(name="Product 1", slug="p1", price=9, weight=6.0)
        self.p2 = Product.objects.create(name="Product 2", slug="p2", price=11, weight=12.0)

        # Delete the cart for every test method.
        cart = cart_utils.get_cart(self.request)
        if cart:
            cart.delete()

    def test_get_product_delivery_time_1(self):
        """Tests the product delivery time for the *product view*.
        """
        request = create_request()
        request.user = AnonymousUser()

        customer = customer_utils.get_or_create_customer(request)
        customer.selected_shipping_method = self.sm1
        customer.save()

        # We select a explicitely shipping method for the customer. For the
        # product view this shouldn't make a difference. It should always the
        # first valid shipping method be taken to display the delivery time.
        customer.selected_shipping_method = self.sm2
        customer.save()

        # Create a weigth criterion and add it to the shipping method 1.
        c = WeightCriterion.objects.create(weight=10.0, operator=GREATER_THAN)
        co = CriteriaObjects(criterion=c, content=self.sm1)
        co.save()

        # Now we ask for the delivery time for product 1. As sm1 is not valid
        # (p1 has an weight of 6.0) we should get the delivery time from sm2,
        # which is dt2
        dt = utils.get_product_delivery_time(request, self.p1.slug)
        self.assertEqual(dt.min, self.dt2.min)
        self.assertEqual(dt.max, self.dt2.max)
        self.assertEqual(dt.unit, self.dt2.unit)

        # For product 2 sm1 is valid (p2 has an weight of 11.0), hence we should
        # get dt1.
        dt = utils.get_product_delivery_time(request, self.p2.slug)
        self.assertEqual(dt.min, self.dt1.min)
        self.assertEqual(dt.max, self.dt1.max)
        self.assertEqual(dt.unit, self.dt1.unit)

        # Now we switch to manual delivery time
        self.p1.manual_delivery_time = True
        self.p1.delivery_time = self.dt3
        self.p1.save()

        dt = utils.get_product_delivery_time(request, self.p1.slug)
        self.assertEqual(dt.min, self.dt3.min)
        self.assertEqual(dt.max, self.dt3.max)
        self.assertEqual(dt.unit, self.dt3.unit)

    def test_get_product_delivery_time_2(self):
        """Tests the product delivery time for the *cart view*.
        """
        request = create_request()
        request.user = AnonymousUser()

        customer = customer_utils.get_or_create_customer(request)
        customer.selected_shipping_method = self.sm1
        customer.save()

        dt = utils.get_product_delivery_time(request, self.p1.slug, for_cart=True)
        self.assertEqual(dt.min, self.dt1.min)
        self.assertEqual(dt.max, self.dt1.max)
        self.assertEqual(dt.unit, self.dt1.unit)

        dt = utils.get_product_delivery_time(request, self.p2.slug, for_cart=True)
        self.assertEqual(dt.min, self.dt1.min)
        self.assertEqual(dt.max, self.dt1.max)
        self.assertEqual(dt.unit, self.dt1.unit)

        customer.selected_shipping_method = self.sm2
        customer.save()

        # As the customer has now selected sm2 explicitely the delivery method
        # for the products is dt2 although the default shipping method is
        # sm1.
        dt = utils.get_product_delivery_time(request, self.p1.slug, for_cart=True)
        self.assertEqual(dt.min, self.dt2.min)
        self.assertEqual(dt.max, self.dt2.max)
        self.assertEqual(dt.unit, self.dt2.unit)

        # For product 2 sm1 is valid, hence we should get dt1
        dt = utils.get_product_delivery_time(request, self.p2.slug, for_cart=True)
        self.assertEqual(dt.min, self.dt2.min)
        self.assertEqual(dt.max, self.dt2.max)
        self.assertEqual(dt.unit, self.dt2.unit)

        # Create a weigth criterion and add it to the shipping method 1. That
        # means sm1 is not valid anymore for p1.
        c = WeightCriterion.objects.create(weight=10.0, operator=GREATER_THAN)
        co = CriteriaObjects(criterion=c, content=self.sm1)
        co.save()

        # And even if the customer select sm1 explicitely ...
        customer.selected_shipping_method = self.sm1
        customer.save()

        # ... the shipping method for p1 is sm2 and hence the delivery time is
        # dt1
        dt = utils.get_product_delivery_time(request, self.p1.slug, for_cart=True)
        self.assertEqual(dt.min, self.dt2.min)
        self.assertEqual(dt.max, self.dt2.max)
        self.assertEqual(dt.unit, self.dt2.unit)

    def test_active_shipping_methods_1(self):
        """Tests active shipping methods.
        """
        # At start we have two active shipping methods, see above.
        sm = ShippingMethod.objects.active()
        self.assertEqual(len(sm), 2)

        # Now we deactivate one.
        self.sm1.active = False
        self.sm1.save()
        sm = ShippingMethod.objects.active()
        self.assertEqual(len(sm), 1)

        # Now we deactivate the other one.
        self.sm2.active = False
        self.sm2.save()
        sm = ShippingMethod.objects.active()
        self.assertEqual(len(sm), 0)

    def test_valid_shipping_methods_1(self):
        """Tests valid shipping methods.
        """
        # Add the a user criterion with the current user to the shipping method.
        c = UserCriterion.objects.create()
        c.users = (self.user, )
        c.save()

        co = CriteriaObjects.objects.create(criterion=c, content=self.sm1)

        # And its still valid.
        sms = utils.get_valid_shipping_methods(self.request)
        self.assertEqual(len(sms), 2)

        # Tests that the correct shipping methods are returned
        sm_names = [sm.name for sm in sms]
        self.failUnless("Standard" in sm_names)
        self.failUnless("Express" in sm_names)

        # We now ``logout``
        self.request.user = None

        # And the shipping method is not valid any more.
        sms = utils.get_valid_shipping_methods(self.request)
        self.assertEqual(len(sms), 1)

        # Tests that the correct shipping methods are returned
        sm_names = [sm.name for sm in sms]
        self.failUnless("Express" in sm_names)

    def test_valid_shipping_methods_2(self):
        """Tests valid shipping methods. Test with a cart price criterion.
        """
        user = User.objects.get(username="admin")
        request = DummyRequest(user=user)

        # Create a cart price criterion and add it to the shipping method 1
        c = CartPriceCriterion.objects.create(price=10.0, operator=GREATER_THAN)
        co = CriteriaObjects(criterion=c, content=self.sm1)
        co.save()

        # Cart price is 0.0 sms1 is not valid
        sms = utils.get_valid_shipping_methods(request)
        self.assertEqual(len(sms), 1)

        # Add some products to the cart
        cart = cart_utils.create_cart(request)

        # Cart price is still under 10 - sms1 is not valid
        CartItem.objects.create(cart=cart, product=self.p1, amount=1)
        update_cart_cache(cart)

        sms = utils.get_valid_shipping_methods(request)
        self.assertEqual(len(sms), 1)

        # Cart price is greater than 10.0 now - sms1 is valid
        CartItem.objects.create(cart=cart, product=self.p2, amount=1)
        update_cart_cache(cart)

        sms = utils.get_valid_shipping_methods(request)
        self.assertEqual(len(sms), 2)

    def test_valid_shipping_methods_3(self):
        """Test with a given product.
        """
        # Prepare request
        user = User.objects.get(username="admin")
        request = DummyRequest(user=user)

        # Create a weigth criterion and add it to the shipping method 1.
        c = WeightCriterion.objects.create(weight=10.0, operator=GREATER_THAN)
        co = CriteriaObjects(criterion=c, content=self.sm1)
        co.save()

        # As the product has a weigth of 6.0 the shipping method is not valid
        result = c.is_valid(request, product=self.p1)
        self.assertEqual(result, False)

        # As product 2 has a weigth of 12.0 the shipping method is valid
        result = c.is_valid(request, product=self.p1)
        self.assertEqual(result, False)

    def test_get_first_valid_shipping_method(self):
        """Test utils.get_first_valid_shipping_method
        """
        # Prepare request
        user = User.objects.get(username="admin")
        request = DummyRequest(user=user)

        # Create a weigth criterion and add it to the shipping method 1.
        c = WeightCriterion.objects.create(weight=5.0, operator=GREATER_THAN)
        c = WeightCriterion.objects.create(weight=10.0, operator=LESS_THAN)
        co = CriteriaObjects(criterion=c, content=self.sm1)
        co.save()

        # Create a weigth criterion and add it to the shipping method 2.
        c = WeightCriterion.objects.create(weight=10.0, operator=GREATER_THAN)
        co = CriteriaObjects(criterion=c, content=self.sm2)
        co.save()

        # For product 1 (weight: 6.0) the sm1 is the first valid (weight: 5.0 - 10.0)
        result = utils.get_first_valid_shipping_method(request, product=self.p1)
        self.assertEqual(result, self.sm1)

        # For product 1 (weight: 12.0) the sm1 is the first valid (weigth: > 10.0)
        result = utils.get_first_valid_shipping_method(request, product=self.p2)
        self.assertEqual(result, self.sm2)

    def test_shipping_price_1(self):
        """Tests the default shipping price of the shipping method.
        """
        # There are no shipping prices, hence the default shipping price is
        # returned, which is 1, see above.
        costs = utils.get_shipping_costs(self.request, self.sm1)
        self.assertEqual(costs.get("price"), 1)

    def test_shipping_price_2(self):
        """Tests an additional shipping method price.
        """
        # Add a shipping method price
        smp = ShippingMethodPrice.objects.create(shipping_method=self.sm1, price=5)

        # As this has no criteria it is valid by default
        costs = utils.get_shipping_costs(self.request, self.sm1)
        self.assertEqual(costs["price"], 5)

    def test_shipping_price_3(self):
        """Tests an additional shipping method price with a criterion.
        """
        # Add a shipping method price
        smp = ShippingMethodPrice.objects.create(shipping_method=self.sm1, price=5)

        # Add a criterion the to the price
        c = CartPriceCriterion.objects.create(price=10.0, operator=GREATER_THAN)
        co = CriteriaObjects.objects.create(criterion=c, content=smp)

        # The cart price is less than 10, hence the price is not valid and the
        # shipping price is the default price of the shipping method , which is
        # 1, see above.
        costs = utils.get_shipping_costs(self.request, self.sm1)
        self.assertEqual(costs["price"], 1)

        # No we add some items to the cart
        cart = cart_utils.get_or_create_cart(self.request)
        CartItem.objects.create(cart=cart, product=self.p1, amount=2)
        update_cart_cache(cart)

        # The cart price is now greater than 10, hence the price valid and the
        # shipping price is the price of the yet valid additional price.
        costs = utils.get_shipping_costs(self.request, self.sm1)
        self.assertEqual(costs["price"], 5)
