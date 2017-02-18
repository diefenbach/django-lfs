# coding: utf-8

from django.http import Http404
from django.test import TestCase
from lfs.caching.utils import lfs_get_object, lfs_get_object_or_404
from lfs.catalog.models import Product


class CachingTestCase(TestCase):
    fixtures = ['lfs_shop.xml', "lfs_user.xml"]

    def test_lfs_get_object(self):
        self.assertTrue(lfs_get_object(Product, slug=u'zażółćgęśląjaźń') is None)

    def test_lfs_get_object_or_404(self):
        self.assertRaises(Http404, lfs_get_object_or_404, Product, slug=u'zażółćgęśląjaźń')
