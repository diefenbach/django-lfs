# python imports
import locale

# Import tests from other packages
from lfs.cart.tests import *
from lfs.catalog.tests import *
from lfs.customer_tax.tests import *
from lfs.marketing.tests import *
from lfs.order.tests import *
from lfs.page.tests import *
from lfs.search.tests import *
from lfs.shipping.tests import *
from lfs.voucher.tests import *
from lfs.customer.tests import *
from lfs.checkout.tests import *
from lfs.payment.tests import *
# from lfs.manage.tests import *
from lfs.gross_price.tests import *
from lfs.net_price.tests import *
# from lfs.core.wmtests import *

try:
    from lfs_order_numbers.tests import *
except ImportError:
    pass


# django imports
from django.contrib.auth.models import User
from django.contrib.sessions.backends.file import SessionStore
from django.core.urlresolvers import reverse
from django.template.loader import get_template_from_string
from django.template import Context
from django.test import TestCase
from django.test.client import Client

# lfs imports
import lfs.core.utils
from lfs.core.models import Country
from lfs.core.models import Shop
from lfs.core.templatetags.lfs_tags import currency
from lfs.order.models import Order
from lfs.tests.utils import RequestFactory


class ShopTestCase(TestCase):
    """Tests the views of the lfs.catalog.
    """
    fixtures = ['lfs_shop.xml']

    def test_shop_defaults(self):
        """Tests the shop values right after creation of an instance
        """
        shop = Shop.objects.get(pk=1)

        self.assertEqual(shop.name, "LFS")
        self.assertEqual(shop.shop_owner, "John Doe")
        self.assertEqual(shop.product_cols, 1)
        self.assertEqual(shop.product_rows, 10)
        self.assertEqual(shop.category_cols, 1)
        self.assertEqual(shop.google_analytics_id, "")
        self.assertEqual(shop.ga_site_tracking, False)
        self.assertEqual(shop.ga_ecommerce_tracking, False)
        self.assertEqual(shop.default_country.name, u"Deutschland")
        self.assertEqual(shop.get_default_country().name, u"Deutschland")
        self.assertEqual(shop.meta_title, u"<name>")
        self.assertEqual(shop.meta_keywords, u"")
        self.assertEqual(shop.meta_description, u"")

    def test_unsupported_locale(self):
        """
        """
        shop = lfs.core.utils.get_default_shop()
        shop.default_locale = "unsupported"
        shop.save()

        self.client.get("/")

    def test_from_email(self):
        """
        """
        shop = lfs.core.utils.get_default_shop()

        shop.from_email = "john@doe.com"
        self.assertEqual(shop.from_email, "john@doe.com")

    def test_get_notification_emails(self):
        """
        """
        shop = lfs.core.utils.get_default_shop()

        shop.notification_emails = "john@doe.com, jane@doe.com, baby@doe.com"

        self.assertEqual(
            shop.get_notification_emails(),
            ["john@doe.com", "jane@doe.com", "baby@doe.com"])

        shop.notification_emails = "john@doe.com\njane@doe.com\nbaby@doe.com"
        self.assertEqual(
            shop.get_notification_emails(),
            ["john@doe.com", "jane@doe.com", "baby@doe.com"])

        shop.notification_emails = "john@doe.com\r\njane@doe.com\r\nbaby@doe.com"
        self.assertEqual(
            shop.get_notification_emails(),
            ["john@doe.com", "jane@doe.com", "baby@doe.com"])

        shop.notification_emails = "john@doe.com\n\rjane@doe.com\n\rbaby@doe.com"
        self.assertEqual(
            shop.get_notification_emails(),
            ["john@doe.com", "jane@doe.com", "baby@doe.com"])

        shop.notification_emails = "john@doe.com,,,,\n\n\n\njane@doe.com"
        self.assertEqual(
            shop.get_notification_emails(),
            ["john@doe.com", "jane@doe.com"])

    def test_get_meta_title(self):
        shop = lfs.core.utils.get_default_shop()
        self.assertEqual("LFS", shop.get_meta_title())

        shop.meta_title = "John Doe"
        shop.save()

        self.assertEqual("John Doe", shop.get_meta_title())

        shop.meta_title = "<name> - John Doe"
        shop.save()

        self.assertEqual("LFS - John Doe", shop.get_meta_title())

        shop.meta_title = "John Doe - <name>"
        shop.save()

        self.assertEqual("John Doe - LFS", shop.get_meta_title())

    def test_get_meta_keywords(self):
        shop = lfs.core.utils.get_default_shop()
        self.assertEqual("", shop.get_meta_keywords())

        shop.meta_keywords = "John Doe"
        shop.save()

        self.assertEqual("John Doe", shop.get_meta_keywords())

        shop.meta_keywords = "<name> - John Doe"
        shop.save()

        self.assertEqual("LFS - John Doe", shop.get_meta_keywords())

        shop.meta_keywords = "<name> - John Doe"
        shop.save()

        self.assertEqual("LFS - John Doe", shop.get_meta_keywords())

        shop.meta_keywords = "<name> - John Doe - <name>"
        shop.save()

        self.assertEqual("LFS - John Doe - LFS", shop.get_meta_keywords())

    def test_get_meta_description(self):
        shop = lfs.core.utils.get_default_shop()
        self.assertEqual("", shop.get_meta_description())

        shop.meta_description = "John Doe"
        shop.save()

        self.assertEqual("John Doe", shop.get_meta_description())

        shop.meta_description = "<name> - John Doe"
        shop.save()

        self.assertEqual("LFS - John Doe", shop.get_meta_description())

        shop.meta_description = "<name> - John Doe"
        shop.save()

        self.assertEqual("LFS - John Doe", shop.get_meta_description())

        shop.meta_description = "<name> - John Doe - <name>"
        shop.save()

        self.assertEqual("LFS - John Doe - LFS", shop.get_meta_description())


