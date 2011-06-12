import os
import datetime

from django.conf import settings
from windmill.authoring import djangotest


class TestProjectWindmillTest(djangotest.WindmillDjangoUnitTest):
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'windmilltests')
    browser = 'chrome'
    settings.TESTING = True
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        # check that object counts are at zero
        super(TestProjectWindmillTest, self).setUp()

    def tearDown(self):
        # check for new objects in database
        pass
