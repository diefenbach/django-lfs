# django imports
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

# test imports
from lfs.tests.utils import DummyRequest

# lfs imports
from lfs.page.models import Page


class PageTestCase(TestCase):
    """Unit tests for lfs.page
    """
    fixtures = ['lfs_shop.xml', "lfs_user.xml"]

    def setUp(self):
        """
        """
        self.client.login(username="admin", password="admin")

        self.user = User.objects.get(username="admin")
        self.request = DummyRequest(user=self.user)

        self.page = Page.objects.create(
            title="Page Title",
            slug="page-title",
            body="<p>This is a body</p>"
        )

    def test_add_page(self):
        """Tests to add a page.
        """
        self.assertEqual(self.page.title, "Page Title")
        self.assertEqual(self.page.slug, "page-title")
        self.assertEqual(self.page.body, "<p>This is a body</p>")
        self.assertEqual(self.page.active, False)
        self.assertEqual(self.page.position, 999)

    def test_page_view_1(self):
        """Tests page view as superuser.
        """
        url = reverse("lfs_page_view", kwargs={"slug": self.page.slug})
        response = self.client.get(url)
        self.failIf(response.content.find("Page Title") == -1)
        self.failIf(response.content.find("<p>This is a body</p>") == -1)

    def test_page_view_2(self):
        """Tests page view as anonymous.
        """
        self.client.logout()

        url = reverse("lfs_page_view", kwargs={"slug": self.page.slug})
        response = self.client.get(url)

        self.failIf(response.content.find("We are sorry") == -1)

        self.page.active = True
        self.page.save()

        response = self.client.get(url)
        self.failIf(response.content.find("Page Title") == -1)
        self.failIf(response.content.find("<p>This is a body</p>") == -1)

    def test_active_pages(self):
        """Tests the ActiveManager for pages.
        """
        pages = Page.objects.active()
        self.assertEqual(len(pages), 0)

        self.page.active = True
        self.page.save()

        pages = Page.objects.active()
        self.assertEqual(len(pages), 1)
