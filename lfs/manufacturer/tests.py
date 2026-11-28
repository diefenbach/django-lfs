# coding: utf-8
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from lfs.catalog.models import Product, Category
from lfs.manufacturer.models import Manufacturer


class ManufacturersTestCase(TestCase):
    fixtures = ["lfs_shop.xml"]

    def setUp(self):
        """ """
        self.p1 = Product.objects.create(slug="product-1", price=5, active=True)
        self.p2 = Product.objects.create(slug="product-2", price=3, active=True)
        self.p3 = Product.objects.create(slug="product-3", price=1, active=True)

        self.c1 = Category.objects.create(name="Category 1", slug="category-1")
        self.c1.products.set([self.p1, self.p2, self.p3])
        self.c1.save()
        self.m1 = Manufacturer.objects.create(
            name="LFS C.O.", slug="lfs-co", short_description="sd", description="desc", position=1
        )

        # set up a user with permission to access the manage interface
        self.user, created = User.objects.get_or_create(username="manager", is_superuser=True)
        self.password = "pass"
        self.user.set_password(self.password)
        self.user.save()

    def test_manufacturers_page(self):
        """Test if page showing all manufacturers works"""
        url = reverse("lfs_manufacturers")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["manufacturers"]), 1)

    def test_manufacturer_page(self):
        """Test if page showing manufacturer details works"""
        url = reverse("lfs_manufacturer", kwargs={"slug": self.m1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_manufacturer_breadcrumbs(self):
        """If the product is visited from the manufacturer page, then manufacturer should be visible in breadcrumbs.
        If the product is visited from the category page, then category should be visible in breadcrumbs.
        If the product is visited directly, then
        """
        self.p1.manufacturer = self.m1
        self.p1.save()

        # direct visit
        url = reverse("lfs_product", kwargs={"slug": self.p1.slug})
        response = self.client.get(url)
        self.assertContains(response, self.c1.name)

        # visit from the manufacturer's page
        # first go to manufacturer page
        url = reverse("lfs_manufacturer", kwargs={"slug": self.m1.slug})
        self.client.get(url)
        # then visit the product
        url = reverse("lfs_product", kwargs={"slug": self.p1.slug})
        response = self.client.get(url)
        self.assertContains(response, self.m1.name)

        # visit from the category's page - resets manufacturer
        # first go to category page
        url = reverse("lfs_category", kwargs={"slug": self.c1.slug})
        self.client.get(url)
        # then visit the product
        url = reverse("lfs_product", kwargs={"slug": self.p1.slug})
        response = self.client.get(url)
        self.assertContains(response, self.c1.name)
