import os
import datetime

from django.conf import settings
from windmill.authoring import djangotest

from lfs.core.models import Shop
from lfs.catalog.models import Product


class CartPriceIntegrationTest(djangotest.WindmillDjangoUnitTest):
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'windmilltests', 'grosspricetests')
    browser = 'chrome'
    settings.TESTING = True
    # We need to set DEBUG = True so that our static content gets server
    settings.DEBUG = True
    fixtures = ['lfs_price_test.xml']

    def setUp(self):
        # Our data is loaded from fixtures
        self.assertEqual(1, Shop.objects.count())

        # Check that apple is using GrossPriceCalculator
        apple = Product.objects.get(slug='apple')
        self.assertEqual('lfs.net_price.NetPriceCalculator', apple.price_calculator)

        # Check that chocolate is using NetPriceCalculator
        chocolate = Product.objects.get(slug='chocolate')
        self.assertEqual('lfs.gross_price.GrossPriceCalculator', chocolate.price_calculator)

        super(CartPriceIntegrationTest, self).setUp()

    def tearDown(self):
        # check for new objects in database
        pass


class ManageInterfaceIntegrationTest(djangotest.WindmillDjangoUnitTest):
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'windmilltests', 'managetests')
    browser = 'chrome'
    settings.TESTING = True
    # We need to set DEBUG = True so that our static content gets server
    settings.DEBUG = True
    fixtures = ['lfs_price_test.xml']

    def setUp(self):
        # Our data is loaded from fixtures
        self.assertEqual(1, Shop.objects.count())

        # Check that apple is using GrossPriceCalculator
        apple = Product.objects.get(slug='apple')
        self.assertEqual('lfs.net_price.NetPriceCalculator', apple.price_calculator)

        super(ManageInterfaceIntegrationTest, self).setUp()

    def tearDown(self):
        # check for new objects in database
        pass
