import os
import datetime

from django.conf import settings
from windmill.authoring import djangotest 


class TestProjectWindmillTest(djangotest.WindmillDjangoUnitTest): 
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'windmilltests')
    browser = 'chrome'
    settings.TESTING = True
    
    def setUp(self):
        # set up our shop here
        super(TestProjectWindmillTest, self).setUp()
        
    def tearDown(self):
        # test for changes to shop here
        pass
