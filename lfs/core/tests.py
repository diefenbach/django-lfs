import locale

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.file import SessionStore
from django.template import Template
from django.template import Context
from django.test import TestCase

import lfs.core.utils
from lfs.core.models import Shop
from lfs.core.templatetags.lfs_tags import currency
from lfs.order.models import Order
from lfs.tests.utils import RequestFactory

from lfs.cart.tests import *  # NOQA
from lfs.caching.tests import *  # NOQA
from lfs.catalog.tests import *  # NOQA
from lfs.customer_tax.tests import *  # NOQA
from lfs.marketing.tests import *  # NOQA
from lfs.order.tests import *  # NOQA
from lfs.page.tests import *  # NOQA
from lfs.search.tests import *  # NOQA
from lfs.shipping.tests import *  # NOQA
from lfs.voucher.tests import *  # NOQA
from lfs.customer.tests import *  # NOQA
from lfs.checkout.tests import *  # NOQA
from lfs.manage.tests import *  # NOQA
from lfs.gross_price.tests import *  # NOQA
from lfs.net_price.tests import *  # NOQA
# from lfs.core.wmtests import *

try:
    from lfs_order_numbers.tests import *  # NOQA
except ImportError:
    pass

try:
    from lfs_paypal.tests import *  # NOQA
except ImportError:
    pass


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
        from django.conf import settings
        settings.LFS_LOCALE = "unsupported"

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

        template = Template("""{% load lfs_tags %}{% google_analytics_tracking %}""")
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

        template = Template("""{% load lfs_tags %}{% google_analytics_ecommerce %}""")
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
        self.failIf(content.find("_trackPageview") == -1)

    def test_currency(self):
        """
        """
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        self.assertEqual(currency(0.0), '<span class="money">$0.00</span>')
        self.assertEqual(currency(1.0), '<span class="money">$1.00</span>')

        shop = lfs.core.utils.get_default_shop()
        shop.use_international_currency_code = True
        shop.save()

        self.assertEqual(currency(0.0, None, False), '<span class="money">USD 0.00</span>')
        self.assertEqual(currency(1.0, None, False), '<span class="money">USD 1.00</span>')

        self.assertEqual(currency(-1.0, None, False), '<span class="money negative">-USD 1.00</span>')


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
