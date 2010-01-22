"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

class AddressWidgetTest(TestCase):
    def test_get_ireland(self):
        """
        Tests that we get the correct widget for Ireland
        """
        pass
    
    
    def test_incorrect_country_code(self):
        """
        Tests that we don't throw an exception for an incorrect country code
        """
        pass
    
    
    def test_get_default(self):
        """
        Tests that we don't throw an exception for an incorrect country code
        """
        pass
        