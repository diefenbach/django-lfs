# django imports
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from lfs.catalog.models import Category

from lfs.manage.api.handlers import CategorySortView


class ManageTestCase(TestCase):
    """Tests manage interface
    """
    def setUp(self):
        for i in range(1, 4):
            cat, created = Category.objects.get_or_create(pk=i, name="cat" + str(i), slug="cat" + str(i), position=10, parent=None)

        self.client = Client()

    def test_category_sorting(self):
        """
        Test we get correct sorting of categories from json api
        """

        self.assertEqual(3, Category.objects.count())
        csv = CategorySortView()

        js = 'category[3]=root&category[1]=root&category[2]=1'
        csv.sort_categories(js)
        cat1 = Category.objects.get(pk=1)
        cat2 = Category.objects.get(pk=2)
        cat3 = Category.objects.get(pk=3)

        # check positions are correct
        self.assertEqual(cat1.position, 20)
        self.assertEqual(cat2.position, 30)
        self.assertEqual(cat3.position, 10)

        # check parents are correct
        self.assertEqual(cat1.parent, None)
        self.assertEqual(cat2.parent, cat1)
        self.assertEqual(cat3.parent, None)

        js = 'category[1]=root&category[2]=root&category[3]=2'
        csv.sort_categories(js)
        cat1 = Category.objects.get(pk=1)
        cat2 = Category.objects.get(pk=2)
        cat3 = Category.objects.get(pk=3)

        # check positions are correct
        self.assertEqual(cat1.position, 10)
        self.assertEqual(cat2.position, 20)
        self.assertEqual(cat3.position, 30)

        # check parents are correct
        self.assertEqual(cat1.parent, None)
        self.assertEqual(cat2.parent, None)
        self.assertEqual(cat3.parent, cat2)
