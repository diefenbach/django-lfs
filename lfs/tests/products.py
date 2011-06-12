# django imports
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

# test imports
from lfs.tests.utils import DummyRequest

# lfs imports
from lfs.catalog.models import Product
from lfs.catalog.models import Category


class ProductsTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        self.client.login(username="admin", password="admin")

        for i in range(0, 10):
            product = Product(
                name="Product %s" % i,
                slug="product-%s" % i,
                description="This is the description %s" % i,
                price=i
            )
            product.save()

        c1 = Category(name="Category 1", slug="category-1")
        c1.save()

        c11 = Category(name="Category 1-1", slug="category-1-1", parent=c1)
        c11.save()

        c111 = Category(name="Category 1-1-1", slug="category-1-1-1", parent=c11)
        c111.save()

        # Assign products
        product = Product.objects.get(slug="product-1")
        c111.products = (product, )

    def test_created_products(self):
        """
        """
        for i in range(0, 10):
            p = Product.objects.get(slug="product-%s" % i)
            self.assertEqual(p.name, "Product %s" % i)
            self.assertEqual(p.price, i)
            self.assertEqual(p.description, "This is the description %s" % i)

    def test_categories(self):
        """
        """
        product = Product.objects.get(slug="product-1")
        category_slugs = [c.slug for c in product.get_categories()]

        self.assertEqual(category_slugs, ["category-1-1-1"])

    def test_categories_with_parents(self):
        """
        """
        product = Product.objects.get(slug="product-1")
        category_slugs = [c.slug for c in product.get_categories(with_parents=True)]

        self.assertEqual(category_slugs, ["category-1-1-1", "category-1-1", "category-1"])
