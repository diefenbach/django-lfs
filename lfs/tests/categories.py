from django.test import TestCase
from lfs.catalog.models import Category


class CategoriesTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        self.client.login(username="admin", password="admin")

        # Create a simple category structure
        category_1 = Category(name="Category 1", slug="category-1")
        category_1.save()

        category_2 = Category(name="Category 2", slug="category-2")
        category_2.save()

        category_1_1 = Category(name="Category 1-1", slug="category-1-1", parent=category_1)
        category_1_1.save()

        category_1_1_1 = Category(name="Category 1-1-1", slug="category-1-1-1", parent=category_1_1)
        category_1_1_1.save()

    def test_category_creation(self):
        """Has the above categories been created properly.
        """
        self.assertEqual(len(Category.objects.all()), 4)
