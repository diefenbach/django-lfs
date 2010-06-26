# django imports
from django.core.urlresolvers import reverse
from django.test import TestCase

# test imports
from lfs.catalog.models import Product

class SearchTestCase(TestCase):
    """Unit tests for lfs.search
    """
    fixtures = ['lfs_shop.xml']
    
    def setUp(self):
        """
        """
        self.p1 = Product.objects.create(name="Product 1", slug="p1", price=9, active=True)
        self.p2 = Product.objects.create(name="Product 2", slug="p2", price=11, active=True)

    def test_search(self):
        """
        """
        url = reverse("lfs_search")
        
        # Must be found
        response = self.client.get(url, {"q" : "Product"})
        self.failIf(response.content.find("Product 1") == -1)

        # Must not be found
        response = self.client.get(url, {"q" : "Hurz"})
        self.failIf(response.content.find("Product 1") != -1)