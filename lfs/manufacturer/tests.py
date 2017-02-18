# coding: utf-8
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from lfs.catalog.models import Product, Category
from lfs.manufacturer.models import Manufacturer


class ManufacturersTestCase(TestCase):
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        self.p1 = Product.objects.create(slug="product-1", price=5, active=True)
        self.p2 = Product.objects.create(slug="product-2", price=3, active=True)
        self.p3 = Product.objects.create(slug="product-3", price=1, active=True)

        self.c1 = Category.objects.create(name="Category 1", slug="category-1")
        self.c1.products = [self.p1, self.p2, self.p3]
        self.c1.save()
        self.m1 = Manufacturer.objects.create(name='LFS C.O.', slug='lfs-co', short_description='sd',
                                              description='desc', position=1)

        # set up a user with permission to access the manage interface
        self.user, created = User.objects.get_or_create(username='manager', is_superuser=True)
        self.password = 'pass'
        self.user.set_password(self.password)
        self.user.save()

    def test_manufacturers_page(self):
        """ Test if page showing all manufacturers works
        """
        url = reverse("lfs_manufacturers")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['manufacturers']), 1)

    def test_manufacturer_page(self):
        """ Test if page showing manufacturer details works
        """
        url = reverse("lfs_manufacturer", kwargs={'slug': self.m1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_manufacturer_breadcrumbs(self):
        """ If the product is visited from the manufacturer page, then manufacturer should be visible in breadcrumbs.
            If the product is visited from the category page, then category should be visible in breadcrumbs.
            If the product is visited directly, then
        """
        self.p1.manufacturer = self.m1
        self.p1.save()

        # direct visit
        url = reverse("lfs_product", kwargs={'slug': self.p1.slug})
        response = self.client.get(url)
        self.assertContains(response, self.c1.name)

        # visit from the manufacturer's page
        # first go to manufacturer page
        url = reverse("lfs_manufacturer", kwargs={'slug': self.m1.slug})
        self.client.get(url)
        # then visit the product
        url = reverse("lfs_product", kwargs={'slug': self.p1.slug})
        response = self.client.get(url)
        self.assertContains(response, self.m1.name)

        # visit from the category's page - resets manufacturer
        # first go to category page
        url = reverse("lfs_category", kwargs={'slug': self.c1.slug})
        self.client.get(url)
        # then visit the product
        url = reverse("lfs_product", kwargs={'slug': self.p1.slug})
        response = self.client.get(url)
        self.assertContains(response, self.c1.name)


class ManufacturersManageTestCase(TestCase):
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        self.p1 = Product.objects.create(name="Product 1", slug="product-1", price=5, active=True)
        self.p2 = Product.objects.create(name="Product 2", slug="product-2", price=3, active=True)
        self.p3 = Product.objects.create(name="Product 3", slug="product-3", price=1, active=True)

        self.c1 = Category.objects.create(name="Category 1", slug="category-1")
        self.c1.products = [self.p1, self.p2, self.p3]
        self.c1.save()
        self.m1 = Manufacturer.objects.create(name='LFS C.O', slug='lfs-co', short_description='sd',
                                              description='desc', position=1)

        # set up a user with permission to access the manage interface
        self.user, created = User.objects.get_or_create(username='manager', is_superuser=True)
        self.password = 'pass'
        self.user.set_password(self.password)
        self.user.save()

        # login the manager account so we can access the add variant function
        self.client.login(username='manager', password='pass')

    def test_manage_manufacturer(self):
        """ Test if main management view for manufacturer is rendered properly
        """
        url = reverse("lfs_manage_manufacturer", kwargs={'manufacturer_id': self.m1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_manufacturer(self):
        url = reverse("lfs_manufacturer_add_manufacturer")

        manufacturers_count = Manufacturer.objects.count()

        response = self.client.post(url, {'name': 'Django C.O.', 'slug': 'django-co'})
        self.assertEqual(response.status_code, 302)
        new_manufacturers_count = Manufacturer.objects.count()
        self.assertEqual(manufacturers_count + 1, new_manufacturers_count)

    def test_manufacturer_dispatcher(self):
        url = reverse("lfs_manufacturer_dispatcher")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_update_manufacturer(self):
        url = reverse("lfs_manufacturer_update_manufacturer_data", kwargs={'manufacturer_id': self.m1.pk})

        response = self.client.post(url, {'name': 'Django C.O.', 'slug': 'django-co',
                                          'short_description': 'short', 'description': 'description'})
        self.assertEqual(response.status_code, 200)
        updated_man = Manufacturer.objects.get(pk=self.m1.pk)
        self.assertEqual(updated_man.short_description, u'short')
        self.assertEqual(updated_man.description, u'description')

    def test_delete_manufacturer(self):
        url = reverse("lfs_manufacturer_delete_manufacturer", kwargs={'manufacturer_id': self.m1.pk})
        manufacturers_count = Manufacturer.objects.count()
        self.client.post(url)
        new_manufacturers_count = Manufacturer.objects.count()
        self.assertEqual(manufacturers_count - 1, new_manufacturers_count)

    def test_manufacturer_products_tab(self):
        url = reverse("lfs_manufacturer_load_products_tab", kwargs={'manufacturer_id': self.m1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.p1.name, count=1)

        # assign manufacturer and check if it is still shown only once
        self.p1.manufacturer = self.m1
        self.p1.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.p1.name, count=1)

    def test_manage_manufacturer_add_products(self):
        url = reverse("lfs_manage_manufacturer_add_products", kwargs={'manufacturer_id': self.m1.pk})
        response = self.client.post(url, {self.p1.pk: 'on', self.p2.pk: 'on'})
        self.assertEqual(response.status_code, 200)

        self.assertEquals(Product.objects.get(pk=self.p1.pk).manufacturer.pk, self.m1.pk)
        self.assertEquals(Product.objects.get(pk=self.p2.pk).manufacturer.pk, self.m1.pk)
        self.assertEquals(Product.objects.get(pk=self.p3.pk).manufacturer, None)

    def test_manage_manufacturer_remove_products(self):
        self.p1.manufacturer = self.m1
        self.p1.save()
        self.p2.manufacturer = self.m1
        self.p2.save()

        url = reverse("lfs_manage_manufacturer_remove_products", kwargs={'manufacturer_id': self.m1.pk})
        response = self.client.post(url, {self.p2.pk: 'on'})
        self.assertEqual(response.status_code, 200)

        self.assertEquals(Product.objects.get(pk=self.p1.pk).manufacturer.pk, self.m1.pk)
        self.assertEquals(Product.objects.get(pk=self.p2.pk).manufacturer, None)
        self.assertEquals(Product.objects.get(pk=self.p3.pk).manufacturer, None)

    def test_manage_manufacturer_selected_products(self):
        self.p1.manufacturer = self.m1
        self.p1.save()
        self.p2.manufacturer = self.m1
        self.p2.save()

        url = reverse("lfs_manage_manufacturer_selected_products", kwargs={'manufacturer_id': self.m1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.p1.name, count=1)
        self.assertContains(response, self.p2.name, count=1)
        self.assertContains(response, self.p3.name, count=0)
