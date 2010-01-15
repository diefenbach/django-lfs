from django.test import TestCase

from lfs.core.models import Country
from lfs.addresses.views import get_l10n, NUM_ADDRESS_LINES

class AddressWidgetTest(TestCase):
    
    def test_get_de_address(self):
        """
        Tests that we get the correct widget for Germany
        """
        l10n_obj = get_l10n("de")
        self.assertNotEqual(l10n_obj, None)
        
        ie_address_fields = l10n_obj.get_address_fields()
        self.assertEqual(len(ie_address_fields), NUM_ADDRESS_LINES)
        
        self.assertEqual(ie_address_fields[0].label, "Company name")
        self.assertEqual(ie_address_fields[1].label, "Street")
        self.assertEqual(ie_address_fields[2].label, "Zip Code")
        self.assertEqual(ie_address_fields[3].label, "City")
        self.assertEqual(ie_address_fields[4].label, "State")
    
    def test_get_ie_address(self):
        """
        Tests that we get the correct widget for Ireland
        """
        l10n_obj = get_l10n("ie")
        self.assertNotEqual(l10n_obj, None)
        
        ie_address_fields = l10n_obj.get_address_fields()
        self.assertEqual(len(ie_address_fields), NUM_ADDRESS_LINES)
        
        self.assertEqual(ie_address_fields[0].label, "Address 1")
        self.assertEqual(ie_address_fields[1].label, "Address 2")
        self.assertEqual(ie_address_fields[2].label, "Address 3")
        self.assertEqual(ie_address_fields[3].label, "Town")
        self.assertEqual(ie_address_fields[4].label, "County")
    
    
    def test_incorrect_country_code(self):
        """
        Tests that we don't throw an exception for an incorrect country code
        """
        l10n_obj = get_l10n("xx")
        self.assertNotEqual(l10n_obj, None)
        
        ie_address_fields = l10n_obj.get_address_fields()
        self.assertEqual(len(ie_address_fields), NUM_ADDRESS_LINES)
        
        self.assertEqual(ie_address_fields[0].label, "Company name")
        self.assertEqual(ie_address_fields[1].label, "Street")
        self.assertEqual(ie_address_fields[2].label, "Zip Code")
        self.assertEqual(ie_address_fields[3].label, "City")
        self.assertEqual(ie_address_fields[4].label, "State")
    
    
    def test_get_default(self):
        """
        Tests that we don't throw an exception for an incorrect country code
        """
        l10n_obj = get_l10n("nocountryforoldmen")
        self.assertNotEqual(l10n_obj, None)
        
        ie_address_fields = l10n_obj.get_address_fields()
        self.assertEqual(len(ie_address_fields), NUM_ADDRESS_LINES)
        
        self.assertEqual(ie_address_fields[0].label, "Company name")
        self.assertEqual(ie_address_fields[1].label, "Street")
        self.assertEqual(ie_address_fields[2].label, "Zip Code")
        self.assertEqual(ie_address_fields[3].label, "City")
        self.assertEqual(ie_address_fields[4].label, "State")
    
        