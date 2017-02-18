from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase

from lfs.page.models import Page
from lfs.tests.utils import DummyRequest


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

        self.root = Page.objects.create(
            id=1,
            title="Root",
            slug="",
            exclude_from_navigation=False,
        )

        self.page = Page.objects.create(
            id=2,
            title="Page Title",
            slug="page-title",
            body="<p>This is a body</p>",
            short_text="This is a short text"
        )

    def test_add_page(self):
        """Tests to add a page.
        """
        self.assertEqual(self.page.id, 2)
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

    def test_get_meta_title(self):
        self.assertEqual("Page Title", self.page.get_meta_title())

        self.page.meta_title = "John Doe"
        self.page.save()

        self.assertEqual("John Doe", self.page.get_meta_title())

        self.page.meta_title = "<title> - John Doe"
        self.page.save()

        self.assertEqual("Page Title - John Doe", self.page.get_meta_title())

        self.page.meta_title = "John Doe - <title>"
        self.page.save()

        self.assertEqual("John Doe - Page Title", self.page.get_meta_title())

    def test_get_meta_keywords(self):
        self.assertEqual("", self.page.get_meta_keywords())

        self.page.meta_keywords = "John Doe"
        self.page.save()

        self.assertEqual("John Doe", self.page.get_meta_keywords())

        self.page.meta_keywords = "<title> - John Doe"
        self.page.save()

        self.assertEqual("Page Title - John Doe", self.page.get_meta_keywords())

        self.page.meta_keywords = "<short-text> - John Doe"
        self.page.save()

        self.assertEqual("This is a short text - John Doe", self.page.get_meta_keywords())

        self.page.meta_keywords = "<short-text> - John Doe - <title>"
        self.page.save()

        self.assertEqual("This is a short text - John Doe - Page Title", self.page.get_meta_keywords())

    def test_get_meta_description(self):
        self.assertEqual("", self.page.get_meta_description())

        self.page.meta_description = "John Doe"
        self.page.save()

        self.assertEqual("John Doe", self.page.get_meta_description())

        self.page.meta_description = "<title> - John Doe"
        self.page.save()

        self.assertEqual("Page Title - John Doe", self.page.get_meta_description())

        self.page.meta_description = "<short-text> - John Doe"
        self.page.save()

        self.assertEqual("This is a short text - John Doe", self.page.get_meta_description())

        self.page.meta_description = "<short-text> - John Doe - <title>"
        self.page.save()

        self.assertEqual("This is a short text - John Doe - Page Title", self.page.get_meta_description())

    def test_add_page_with_existing_slug(self):
        next_id = Page.objects.count() + 1
        Page.objects.create(id=next_id, title="Test1", slug="test")
        self.assertRaises(IntegrityError, Page.objects.create, id=next_id + 1, title="Test2", slug="test")