class TagsTestCase(TestCase):
    """
    """
    fixtures = ['lfs_shop.xml']

    def test_ga_site_tracking(self):
        """
        """
        shop = Shop.objects.get(pk=1)
        shop.google_analytics_id = ""
        shop.ga_site_tracking = False
        shop.ga_ecommerce_tracking = False
        shop.save()

        template = get_template_from_string(
            """{% load lfs_tags %}{% google_analytics_tracking %}""")

        content = template.render(Context())
        self.failIf(content.find("pageTracker") != -1)

        # Enter a google_analytics_id
        shop.google_analytics_id = "UA-XXXXXXXXXX"
        shop.save()

        # But this is not enough
        content = template.render(Context())
        self.failIf(content.find("pageTracker") != -1)

        # It has to be activated first
        shop.ga_site_tracking = True
        shop.save()

        # Now it works and "pageTracker" is found
        content = template.render(Context())
        self.failIf(content.find("pageTracker") == -1)

    def test_ga_ecommerce_tracking(self):
        """
        """
        shop = lfs.core.utils.get_default_shop()
        shop.google_analytics_id = ""
        shop.ga_site_tracking = False
        shop.ga_ecommerce_tracking = False
        shop.save()

        session = SessionStore()

        rf = RequestFactory()
        request = rf.get('/')
        request.session = session

        template = get_template_from_string(
            """{% load lfs_tags %}{% google_analytics_ecommerce %}""")

        content = template.render(Context({"request": request}))
        self.failIf(content.find("pageTracker") != -1)

        # Enter a google_analytics_id
        shop.google_analytics_id = "UA-XXXXXXXXXX"
        shop.save()

        # Simulating a new request
        rf = RequestFactory()
        request = rf.get('/')
        request.session = session

        # But this is not enough
        content = template.render(Context({"request": request}))
        self.failIf(content.find("pageTracker") != -1)

        # It has to be activated first
        shop.ga_ecommerce_tracking = True
        shop.save()

        # Simulating a new request
        rf = RequestFactory()
        request = rf.get('/')
        request.session = session

        # But this is still not enough
        content = template.render(Context({"request": request}))
        self.failIf(content.find("pageTracker") != -1)

        # There has to be an order within the session
        session["order"] = Order()

        # Now it works and "pageTracker" is found
        content = template.render(Context({"request": request}))
        self.failIf(content.find("pageTracker") == -1)

    def test_currency(self):
        """
        """
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        self.assertEqual(currency(0.0), "$0.00")
        self.assertEqual(currency(1.0), "$1.00")

        shop = lfs.core.utils.get_default_shop()
        shop.use_international_currency_code = True
        shop.save()

        self.assertEqual(currency(0.0, None, False), "USD 0.00")
        self.assertEqual(currency(1.0, None, False), "USD 1.00")


class ManageURLsTestCase(TestCase):
    def test_manage_urls_anonymous(self):
        """Tests that all manage urls cannot accessed by anonymous user.
        """
        rf = RequestFactory()
        request = rf.get("/")
        request.user = AnonymousUser()

        from lfs.manage.urls import urlpatterns
        for url in urlpatterns:
            result = url.callback(request)
            self.failUnless(result["Location"].startswith("/login/?next=/"))
